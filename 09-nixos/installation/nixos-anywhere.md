---
status: complete
last-checked: 2026-08
---

# nixos-anywhere

## Overview

[nixos-anywhere](https://github.com/nix-community/nixos-anywhere) (nix-community) installs NixOS on a remote machine over SSH. It SSHs to the target, optionally kexecs into a NixOS installer, partitions with [disko](../../12-deployment-and-infra/disko.md), installs your flake’s `nixosConfigurations.<name>`, and can reboot into the new system.

It complements local [manual](manual-install.md) and [graphical](graphical-installer.md) installs when the machine is already reachable on the network. After install, ongoing remote updates use `nixos-rebuild --target-host` or deploy tools—not nixos-anywhere itself (see [remote deploy](../operations/remote-deploy.md)).

## Details

**When to use / when not.**

| Situation | Prefer |
|-----------|--------|
| Bare metal or VPS already SSH-reachable; you want a flake + disko wipe-and-install | **nixos-anywhere** |
| No network yet, need Wi‑Fi during install, or no SSH into a live OS/installer | [Manual](manual-install.md) / [graphical](graphical-installer.md) ISO (or [netboot](netboot-and-pxe.md)) |
| Machine already runs NixOS; only config/package changes | [Remote deploy](../operations/remote-deploy.md) (`nixos-rebuild --target-host`, deploy-rs, colmena, …)—**not** nixos-anywhere |
| Repair without reformatting | Upstream “repair” howto / selective `--phases`—not a full default run |

**Flow (default phases).** With `--phases` unset, nixos-anywhere runs `kexec`, `disko`, `install`, `reboot`:

1. **kexec** — If the target is not already a NixOS installer, load a kexec tarball and boot into one.
2. **disko** — Unmount/destroy target filesystems as configured, then create and mount per the disko disk config.
3. **install** — Copy and activate the NixOS system from the flake (or `--store-paths`).
4. **reboot** — Unmount, export ZFS pools if any, reboot into the installed system.

Skip or reorder phases with `--phases` (comma-separated). Default disko mode (`--disko-mode disko`) destroys filesystems on disks it will format before creating and mounting—treat a full run as a wipe.

**What you need.**

- **Source:** Linux, macOS, NixOS, or WSL2 with Nix; flakes + `nix-command` so `nix run` / `nix flake` work. You do not install nixos-anywhere locally.
- A flake with a `nixosConfigurations.<name>` that includes a [disko](../../12-deployment-and-infra/disko.md) disk layout (see also [partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)).
- Target reachable over SSH (root, or a user with passwordless sudo). Keys or password auth; temporary install keys are created unless you pass `-i`.
- Destination: **x86_64 or aarch64** Linux with kexec support for the default path. Other arches need a custom image via `--kexec`. The default bundled kexec image is **x86_64-only**—use `--kexec` for aarch64 or custom networking.
- At least **1.5 GB RAM** (excluding swap) when using kexec.
- Wired/public/local network reachability. The tool does not support Wi‑Fi for its networking assumptions; use a custom `--kexec` installer if you need VPN or similar.

**Useful flags.**

| Flag | Role |
|------|------|
| `--flake` / `-f` `<path>#<name>` | Flake URI and `nixosConfigurations` name |
| `--target-host user@host` | SSH target |
| `--build-on auto\|local\|remote` | Where to build the closure (default `auto`) |
| `--kexec <path>` | Custom kexec tarball (non‑x86_64, VPN, etc.) |
| `--phases …` | Subset/order of `kexec,disko,install,reboot` |
| `--store-paths` / `-s` `<disko> <system>` | Use store paths instead of a flake |
| `--vm-test` | Test config + disko in a VM without installing |
| `--generate-hardware-config nixos-facter\|nixos-generate-config <path>` | Emit `facter.json` or `hardware-configuration.nix` during install |
| `--no-disko-deps` | Upload only the disko script (less RAM on tight targets) |
| `--env-password` | Use `SSHPASS` for `ssh-copy-id` password auth |

**Failure modes.**

| Symptom / risk | Likely cause | What to check |
|----------------|--------------|---------------|
| SSH login / `ssh-copy-id` fails | Wrong user/key; non-root without passwordless sudo; password auth without `SSHPASS` + `--env-password` | Reach the host manually; use `-i` or set `SSHPASS` |
| `Failure unpacking initrd` / kexec dies | Under 1.5 GB free RAM (excluding swap) | Add RAM, or skip kexec if already in a NixOS installer; see `--no-disko-deps` for later phases |
| `The default kexec image only support x86_64 cpus` | aarch64 (or other) target with default image | Pass `--kexec` with a matching tarball (e.g. from nixos-images) |
| Disks empty / wrong layout after run | Default disko phase destroys then recreates | Confirm `disk-config` device names (`lsblk`); use `--vm-test` first |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | New install replaced host keys | `ssh-keygen -R <ip>` (or `--copy-host-keys` if you intentionally keep old keys) |
| `nix run` / flake errors on the source | Nix missing, or flakes/`nix-command` not enabled | Install Nix; enable experimental features; ensure `nix flake` works |
| Flake attribute missing | `#name` not under `nixosConfigurations` | Match the fragment to `nixosConfigurations.<name>` |
| No `tar` / `setsid` on target | Minimal OS without tools needed to unpack/run kexec | Install those tools, or boot a NixOS installer first |

**After install.** Host SSH keys usually change—clean `known_hosts`. Further config changes go through the flake with `nixos-rebuild switch --flake … --target-host …` or tools under [deployment and infra](../../12-deployment-and-infra/README.md) ([deploy-rs](../../12-deployment-and-infra/deploy-rs.md), [colmena](../../12-deployment-and-infra/colmena.md), etc.). See [remote deploy](../operations/remote-deploy.md).

## Examples

Install from a local flake onto a remote root SSH host:

```bash
nix run github:nix-community/nixos-anywhere -- \
  --flake .#myhost \
  --target-host root@203.0.113.10
```

Dry-run the system and disko layout in a VM:

```bash
nix run github:nix-community/nixos-anywhere -- \
  --flake .#myhost \
  --vm-test
```

Install without rebooting (stop after `install`):

```bash
nix run github:nix-community/nixos-anywhere -- \
  --flake .#myhost \
  --target-host root@203.0.113.10 \
  --phases kexec,disko,install
```

aarch64 (or other non‑default) target: pass a matching kexec tarball (build needs native aarch64, a remote builder, or `boot.binfmt.emulatedSystems`):

```bash
nix run github:nix-community/nixos-anywhere -- \
  --kexec "$(nix build --print-out-paths github:nix-community/nixos-images#packages.aarch64-linux.kexec-installer-nixos-unstable-noninteractive)/nixos-kexec-installer-noninteractive-aarch64-linux.tar.gz" \
  --flake .#myhost \
  --target-host root@203.0.113.10
```

## See also

- [Manual install](manual-install.md)
- [Graphical installer](graphical-installer.md)
- [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)
- [Remote deploy](../operations/remote-deploy.md)
- [disko](../../12-deployment-and-infra/disko.md)
- [Netboot and PXE](netboot-and-pxe.md)
- [Install and bootstrap](../../cheatsheets/install-and-bootstrap.md) — path chooser (ISO vs anywhere vs day-2)
- [nixos-anywhere bootstrap (worked example)](../../16-configuration-examples/nixos-anywhere-bootstrap.md)

## References

- [nixos-anywhere Quickstart](https://nix-community.github.io/nixos-anywhere/quickstart.html)
- [nixos-anywhere system requirements](https://nix-community.github.io/nixos-anywhere/)
- [nixos-anywhere Reference](https://nix-community.github.io/nixos-anywhere/reference.html)
- [Using your own kexec image](https://nix-community.github.io/nixos-anywhere/howtos/custom-kexec.html)
- [nixos-anywhere (GitHub)](https://github.com/nix-community/nixos-anywhere)
- [disko (GitHub)](https://github.com/nix-community/disko)
