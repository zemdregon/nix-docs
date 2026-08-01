---
status: complete
last-checked: 2026-08
---

# Docker and Podman

## Overview

NixOS can run upstream **OCI container engines** on the host: the Docker daemon (`virtualisation.docker`) or Podman (`virtualisation.podman`). Both pull and run images from registries, expose published ports, and work with compose-style workflows—without baking service config into the host `configuration.nix` the way [declarative containers](declarative-containers.md) do.

This page covers **host runtimes** (daemon or socket, groups, firewall, GPU hooks, systemd integration). Building images from Nix closures is separate: see [Containers (OCI)](../../11-development/containers-oci.md).

## Details

### Docker (`virtualisation.docker`)

`virtualisation.docker.enable = true` starts **dockerd** as a systemd service and installs the `docker` CLI. Socket activation is always on (`docker.socket`); `enableOnBoot` (default `true`) controls whether `dockerd` itself starts at boot—needed for containers created with `--restart=always`.

The module creates the **`docker` group**; users in that group can talk to `/run/docker.sock` and effectively gain root on the host—same trust model as upstream Docker.

| Option | Role |
|--------|------|
| `daemon.settings` | Serialized to `daemon.json` (freeform JSON attrs; merges with module defaults for `group`, `hosts`, `log-driver`, `storage-driver`) |
| `logDriver` | Top-level enum defaulting to `journald`; written into `daemon.settings` as `log-driver` |
| `storageDriver` | Optional explicit storage driver (`overlay2`, `zfs`, …); changing it makes existing images inaccessible |
| `enableOnBoot` | Start `dockerd` at boot vs on-demand via socket activation |
| `autoPrune` | Optional systemd timer for `docker system prune` |

Common `daemon.settings` keys include `live-restore`, IPv6 CIDRs, and runtime overrides. Prefer `daemon.settings` for anything that belongs in upstream `daemon.json`; use `extraOptions` only for flags not covered by the module.

Do **not** enable Docker and Podman’s Docker-compat socket at the same time—the modules **assert** they conflict (see [Failure modes](#failure-modes)).

### Podman (`virtualisation.podman`)

`virtualisation.podman.enable = true` installs Podman and shared `/etc/containers` config (`virtualisation.containers.enable` is turned on). Podman is **daemonless** and fits **rootless** workflows (`podman` as an unprivileged user) better than a root-owned Docker socket.

| Option | Role |
|--------|------|
| `dockerCompat` | Adds a `docker` → `podman` alias (CLI compatibility; **asserts** against `virtualisation.docker.enable`) |
| `dockerSocket.enable` | Symlinks Podman’s API socket to `/run/docker.sock` so `docker-compose` and other Docker-API clients can target Podman (**asserts** against Docker) |
| `defaultNetwork.settings` | Tweaks the default bridge network; set `dns_enabled = true` when compose stacks need DNS between containers on the default network |
| `autoPrune` | Optional timer for `podman system prune` |

Members of the **`podman` group** can use the rootful socket; treat that group like `docker` for privilege. Rootless Podman uses per-user sockets under `$XDG_RUNTIME_DIR` and needs `subUidRanges` / `subGidRanges` on the user (see [Examples](#examples)).

When `networking.nftables.enable` is set, the Podman module can set `firewall_driver = "nftables"` in `containersConf`.

### Choosing an approach

| Approach | Isolation | Declarative in Nix? | Typical fit |
|----------|-----------|---------------------|-------------|
| **Docker on host** | Shared kernel; `docker` group ≈ root | Imperative (`docker run`, compose files) | Third-party compose stacks, tools expecting Docker API, teams already on Docker |
| **Podman on host** | Shared kernel; rootful socket ≈ root; rootless reduces blast radius | Imperative; rootless fits user-level compose | Daemonless hosts, rootless by default, Docker-API compat via `dockerSocket` |
| **[Declarative containers](declarative-containers.md)** | systemd-nspawn guest; shared store; incomplete vs host root | `containers.<name>` in `configuration.nix` | Nested NixOS services versioned with the host pin and rollback |
| **`virtualisation.oci-containers`** | Same engine as chosen backend (`docker` or `podman`) | Per-container attrs → systemd units | Compose-like images/ports/env declared in Nix without full `containers.*` guests |
| **[MicroVMs](microvms.md)** | Separate kernel (QEMU, Firecracker, …) | Flake/module guest definitions | Untrusted or strongly isolated workloads, non-NixOS guests |

Host engines are a poor default for production state you would rather declare in Nix; they shine for **porting existing compose files** or tooling that expects a Docker API. When you want OCI images but systemd-managed lifecycle in Nix, `virtualisation.oci-containers` is the usual bridge (not a separate `services.oci-containers` tree—the option lives under `virtualisation`).

### Firewall and networking

Docker adjusts **iptables/nftables** and forwarding sysctl (`net.ipv4.conf.*.forwarding`) for bridge networking. Published ports are implemented in NAT/FORWARD chains, which can **bypass** the NixOS stateful firewall’s INPUT rules—ports may be reachable from outside even when `networking.firewall` has no matching allow ([nixpkgs#111852](https://github.com/NixOS/nixpkgs/issues/111852)). Mitigations people use in practice:

- Bind publishes to localhost: `"127.0.0.1:8080:8080"` instead of `"8080:8080"`.
- Restrict at the Docker chain (`DOCKER-USER`) or NAT layer via `networking.firewall.extraCommands` (advanced; backend-specific).
- Prefer the **Podman** backend for `oci-containers` when you need tighter integration with NixOS firewall rules (still verify port bindings—Podman portmap uses NAT as well).

Podman’s module opens UDP 53 on the bridge interface when `defaultNetwork.settings.dns_enabled` is true and the firewall backend is not `firewalld`. For host firewall patterns, see [Networking](../configuration/networking.md).

### Failure modes

| Symptom | Likely cause | What to check |
|---------|--------------|---------------|
| `nixos-rebuild` fails with Docker/Podman conflict | Both `virtualisation.docker.enable` and `virtualisation.podman.dockerCompat` or `dockerSocket.enable` | Enable **one** API surface: real Docker **or** Podman compat, not both |
| Service reachable from WAN despite closed firewall | Docker/Podman published ports bypass INPUT rules | [nixpkgs#111852](https://github.com/NixOS/nixpkgs/issues/111852); bind `127.0.0.1:…`, reverse proxy, or explicit filter rules |
| Rootless Podman: “cannot find UID/GID maps” | Missing `subUidRanges` / `subGidRanges` | Set on `users.users.<name>` (non-overlapping ranges per user) |
| Rootless container does not start at boot | No user session / linger off | `users.users.<name>.linger = true` for boot-time rootless units; `oci-containers` warns when rootless + no linger |
| Rootless `oci-containers` + healthcheck stuck | `podman.sdnotify = "healthy"` needs static `uid` and user session | Set `users.users.<name>.uid`; ensure linger; see module assertions for `sdnotify` |
| Secrets in compose committed to Nix | Passwords in `configuration.nix` or compose inlined in the store | Use `environmentFiles`, bind mounts from `/run/secrets`, agenix/sops-nix—never inline secrets in the store |
| GPU in container fails | Toolkit or driver not enabled | `hardware.nvidia-container-toolkit.enable`; host driver stack separate from nixpkgs CUDA libs |

Disabling Docker’s iptables integration (`daemon.settings` / `extraOptions`) is sometimes suggested online; it can break container DNS and outbound traffic—treat it as a last resort after reading upstream networking docs.

### GPU access in containers

GPU workloads need the host **driver** plus container runtime integration. On NixOS, `hardware.nvidia-container-toolkit.enable = true` generates CDI config for Docker/Podman (`--device=nvidia.com/gpu=…`). That is runtime wiring, not a substitute for `cudaPackages` or driver options in your build config—see [CUDA, ROCm, and ML stacks](../../11-development/cuda-rocm-ml.md) and the [Nixpkgs CUDA + containers section](https://nixos.org/manual/nixpkgs/unstable/#cuda-docker-podman). Deprecated `virtualisation.docker.enableNvidia` / `virtualisation.podman.enableNvidia` should be replaced by the toolkit option.

### Secrets and compose files

Do not commit database passwords, API keys, or TLS material in `docker-compose.yml` checked into the repo—they leak the same way in git. Values inlined in `configuration.nix` end up in the **world-readable Nix store**. Use **`env_file`** / `environmentFiles`, bind-mounted paths populated at deploy time (agenix, sops-nix, or `/run/secrets/…`), and keep only non-secret structure in version control. For declarative OCI units, `virtualisation.oci-containers.containers.<name>.environmentFiles` accepts store-external paths.

### `virtualisation.oci-containers` (declarative OCI units)

The `virtualisation.oci-containers` module (successor to the removed `docker-containers` option) defines containers as **systemd services** generated from Nix attrs: `image`, `ports`, `volumes`, `environment`, `dependsOn`, `autoStart`, and backend-specific `podman` settings. `backend` is `"podman"` (default on recent `stateVersion`) or `"docker"`; enabling containers with a non-empty `containers` set pulls in the matching runtime module.

This is the usual NixOS bridge between imperative compose and fully declarative NixOS guests: you keep upstream images and port/volume shapes, but activation goes through `nixos-rebuild` and `systemctl`. It does **not** replace [declarative containers](declarative-containers.md) when you need a nested NixOS `config` module inside the guest.

### Systemd integration and compose at boot

There is no single built-in “import this `docker-compose.yml`” option in the NixOS module tree. Common patterns:

| Pattern | How it runs at boot |
|---------|---------------------|
| **`virtualisation.oci-containers`** | One systemd unit per container; `autoStart = true` (default) adds `wantedBy = [ "multi-user.target" ]` |
| **Custom systemd unit** | `systemd.services.<name>` runs `docker compose up` / `podman-compose up` in `WorkingDirectory`; use `After=` / `Requires=` for ordering |
| **User systemd + linger** | Rootless compose as `systemd --user` services; requires `users.users.<name>.linger = true` for boot without login |
| **Manual / on-demand** | `autoStart = false` on `oci-containers` entries; start with `systemctl start <serviceName>` |

`oci-containers` sets `Restart = on-failure` and uses `podman run --rm` / Docker equivalents with pre-start image pull/load. Compose-specific features (profiles, extends, multiple files) still belong in compose tooling or hand-written units unless you translate them into per-container attrs.

## Examples

Docker on a server with journald logging via `daemon.settings` (add trusted users to `docker`):

```nix
{
  virtualisation.docker = {
    enable = true;
    enableOnBoot = true;
    daemon.settings = {
      "log-driver" = "journald";
      "log-opts" = {
        tag = "{{.Name}}";
      };
    };
  };
  users.users.alice.extraGroups = [ "docker" ];
}
```

Podman as a Docker-API drop-in for compose tooling:

```nix
{
  virtualisation.podman = {
    enable = true;
    dockerCompat = true;
    dockerSocket.enable = true;
    defaultNetwork.settings.dns_enabled = true;
  };
  users.users.alice.extraGroups = [ "podman" ];
}
```

Rootless Podman for a normal login user (subids + optional socket via user session):

```nix
{
  virtualisation.podman.enable = true;

  users.users.alice = {
    isNormalUser = true;
    linger = true;
    subUidRanges = [{ startUid = 100000; count = 65536; }];
    subGidRanges = [{ startGid = 100000; count = 65536; }];
  };
}
```

After login, rootless clients often use `unix://$XDG_RUNTIME_DIR/podman/podman.sock` (set `DOCKER_HOST` in the user environment if compose expects it).

Declarative single container via `oci-containers` (Podman backend):

```nix
{
  virtualisation.oci-containers = {
    backend = "podman";
    containers.hello = {
      image = "docker.io/library/nginx";
      ports = [ "127.0.0.1:8080:80" ];
      autoStart = true;
    };
  };
}
```

After `nixos-rebuild switch`, verify with `podman ps` or `systemctl status podman-hello`; reconcile firewall and bind addresses if published ports are unexpectedly reachable.

## Boundaries

**In scope for this page:** enabling Docker or Podman on a NixOS host, group/socket security, firewall interactions, GPU toolkit wiring, secrets hygiene for compose, `oci-containers` as a systemd-backed declarative pattern, and choosing among host engines vs nspawn guests vs microVMs.

**Out of scope:** writing Dockerfiles or `dockerTools` image builds ([Containers (OCI)](../../11-development/containers-oci.md)); full `containers.<name>` nested NixOS modules ([declarative containers](declarative-containers.md)); Kubernetes/k3s; third-party compose generators; and upstream engine release notes beyond NixOS module options.

**Not provided by NixOS modules:** automatic translation from arbitrary `docker-compose.yml` files to Nix—expect manual mapping, custom systemd units, or external tooling.

## References

- [NixOS options — `virtualisation.docker`](https://search.nixos.org/options?query=virtualisation.docker)
- [NixOS options — `virtualisation.podman`](https://search.nixos.org/options?query=virtualisation.podman)
- [NixOS options — `virtualisation.oci-containers`](https://search.nixos.org/options?query=virtualisation.oci-containers)
- [NixOS options — `hardware.nvidia-container-toolkit`](https://search.nixos.org/options?query=hardware.nvidia-container-toolkit)
- [nixpkgs#111852 — Docker vs NixOS firewall interaction](https://github.com/NixOS/nixpkgs/issues/111852)

## See also

- [Declarative containers](declarative-containers.md) — `containers.<name>` NixOS guests on the host
- [Containers and nspawn](containers-and-nspawn.md) — imperative `nixos-container` lifecycle
- [Networking](../configuration/networking.md) — `networking.firewall` and backend choice
- [Containers (OCI)](../../11-development/containers-oci.md) — building images with `dockerTools` / nix2container
- [CUDA, ROCm, and ML stacks](../../11-development/cuda-rocm-ml.md) — drivers, `cudaPackages`, and container GPU access
- [MicroVMs](microvms.md) — kernel-isolated NixOS guests
