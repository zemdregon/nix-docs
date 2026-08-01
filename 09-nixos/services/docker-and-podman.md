---
status: draft
---

# Docker and Podman

## Overview

NixOS can run upstream **OCI container engines** on the host: the Docker daemon (`virtualisation.docker`) or Podman (`virtualisation.podman`). Both pull and run images from registries, expose published ports, and work with compose-style workflows—without baking service config into the host `configuration.nix` the way [declarative containers](declarative-containers.md) do.

This page covers **host runtimes** (daemon or socket, groups, firewall, GPU hooks). Building images from Nix closures is separate: see [Containers (OCI)](../../11-development/containers-oci.md).

## Details

### Docker (`virtualisation.docker`)

`virtualisation.docker.enable = true` starts **dockerd** as a systemd service and installs the `docker` CLI. The module creates the **`docker` group**; users in that group can talk to `/run/docker.sock` and effectively gain root on the host—same trust model as upstream Docker.

Common knobs: `daemon.settings` (serialized to `daemon.json`), `storageDriver`, `logDriver` (defaults to `journald`), `autoPrune`, and `enableOnBoot`. Socket activation is always used; `enableOnBoot` controls whether the daemon starts at boot (needed for containers with `--restart=always`).

Do **not** enable Docker and Podman’s Docker-compat socket at the same time—the modules assert they conflict.

### Podman (`virtualisation.podman`)

`virtualisation.podman.enable = true` installs Podman and shared `/etc/containers` config (`virtualisation.containers.enable` is turned on). Podman is **daemonless** and fits **rootless** workflows (`podman` as an unprivileged user) better than a root-owned Docker socket.

| Option | Role |
|--------|------|
| `dockerCompat` | Adds a `docker` → `podman` alias (CLI compatibility; conflicts with `virtualisation.docker.enable`) |
| `dockerSocket.enable` | Symlinks Podman’s API socket to `/run/docker.sock` so `docker-compose` and other Docker-API clients can target Podman (also conflicts with Docker) |
| `defaultNetwork.settings` | Tweaks the default bridge network; set `dns_enabled = true` when compose stacks need DNS between containers on the default network |

Members of the **`podman` group** can use the rootful socket; treat that group like `docker` for privilege.

### Firewall and networking

Docker adjusts **iptables/nftables** and forwarding sysctl for bridge networking. That can interact badly with the NixOS **stateful firewall**—ports may appear open or closed unexpectedly after container activity ([nixpkgs#111852](https://github.com/NixOS/nixpkgs/issues/111852)). Podman’s module can integrate with nftables when `networking.nftables.enable` is set. For host firewall patterns and this footgun, see [Networking](../configuration/networking.md).

Published container ports still need to match what you intend to expose; do not assume `networking.firewall` and Docker’s rules stay in sync without checking after upgrades.

### When to use host engines vs other isolation

| Approach | Fits when |
|----------|-----------|
| **Docker / Podman on the host** | You run upstream images or `docker-compose` stacks imperatively; quick adoption of third-party recipes; dev machines |
| **[Declarative containers](declarative-containers.md)** | The workload should be a **NixOS module** versioned with the host—same pin, rollback, and `nixos-rebuild` story |
| **[Containers and nspawn](containers-and-nspawn.md)** | Imperative NixOS guests sharing the host store |
| **[MicroVMs](microvms.md)** | Stronger isolation, separate kernel, or non-NixOS guests |

Host engines are a poor default for production state you would rather declare in Nix; they shine for **porting existing compose files** or tooling that expects a Docker API.

### GPU access in containers

GPU workloads need the host **driver** plus container runtime integration. On NixOS, `hardware.nvidia-container-toolkit.enable = true` generates CDI config for Docker/Podman (`--device=nvidia.com/gpu=…`). That is runtime wiring, not a substitute for `cudaPackages` or driver options in your build config—see [CUDA, ROCm, and ML stacks](../../11-development/cuda-rocm-ml.md) and the [Nixpkgs CUDA + containers section](https://nixos.org/manual/nixpkgs/unstable/#cuda-docker-podman). Deprecated `virtualisation.docker.enableNvidia` / `virtualisation.podman.enableNvidia` should be replaced by the toolkit option.

### Secrets and compose files

Do not commit database passwords, API keys, or TLS material in `docker-compose.yml` checked into the repo—they end up in the world-readable Nix store if inlined in `configuration.nix`, and plain compose files in git leak the same way. Use **`env_file`** or bind-mounted paths populated at deploy time (agenix, sops-nix, `environmentFiles`, or `/run/secrets/…`), and keep only non-secret structure in version control.

## Examples

Minimal Docker on a server (add trusted users to `docker`):

```nix
{
  virtualisation.docker.enable = true;
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

After `nixos-rebuild switch`, verify with `docker ps` (or `podman ps`) and exercise your compose stack; reconcile firewall holes if published ports are unreachable.

## References

- [NixOS options — `virtualisation.docker`](https://search.nixos.org/options?query=virtualisation.docker)
- [NixOS options — `virtualisation.podman`](https://search.nixos.org/options?query=virtualisation.podman)
- [nixpkgs#111852 — Docker vs NixOS firewall interaction](https://github.com/NixOS/nixpkgs/issues/111852)

## See also

- [Declarative containers](declarative-containers.md) — `containers.<name>` NixOS guests on the host
- [Containers and nspawn](containers-and-nspawn.md) — imperative `nixos-container` lifecycle
- [Networking](../configuration/networking.md) — `networking.firewall` and backend choice
- [Containers (OCI)](../../11-development/containers-oci.md) — building images with `dockerTools` / nix2container
- [CUDA, ROCm, and ML stacks](../../11-development/cuda-rocm-ml.md) — drivers, `cudaPackages`, and container GPU access
