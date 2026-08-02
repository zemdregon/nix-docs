---
status: complete
---

# Generation

## Overview

A **generation** is a numbered snapshot of a [profile](profile.md) or NixOS system configuration. Each snapshot is an immutable [store path](store-path.md) (or the closure rooted at that path). Installing, upgrading, removing, or rebuilding does not edit store content in place—it appends generation *N + 1* and moves the profile pointer. Upgrading or rolling back means switching which generation the profile references.

## Details

Every profile keeps a monotonic sequence `1`, `2`, `3`, … under the profiles directory (typically `/nix/var/nix/profiles/` for system profiles, or `$XDG_STATE_HOME/nix/profiles` for user profiles when XDG base dirs are enabled). Each successful mutation—`nix-env` / `nix profile` install or remove on a user profile, or a successful `nixos-rebuild` that produces a new system closure—creates the next generation.

On disk, generations appear as versioned symlinks (`profile-42-link`, `system-7-link`, …) pointing at store closures. The profile **name** symlink (`profile`, `system`, …) always references the **current** (active) generation. Listing history shows the number, build time, and the store path each generation resolves to.

Generations coexist in the store. Activating generation *N* updates the profile name symlink to `…-N-link`; generation *N − 1* and its closure remain on disk until nothing roots them. No generation’s store paths are mutated after creation. This is how Nix implements atomic upgrades and instant rollbacks—see [Immutability and rollback](../01-philosophy/immutability-and-rollback.md).

**User vs system.** User profile generations and NixOS system generations use the same mechanism but different profiles, commands, and lifecycles. They are fully independent: rolling back packages in `~/.nix-profile` does not change the running system generation, and `nixos-rebuild switch --rollback` does not touch user profiles.

| Context | What each generation captures | List / inspect | Switch or roll back | Prune old generations |
|---------|--------------------------------|----------------|---------------------|------------------------|
| User [profile](profile.md) | Set of packages in that profile’s symlink farm | `nix-env --list-generations`, `nix profile history` | `nix-env --switch-generation N`, `nix-env --rollback`, `nix profile rollback` | `nix-env --delete-generations …` |
| NixOS system profile | Full system closure: kernel, initrd, init, services, `/etc` | `nixos-rebuild list-generations` | Boot menu entry, `nixos-rebuild switch --rollback`, `switch-to-configuration` on a specific `system-N-link` | `nix-env -p /nix/var/nix/profiles/system --delete-generations …` |

Classic `nix-env` and modern `nix profile` both append generations to the same user profile layout; prefer `nix profile history` / `nix profile rollback` when using the [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md) interface.

On NixOS, each retained system generation gets a boot loader entry (GRUB, systemd-boot, etc.). Selecting an older entry at boot loads that generation’s closure as `/run/current-system` without rewriting the live store tree. The profile default (`/nix/var/nix/profiles/system`) can differ from the booted generation after `nixos-rebuild test` or after booting an older menu entry until you re-register the default. Boot-loader wiring and activation semantics are covered in [Generations and boot](../09-nixos/architecture/generations-and-boot.md).

[NixOS specialisations](../09-nixos/configuration/specialisations.md) build additional system closures alongside the base configuration. Rebuild operations that register a generation also make specialisations bootable as sibling entries tied to that parent generation—useful for variant configs (debug kernels, minimal rescue setups) without a separate profile history.

Each kept generation is a [GC root](../04-store-and-build/garbage-collection.md): the profile version symlink keeps that generation’s entire closure reachable. Deleting generations with `nix-env --delete-generations` (or profile-aware `nix-collect-garbage --delete-old` / `--delete-older-than`) removes those roots; a subsequent `nix-collect-garbage` or `nix-store --gc` can then delete store paths nothing references anymore. Pruning frees disk but removes rollback targets for deleted numbers—balance retention against space, especially on `/nix/store` and `/boot`.

## Examples

User profiles, NixOS system profiles, and pruning old generations:

```bash
# Classic nix-env
nix-env --list-generations
nix-env --switch-generation 42
nix-env --rollback

# Modern nix profile (same underlying generations; needs nix-command)
nix profile history
nix profile rollback
nix profile rollback --to 42
```

```bash
sudo nixos-rebuild list-generations
sudo nixos-rebuild switch --rollback

# Activate generation 7 now and set it as the boot default
sudo /nix/var/nix/profiles/system-7-link/bin/switch-to-configuration switch
```

```bash
# Keep only the current generation and generations newer than 30 days
sudo nix-env -p /nix/var/nix/profiles/system \
  --delete-generations 30d

sudo nix-collect-garbage
```

## References

- [Nix manual — Profiles](https://nix.dev/manual/nix/stable/command-ref/files/profiles.html) — profile layout, numbered generations, and GC roots
- [NixOS manual — Profiles and generations](https://nixos.org/manual/nixos/stable/index.html#sec-profiles) — system generations, boot entries, and rollback

## See also

- [Profile](profile.md)
- [Store path](store-path.md)
- [Immutability and rollback](../01-philosophy/immutability-and-rollback.md)
- [Generations and boot](../09-nixos/architecture/generations-and-boot.md)
- [Specialisations](../09-nixos/configuration/specialisations.md)
- [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md)
- [Garbage collection](../04-store-and-build/garbage-collection.md)
