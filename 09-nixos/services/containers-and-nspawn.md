---
status: complete
---

# Containers and nspawn

## Overview

NixOS can run other NixOS instances as lightweight containers that share the host’s Nix store. Creation is cheap because store paths are reused rather than copied into each container root.

Isolation is incomplete: a process with root inside the container can affect the host. Do not give container root to untrusted users.

There are two management styles:

- **Imperative** — the `nixos-container` CLI (this page).
- **Declarative** — `containers.*` in the host `configuration.nix` (see [declarative containers](declarative-containers.md)).

The Container Management chapter documents these as NixOS containers driven by systemd units (`container@name.service`). Under the hood they use **systemd-nspawn**; this page follows the manual’s framing (containers + units) rather than a general nspawn tutorial.

## Details

### Prerequisites

- Set `boot.enableContainers = true` on the host.
- Container management with `nixos-container` is root-only.

### Imperative lifecycle

| Command | Role |
|---------|------|
| `nixos-container create <name>` | Create rootfs, conf, and initial system profile |
| `nixos-container start` / `stop` | Boot or halt (waits until `multi-user.target` on start) |
| `nixos-container destroy` | Remove the container and its filesystem |
| `nixos-container update` | Rebuild and activate the container config |
| `nixos-container login` | Login prompt (any host user) |
| `nixos-container root-login` | Unauthenticated root shell (host root only) |
| `nixos-container run` | Run a command inside the container |
| `nixos-container show-ip` | Print the container’s IPv4 address |

On create, NixOS lays down:

- Root directory: `/var/lib/nixos-containers/<name>`
- Host conf: `/etc/nixos-containers/<name>.conf`
- System profile: `/nix/var/nix/profiles/per-container/<name>/system`

The running container is a systemd unit: `container@<name>.service`. Use `systemctl status container@foo` for diagnostics; start/stop also work via `systemctl`.

### Networking (imperative defaults)

By default the next free address in `10.233.0.0/16` is assigned. Override with `--host-address` and `--local-address` on create. `nixos-container show-ip` reports the container address.

### Updating configuration

- Edit `/var/lib/nixos-containers/<name>/etc/nixos/configuration.nix` on the host, then `nixos-container update <name>`.
- Or pass a new config on the CLI: `nixos-container update <name> --config '…'` — this **overwrites** the container’s `configuration.nix`.
- From inside the container you can run `nixos-rebuild switch` (see [rebuild / switch / boot / test](../operations/rebuild-switch-boot-test.md)). The container may lack a NixOS channel copy; run `nix-channel --update` first if needed.

Declarative containers upgrade with the host on `nixos-rebuild`; imperative ones are updated independently — often preferable when you do not want host rebuilds to force container rebuilds.

### Relation to declarative containers

`containers.<name>` in the host config builds and can update containers in place on switch. Removing a declarative entry does not delete `/var/lib/nixos-containers/<name>`; use `nixos-container destroy` for that. Deep dive: [declarative containers](declarative-containers.md). For how units fit the host activation model, see [systemd integration](../architecture/systemd-integration.md) and [service patterns](service-patterns.md).

## Examples

Create, start, and get a root shell (as host root):

```bash
# boot.enableContainers = true must already be active on the host
nixos-container create demo
nixos-container start demo
systemctl status container@demo
nixos-container show-ip demo
nixos-container root-login demo
```

Create with an inline config and explicit addresses:

```bash
nixos-container create web \
  --local-address 10.235.1.2 \
  --host-address 10.235.1.1 \
  --config '
    services.httpd.enable = true;
    services.httpd.adminAddr = "admin@example.org";
    networking.firewall.allowedTCPPorts = [ 80 ];
  '
nixos-container start web
curl "http://$(nixos-container show-ip web)/"
```

Rebuild after editing the container’s `configuration.nix` on the host:

```bash
nixos-container update demo
# or overwrite configuration.nix entirely:
# nixos-container update demo --config 'networking.hostName = "demo";'
```

Stop and destroy:

```bash
nixos-container stop demo
nixos-container destroy demo
```

## See also

- [Declarative containers](declarative-containers.md)
- [Service patterns](service-patterns.md)
- [systemd integration](../architecture/systemd-integration.md)
- [rebuild / switch / boot / test](../operations/rebuild-switch-boot-test.md)

## References

- [NixOS Manual — Container Management](https://nixos.org/manual/nixos/stable/index.html#ch-containers) — imperative `nixos-container`, declarative `containers.*`, shared store / incomplete isolation (stable / 26.05 as of 2026-07)
