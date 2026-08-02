---
status: complete
last-checked: 2026-08
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

**Distro notes (high level).**

These are orientation notes, not distro-specific install recipes. The official installer is the same script everywhere; differences are host policy, init, and where you put `/nix`.

| Distro family | Typical fit | Watch for |
|---------------|-------------|-----------|
| **Debian / Ubuntu** | Multi-user (`--daemon`) when systemd is present; common dev and CI base | Small root volumes; cloud images with tiny `/` need a separate durable `/nix` mount. Mixing Nix with apt is normal—distro owns `/usr`, Nix owns the store. |
| **Fedora / RHEL / Alma / Rocky** | Multi-user when systemd works and SELinux allows store/daemon writes | **SELinux enforcing** often blocks the daemon or store until policy is adjusted or the host is permissive for Nix paths. Confirm MAC before blaming Nix itself. |
| **Arch / Manjaro** | Multi-user on a typical systemd desktop or server | Rolling host + fixed Nix version: upgrade Nix with the installer’s documented path, not by layering a second install. Same `/nix` durability rules as everywhere else. |

**`/nix` must be durable and sized.** The store is the long-lived artifact cache: profiles, GC roots, and downloaded substitutes all live under `/nix`. Putting it on tmpfs, a small root partition, or a volume wiped on reboot causes data loss, failed builds, and constant GC pressure. Plan headroom (tens of GB for active dev; more for heavy language stacks or many projects). Bind-mount or partition `/nix` onto a persistent volume on cloud VMs and containers—see below.

**Home Manager (standalone).** Without NixOS modules, run Home Manager as a [standalone](home-manager/standalone-vs-nixos-module.md) tool against your user profile. That is the default user-env path on Ubuntu, Fedora, Arch, and similar: Nix installs packages and HM manages dotfiles, shells, and user services declaratively. You do not need NixOS or a system module; `home-manager switch` (or equivalent) updates the user generation. See [dotfiles patterns](home-manager/dotfiles-patterns.md) for layout conventions.

**Containers and CI.** Ephemeral dev or CI containers lose `/nix` on every run unless you persist it. Common patterns:

- **Bind-mount a host or named volume at `/nix`** so the store survives container recreation.
- **Official `nixos/nix` images** for a known-good Nix base; still mount `/nix` when jobs must reuse substitutes and profiles across runs.
- **Single-user (`--no-daemon`)** inside minimal containers without systemd is valid when isolation matters more than shared multi-user builds.

**Reinstall and upgrades.** Do not pipe a second installer over an existing daemon without following that installer’s documented uninstall first. Overlapping installs leave conflicting units, users, and store ownership. Use one installer family (official or Determinate) and its upgrade/uninstall docs; see [Installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md).

**Platform notes (high level).**

- **WSL2:** With systemd enabled, use multi-user (`--daemon`); otherwise single-user (`--no-daemon`)—same guidance as nix.dev. More WSL-specific context: [WSL and foreign OS](wsl-and-foreign-os.md).
- **macOS:** Multi-user via the official script; for whole-system declarative config see [nix-darwin](nix-darwin.md).

**Config.** Daemon and client settings live in [`nix.conf`](../05-cli-and-tooling/config/nix-conf.md) (and drop-ins). Foreign-distro setups often enable flakes and adjust substituters there after install—post-install tuning is normal on hosts that are not NixOS.

### Failure modes

| Symptom | Likely cause | What to check |
|---------|--------------|---------------|
| `nix` works once, store empty after reboot | `/nix` on tmpfs or ephemeral disk | Mount table: is `/nix` persistent? Size and filesystem type. |
| Permission denied writing to `/nix/store` | SELinux/AppArmor, wrong ownership, or single-user vs multi-user mismatch | Host MAC status; daemon running as expected user; install mode matches host (multi-user needs build users + daemon). |
| Daemon fails to start | No working systemd, or unit conflict from partial reinstall | `systemctl status nix-daemon` (or equivalent); only one install path; uninstall before re-running installer. |
| Builds succeed but are slow every time | No substituters, or fresh `/nix` each CI run | `nix.conf` substituters; bind-mount `/nix` in containers; check cache configuration. |
| `curl \| sh` installer errors mid-run | Existing Nix install, insufficient disk, or MAC blocking writes | Free space on `/nix` volume; documented uninstall; SELinux audit logs on Fedora/RHEL. |
| Profile tools missing in new shell | Hook not sourced in login shell | Installer’s `profile.d` snippet; open a new login shell or source as documented. |

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

**Container: bind-mount a persistent store** (illustrative Docker pattern):

```bash
docker run --rm -it \
  -v nix-store:/nix \
  -v "$PWD:/work" -w /work \
  nixos/nix
```

The named volume `nix-store` keeps substitutes and profiles across container runs; without it, every run starts with an empty store.

## References

- [Download Nix](https://nixos.org/download/) — official installer commands (Linux, macOS, WSL, Docker)
- [nix.dev — Install Nix](https://nix.dev/install-nix)
- [Nix manual — Installation](https://nixos.org/manual/nix/stable/installation/) — multi-user vs single-user

## See also

- [WSL and foreign OS](wsl-and-foreign-os.md) — Nix on Ubuntu-WSL vs NixOS-WSL
- [nix-darwin](nix-darwin.md)
- [Installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md) — which Nix installer on a foreign OS
- [Home Manager: standalone vs NixOS module](home-manager/standalone-vs-nixos-module.md)
- [Home Manager dotfiles patterns](home-manager/dotfiles-patterns.md)
- [nix.conf](../05-cli-and-tooling/config/nix-conf.md)
- [Profile](../02-concepts/profile.md)
- [Nix store layout](../04-store-and-build/nix-store-layout.md)
