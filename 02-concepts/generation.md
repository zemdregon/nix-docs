---
status: complete
---

# Generation

## Overview

A **generation** is a numbered snapshot of a [profile](profile.md) or NixOS system configuration. Each snapshot is an immutable [store path](store-path.md) (or closure rooted at one). Upgrading or rolling back means switching which generation the profile points at—not mutating existing store content.

## Details

**Numbered history.** Profiles keep a sequence `1`, `2`, `3`, … Every install, upgrade, or remove on a user profile, or a successful `nixos-rebuild` that produces a new system closure, adds the next generation. The profile name symlink always references the current (active) generation.

**Switch without mutation.** Generations coexist in the store. Activating generation *N* rewires the profile pointer to generation *N*'s closure; generation *N − 1* remains on disk until garbage collection removes unreferenced paths. This is how Nix implements atomic upgrades and instant rollbacks—see [Immutability and rollback](../01-philosophy/immutability-and-rollback.md).

**User vs system generations.**

| Context | What each generation captures | Typical commands |
|---------|------------------------------|------------------|
| User [profile](profile.md) | Set of packages in that profile | `nix-env --list-generations`, `nix-env --rollback`, `nix profile history` / `nix profile rollback` |
| NixOS system profile | Full system closure: kernel, init, services, `/etc` | `nixos-rebuild list-generations`, boot menu, `nixos-rebuild switch --rollback` |

User and system generations are independent: rolling back a user profile does not change the running NixOS system generation, and vice versa.

**Boot integration.** On NixOS, each system generation gets a boot loader entry. Selecting an older entry at boot activates that generation's closure—see [Generations and boot](../09-nixos/architecture/generations-and-boot.md).

## Examples

```bash
# User profile: show history and roll back
nix-env --list-generations
nix-env --switch-generation 42
nix-env --rollback

# NixOS: list system generations and roll back the active one
sudo nixos-rebuild list-generations
sudo nixos-rebuild switch --rollback
```

Deleting old generations (`nix-env --delete-generations`, `nix-collect-garbage`) drops GC roots; unreferenced store paths can then be collected.

## References

- [Nix manual — Profiles](https://nix.dev/manual/nix/stable/command-ref/files/profiles.html) — profile layout, numbered generations, and GC roots
- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — system generations, boot entries, and rollback

## See also

- [Profile](profile.md)
- [Store path](store-path.md)
- [Immutability and rollback](../01-philosophy/immutability-and-rollback.md)
- [Generations and boot](../09-nixos/architecture/generations-and-boot.md)
- [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md)
- [Garbage collection](../04-store-and-build/garbage-collection.md)
