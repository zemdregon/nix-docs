---
status: complete
---

# Immutability and Rollback

## Overview

Nix treats built artifacts as **immutable**: once a [store path](../02-concepts/store-path.md) exists under `/nix/store`, it is never modified in place. Upgrades **add** new paths and change which closure is *active* by moving a pointer—an environment [profile](../02-concepts/profile.md) or a NixOS system [generation](../02-concepts/generation.md)—not by overwriting live files. Rollback is the same operation in reverse: point back at a previous generation that still lives in the store.

Store immutability is not the same as “immutable OS image” marketing. Nix does not freeze a single root filesystem; it keeps old closures addressable until [garbage collection](../04-store-and-build/garbage-collection.md) drops their references. The **generation** (or profile generation) is the rollback unit.

## Details

### Immutable store paths

Builds write content-addressed paths under `/nix/store`. Rebuilding the same derivation yields the same path; changing inputs yields a new path. Old and new versions coexist until nothing references the old ones. That is why upgrades do not silently rewrite binaries other software still depends on—see [Why Nix](why-nix.md) for the broader motivation.

### Profiles and generations as pointers

What you run day to day is not “the store” wholesale but the closure reachable from the current profile or generation. Installing or upgrading appends a new profile generation (a user environment of symlinks into the store) and atomically flips the profile’s current symlink. Switching NixOS generations swaps the system closure the boot loader and activation scripts use. The previous closure remains on disk as long as it is referenced.

### Rollback without overwrite

On NixOS, boot entries for earlier generations (or `nixos-rebuild switch --rollback`) restore the prior system pointer. For user environments managed with `nix-env`, `nix-env --rollback` moves the active profile back one step; `--switch-generation` selects a specific generation. Operational detail lives under [Rollbacks](../09-nixos/operations/rollbacks.md).

### Garbage collection and retention

`nix-store --gc` (and related collect-garbage commands) deletes **unreferenced** store paths. Paths kept via profiles, generations, or other GC roots survive—so rollbacks stay possible until you remove those references. Blind GC after a bad upgrade can erase the only working closure.

### Not an immutable appliance image

Some systems achieve rollback by swapping whole disk images or A/B partitions. Nix’s model is different: mutable configuration and user data still live outside `/nix/store`, while packages and system closures are immutable store objects selected by generation links. You roll back a **generation**, not by restoring a snapshot of every byte on the machine.

## Examples

**Upgrade adds a path; activation flips a pointer.** `nixos-rebuild switch` builds or substitutes a new system closure, creates a new generation under `/nix/var/nix/profiles/`, and makes it the default boot entry. Earlier generations remain selectable until GC removes their roots.

**Rollback from a running system or the boot menu.** If a rebuild leaves the machine usable but broken, `nixos-rebuild switch --rollback` activates the previous system generation and sets it as the boot default. If the new generation fails to boot, choose the previous entry from the boot loader (for example under GRUB’s “NixOS - All configurations” submenu, or the matching systemd-boot list).

**User-environment rollback.** After a bad `nix-env` install, `nix-env --rollback` (or `nix-env --switch-generation N`) points `~/.nix-profile` at an earlier user environment. List candidates with `nix-env --list-generations`.

These scenarios stay high level here; [Rollbacks](../09-nixos/operations/rollbacks.md) covers boot-default vs running activation and safer `test` workflows.

## References

- [Nix manual — profiles](https://nix.dev/manual/nix/stable/package-management/profiles.html) — user environments, generations, atomic upgrades and rollback
- [Nix manual — Nix store](https://nix.dev/manual/nix/stable/store/index.html) — store paths and identity
- [Nix manual — garbage collection](https://nix.dev/manual/nix/stable/package-management/garbage-collection.html)
- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — system configuration, generations, and activation
- [NixOS manual — rolling back](https://nixos.org/manual/nixos/stable/index.html#sec-rollback)

## See also

- [Why Nix](why-nix.md)
- [Generation](../02-concepts/generation.md)
- [Profile](../02-concepts/profile.md)
- [Store path](../02-concepts/store-path.md)
- [Garbage collection](../04-store-and-build/garbage-collection.md)
- [Rollbacks](../09-nixos/operations/rollbacks.md)
