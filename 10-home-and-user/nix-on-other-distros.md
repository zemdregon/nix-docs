---
status: complete
---

# Nix on Other Distros

## Overview

Nix runs on ordinary Linux distributions and macOS without replacing the host OS. You install the package manager beside apt, dnf, pacman, or Homebrew; packages land in a separate [`/nix` store](../04-store-and-build/nix-store-layout.md), and the distro still owns the system. Multi-user install with a daemon is the recommended default on Linux (systemd) and macOS. On foreign distros, [Home Manager in standalone mode](home-manager/standalone-vs-nixos-module.md) is the usual way to manage a declarative user environment.

## Details

**Installers.** The [official installer](https://nixos.org/download/) (`curl … | sh`) is the canonical path on Linux and macOS; [nix.dev — Install Nix](https://nix.dev/install-nix) mirrors the same commands. The Determinate Systems installer is a common alternative with its own defaults and uninstall story—pick one and stick to its docs. Both put Nix on the machine; neither turns the host into NixOS.

**Coexistence with the distro.** Distro package managers keep managing `/usr`, services, and the kernel. Nix manages store paths and [profiles](../02-concepts/profile.md) under `/nix` (and user profile links). Mixing is normal: use the distro for system packages and services, Nix for reproducible user tools, shells, and project inputs. Do not expect Nix to replace systemd units or package databases owned by the host.

**Multi-user vs single-user.**

| Mode | Flag | When |
|------|------|------|
| Multi-user (recommended) | `--daemon` | Linux with systemd (SELinux off / compatible), macOS; better isolation and shared builds |
| Single-user | `--no-daemon` | No systemd, constrained environments; Nix owned by the installing user |

Multi-user creates build users and a daemon (systemd unit on Linux). Single-user has fewer prerequisites but weaker sharing and isolation. Official guidance: prefer multi-user when the platform supports it.

**Platform notes (high level).**

- **WSL2:** With systemd enabled, use multi-user (`--daemon`); otherwise single-user (`--no-daemon`)—same guidance as nix.dev.
- **Containers / Docker:** Official images (`nixos/nix`) or a bind-mounted store; ephemeral containers lose `/nix` unless you persist it.
- **macOS:** Multi-user via the official script; for whole-system declarative config see [nix-darwin](nix-darwin.md).

**Pitfalls.**

- **SELinux / AppArmor:** Multi-user install expects SELinux disabled or a working policy; MAC frameworks can block store writes or the daemon—check host policy before debugging Nix itself.
- **systemd:** The daemon unit needs a working systemd; without it, use single-user or fix the host init story first.
- **`/nix` on temp or tiny disks:** Putting `/nix` on tmpfs, a small root, or a volume that is wiped on reboot loses the store or fills the disk under GC pressure. Prefer a durable, sized partition or volume for `/nix`.

**Config.** Daemon and client settings live in [`nix.conf`](../05-cli-and-tooling/config/nix-conf.md) (and drop-ins). Foreign-distro setups often enable flakes and adjust substituters there after install.

**Home Manager.** Without NixOS modules, run Home Manager as a [standalone](home-manager/standalone-vs-nixos-module.md) tool against your user profile—this is the common pattern on Ubuntu, Fedora, Arch, and similar.

## Examples

Commands from [nix.dev — Install Nix](https://nix.dev/install-nix) (illustrative; do not re-run on an already-installed host):

```bash
# Linux: recommended multi-user install
curl -L https://nixos.org/nix/install | sh -s -- --daemon

# Linux: single-user (no systemd / constrained host)
curl -L https://nixos.org/nix/install | sh -s -- --no-daemon

# Verify in a new shell
nix --version
```

WSL2 with systemd enabled uses the same `--daemon` line; without systemd, use `--no-daemon`.

## References

- [Download Nix](https://nixos.org/download/) — official installer commands (Linux, macOS, WSL, Docker)
- [nix.dev — Install Nix](https://nix.dev/install-nix)
- [Nix manual — Installation](https://nixos.org/manual/nix/stable/installation/) — multi-user vs single-user

## See also

- [WSL and foreign OS](wsl-and-foreign-os.md) — Nix on Ubuntu-WSL vs NixOS-WSL
- [nix-darwin](nix-darwin.md)
- [Installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md) — which Nix installer on a foreign OS
- [Home Manager: standalone vs NixOS module](home-manager/standalone-vs-nixos-module.md)
- [nix.conf](../05-cli-and-tooling/config/nix-conf.md)
- [Profile](../02-concepts/profile.md)
- [Nix store layout](../04-store-and-build/nix-store-layout.md)
