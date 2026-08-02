---
status: complete
---

# Nix vs apt / pacman

## Overview

**apt** (Debian/Ubuntu), **pacman** (Arch), and **dnf** (Fedora/RHEL) are the usual *imperative* package managers on Linux: each install, upgrade, or remove mutates a shared system tree (`/usr`, `/etc`, a package database). The live machine is the record of what happened.

**Nix** stores packages as immutable paths under `/nix/store` and activates them through [profiles](../02-concepts/profile.md) and [generations](../02-concepts/generation.md). Upgrades switch a symlink to a new environment; rollbacks point it back. Multiple versions coexist because they never overwrite each other. The layout is not FHS: binaries live under hashed store paths, not a single `/usr/bin`.

Nix can run *beside* apt, pacman, or dnf on another distro—see [Nix on other distros](../10-home-and-user/nix-on-other-distros.md)—without replacing the host package manager. Distro PMs remain the right tool for the OS image and its services; Nix is a different packaging model, not a drop-in replacement for apt/pacman/dnf.

## Details

**Mutation model.**

| | apt / pacman / dnf | Nix |
|---|---|---|
| Source of truth | Package DB + files on disk after a sequence of commands | Store paths + which generation a profile points at (or a declarative config that builds one) |
| Upgrade | Replace packages in place under `/usr` | Build/activate a new generation; previous generation remains until GC |
| Rollback | Downgrade named packages, or restore backups/filesystem snapshots outside the PM | Switch profile (or boot) to a previous generation |
| Versions | One install of a package name in the system tree (conflicts otherwise) | Many versions side by side in the store; the profile chooses which are on `PATH` |
| Layout | FHS (`/usr`, `/lib`, …) | Non-FHS: `/nix/store/<hash>-name-version/…` |

See [Declarative vs imperative](../01-philosophy/declarative-vs-imperative.md) for the broader philosophy split. Note that `nix-env` / ad-hoc [`nix profile`](../05-cli-and-tooling/modern-cli/nix-profile.md) mutations are still *command-driven* on the profile; the difference from apt/pacman/dnf is the store + generation mechanism, not that every Nix workflow is declarative.

**Profiles and atomic switches.** A profile is a directory of symlinks into the store (typically reached via `~/.nix-profile`). Each install/upgrade/remove creates a new user environment and a numbered generation; the profile name is an atomic symlink flip to the new generation. That is how Nix gets atomic upgrades and cheap rollbacks without rewriting package files. Distro package managers can downgrade individual packages and work well with filesystem snapshots; they do not version a whole user environment as first-class generations the way Nix profiles do. On a foreign distro, apt/pacman/dnf still own the OS image and system services while Nix only manages store paths and profile links—mixing is normal: system packages from the distro, user tools and reproducible shells from Nix. Do not expect Nix packages to drop into `/usr` the way distro package managers do.

When both the distro and a Nix profile ship the same command name (e.g. `python`, `gcc`), whichever binary appears first on `PATH` wins—usually the profile hook prepends `~/.nix-profile/bin`, but login-shell init order can still leave you on the distro copy. Mixed library or runtime paths can then produce confusing link or version errors even though neither package manager overwrote the other.

apt/pacman/dnf change the host filesystem in place. Nix isolates *builds and package trees* via the store; it is not the same isolation story as Docker images—see [Nix vs Docker](nix-vs-docker.md).

## Examples

**Imperative install on a distro vs Nix profile:**

```bash
# apt / pacman / dnf: mutate the system package set
sudo apt install htop
# or: sudo pacman -S htop
# or: sudo dnf install htop

# Nix: add a package to the user profile (new generation)
# Prefer modern CLI (`nix-command` + usually `flakes`):
nix profile add nixpkgs#htop
# Classic equivalent: nix-env -iA nixpkgs.htop
```

**Rollback after a bad upgrade:**

```bash
# apt/pacman/dnf: no first-class “previous whole environment”; typically
# downgrade specific packages or restore from backup/snapshots outside
# the package manager.

# Nix: list and switch profile generations
nix profile history
nix profile rollback
# Classic: nix-env --list-generations / nix-env --rollback
```

**Side-by-side versions (Nix):** two builds of the same package land in different store paths; only the ones linked into the active profile appear on `PATH`. apt/pacman/dnf generally keep one version of a given package name in the system tree.

## References

- [NixOS project site](https://nixos.org/)
- [Nix reference manual](https://nix.dev/manual/nix/)
- [Nix manual — Profiles](https://nix.dev/manual/nix/stable/package-management/profiles.html) — generations, atomic upgrades, rollback
- [Nix manual — `nix profile`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile.html) — experimental modern profile CLI (`nix-command`)

## See also

- [Declarative vs imperative](../01-philosophy/declarative-vs-imperative.md)
- [Profile](../02-concepts/profile.md)
- [Generation](../02-concepts/generation.md)
- [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md)
- [Nix on other distros](../10-home-and-user/nix-on-other-distros.md)
- [Nix vs Docker](nix-vs-docker.md)
