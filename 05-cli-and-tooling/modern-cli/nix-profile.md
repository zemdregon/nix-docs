---
status: complete
---

# nix profile

## Overview

**`nix profile`** is the Nix 3 CLI for managing user [profiles](../../02-concepts/profile.md): install, upgrade, remove, and inspect packages in a versioned symlink tree on `PATH`. It is the modern replacement for [`nix-env`](../classic-cli/nix-env.md) on the default user profile, using flake [installables](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html#installables) (`nixpkgs#hello`) instead of attribute paths against `<nixpkgs>`.

The command is **experimental**—its interface can change between Nix releases. It requires the [`nix-command`](../../08-experimental-features/nix-command.md) experimental feature (and typically [flakes](../../08-experimental-features/flakes.md) for registry-style refs like `nixpkgs#hello`).

## Details

**Profiles and generations.** Each install, remove, or upgrade appends a new numbered [generation](../../02-concepts/generation.md) to the profile. The profile name is a symlink to `profile-N-link`, which points at an immutable store path of symlinks into installed packages. Older generations stay available for rollback until you delete them or run garbage collection.

**Default locations.** Profile data lives under `$XDG_STATE_HOME/nix/profiles` (usually `~/.local/state/nix/profiles`). The active user profile is reached through `~/.nix-profile` (or `$XDG_STATE_HOME/nix/profile` when `use-xdg-base-directories` is enabled). Each generation is a GC root until removed.

**Manifest format.** `nix profile` records installed packages in `manifest.json`. Classic [`nix-env`](../classic-cli/nix-env.md) uses `manifest.nix`. Once you install with `nix profile`, the default profile is incompatible with `nix-env` until you delete that profile directory (which removes installed packages).

### Subcommands

| Subcommand | Purpose |
|------------|---------|
| `add` / `install` | Add one or more installables to the profile (`install` is an alias for `add`) |
| `list` | Show packages in the profile (name, flake refs, store paths); supports `--json` |
| `remove` | Remove by name, store path, `--regex`, or `--all` |
| `upgrade` | Re-fetch unlocked flake refs and rebuild matched packages (`--all`, name, or `--regex`) |
| `history` | Top-level add/remove/upgrade between profile versions |
| `rollback` | Switch to the previous version, or `--to N` |
| `diff-closures` | Closure diff between successive profile versions (includes dependencies) |
| `wipe-history` | Delete non-current profile versions; optional `--older-than Nd` |

Most subcommands accept `--profile path` to target a profile other than the default.

**Upgrade caveat.** `upgrade` only advances packages installed with an *unlocked* flake reference (e.g. `nixpkgs#hello`). A fully locked ref (e.g. `github:NixOS/nixpkgs/<rev>#hello`) has no “latest” to fetch.

**History vs diff-closures.** `history` shows top-level package changes between versions (`∅ -> version` for adds, `version -> ∅` for removes). `diff-closures` compares full closures—including dependencies—and works on any profile path (including the NixOS system profile).

## Examples

Enable the modern CLI, then manage the default user profile:

```bash
# One-off (flakes usually needed for nixpkgs# refs)
nix --extra-experimental-features 'nix-command flakes' profile add nixpkgs#hello

# List installed packages
nix profile list

# Upgrade everything installed from unlocked flakes
nix profile upgrade --all

# Inspect version history and roll back
nix profile history
nix profile rollback
nix profile rollback --to 510

# See dependency-level changes between generations
nix profile diff-closures

# Trim old generations (keeps current)
nix profile wipe-history --older-than 30d
```

Remove a package and inspect JSON output:

```bash
nix profile remove hello
nix profile list --json
```

Persistent enablement in `nix.conf`:

```ini
experimental-features = nix-command flakes
```

## References

- [Nix manual — `nix profile`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile.html)
- [Nix manual — `nix profile add`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-add.html)
- [Nix manual — `nix profile list`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-list.html)
- [Nix manual — `nix profile remove`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-remove.html)
- [Nix manual — `nix profile upgrade`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-upgrade.html)
- [Nix manual — `nix profile history`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-history.html)
- [Nix manual — `nix profile rollback`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-rollback.html)
- [Nix manual — `nix profile diff-closures`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-diff-closures.html)
- [Nix manual — `nix profile wipe-history`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile-wipe-history.html)

## See also

- [nix-env](../classic-cli/nix-env.md) — classic user profile management
- [Profile](../../02-concepts/profile.md) — symlink farms, user vs system profiles
- [Generation](../../02-concepts/generation.md) — numbered snapshots and rollback
- [nix-command](../../08-experimental-features/nix-command.md) — enabling the Nix 3 CLI
- [Garbage collection](../../04-store-and-build/garbage-collection.md) — reclaiming store space after wiping history
