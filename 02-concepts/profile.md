---
status: complete
---

# Profile

## Overview

A **profile** is a named, mutable pointer into the [Nix store](store-path.md): a directory of symlinks that represents an active package set or environment. Profile generations live outside the store under the profiles directory (typically `/nix/var/nix/profiles/…`, or `$XDG_STATE_HOME/nix/profiles` when XDG base dirs are enabled); `~/.nix-profile` is usually a symlink to the current user profile. Each change appends a new [generation](generation.md) while older generations remain available for rollback.

## Details

**Symlink farm.** A profile directory contains symlinks to [store paths](store-path.md)—one per installed package or component. Activating a profile puts its `bin/` on `PATH` and exposes other outputs (man pages, libraries) without copying or modifying store content.

**Generations.** Each profile mutation (install, upgrade, remove) creates a numbered generation. The profile name is a symlink to `profile-N-link`, which points at the current generation's store path. Switching generations rewires that pointer; store paths are never edited in place.

**User vs system profiles.**

| Profile | Location (typical) | Managed by | Purpose |
|---------|-------------------|------------|---------|
| User | `~/.nix-profile` → profiles dir (`…/profiles/profile`) | `nix-env`, [`nix profile`](../05-cli-and-tooling/modern-cli/nix-profile.md) | Per-user packages and tools |
| System (NixOS) | `/nix/var/nix/profiles/system` | `nixos-rebuild` | Whole-system closure: kernel, services, `/etc` |

On NixOS, the system profile is the live system [generation](generation.md); user profiles are independent and can differ per account.

**GC roots.** Active and historical profile generations are [GC roots](../04-store-and-build/garbage-collection.md), keeping their closures reachable until you delete those generations or run garbage collection.

## Examples

```bash
# List generations of the default user profile
nix-env --list-generations

# Roll back one generation
nix-env --rollback

# Modern CLI (`nix-command`): history and rollback
nix profile history
nix profile rollback
```

On NixOS, `nixos-rebuild list-generations` shows system profile generations; the boot loader can boot any listed generation.

## References

- [Nix manual — Profiles](https://nix.dev/manual/nix/stable/command-ref/files/profiles.html) — filesystem layout, manifests, and user profile link
- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — system profile and activation

## See also

- [Generation](generation.md)
- [Store path](store-path.md)
- [Immutability and rollback](../01-philosophy/immutability-and-rollback.md)
- [Generations and boot](../09-nixos/architecture/generations-and-boot.md)
- [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md)
- [Garbage collection](../04-store-and-build/garbage-collection.md)
