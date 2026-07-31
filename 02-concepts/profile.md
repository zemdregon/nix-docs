---
status: complete
---

# Profile

## Overview

A **profile** is a named, mutable view into the [Nix store](store-path.md): a directory of symlinks to store paths that represents an active package set or environment. Profiles live **outside** the store in a profiles directory—typically `/nix/var/nix/profiles/` (or `$XDG_STATE_HOME/nix/profiles` when [`useXDGBaseDirectories`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-use-xdg-base-directories) is enabled). `~/.nix-profile` is usually a symlink to the current **user** profile so shells can put `~/.nix-profile/bin` on `PATH`.

Each install, upgrade, or remove appends a numbered [generation](generation.md). The profile name points at `profile-N-link`, which points at that generation’s store path; older generations stay on disk for rollback. Active and historical profile links are [GC roots](../04-store-and-build/garbage-collection.md), keeping their closures reachable until you delete those generations or collect garbage.

## Details

### Layout

**Profiles directory.** Nix keeps profile metadata under the state directory. With default paths, user profiles sit in `/nix/var/nix/profiles/per-user/<user>/`; root’s profile uses `/nix/var/nix/profiles/per-user/root/profile`. With XDG base directories, a regular user’s profiles are under `$XDG_STATE_HOME/nix/profiles/` instead.

**Name → link → store path.** For a profile named `profile`, the layout is:

```text
…/profiles/profile          → profile-7-link
…/profiles/profile-7-link   → /nix/store/…-profile
```

Each `profile-N-link` symlink is itself a GC root. The store path it targets is a **symlink farm**: `bin/`, `share/`, and other trees contain symlinks into installed packages—not copies of store content.

**User profile link.** The installer typically creates `~/.nix-profile` pointing at the active user profile (or `$XDG_STATE_HOME/nix/profile` when XDG mode is on). Activation scripts and shell profiles add its `bin/` to `PATH`; other outputs (man pages, `.desktop` files) are exposed the same way.

### Generations

**Numbered snapshots.** Every mutation creates generation *N + 1*: a new store path and a new `profile-(N+1)-link`. The profile name symlink is rewired to the new link; generation *N*’s store path remains until nothing references it. Rolling back means switching the name symlink to an older `profile-M-link`—see [Generation](generation.md) and [Immutability and rollback](../01-philosophy/immutability-and-rollback.md).

**Manifests.** Each generation’s store path includes a manifest of installed packages:

| CLI | Manifest file | Notes |
|-----|---------------|-------|
| [`nix-env`](../05-cli-and-tooling/classic-cli/nix-env.md) | `manifest.nix` | Nix expression listing package names and store paths |
| [`nix profile`](../05-cli-and-tooling/modern-cli/nix-profile.md) | `manifest.json` | JSON metadata for profile entries (experimental `nix-command`) |

Both tools read and write through the same on-disk profile machinery; only the manifest format and CLI differ.

### Profile types

Profiles are a shared mechanism; **which profile** you touch depends on the command:

| Profile | Typical path | Managed by | Purpose |
|---------|--------------|------------|---------|
| User | `~/.nix-profile` → `…/profiles/profile` | `nix-env`, `nix profile` | Per-user packages and tools |
| Channels | `…/profiles/channels` (linked from `~/.nix-defexpr/channels`) | [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md) | Downloaded [channel](channel.md) trees for `<nixpkgs>` |
| System (NixOS) | `/nix/var/nix/profiles/system` | `nixos-rebuild` | Whole-system closure: kernel, services, `/etc` |

User, channels, and system profiles evolve independently. Updating a channel generation does not change the user package profile; on NixOS, rolling back the system profile does not roll back a user’s tools.

### GC roots

**Why profiles matter for GC.** Each `profile-N-link` symlink registered with the store is a GC root. So are the user profile link (`~/.nix-profile`) and, on NixOS, the system profile. Garbage collection deletes only store paths with no remaining roots—historical generations stay reachable until you remove them (`nix-env --delete-generations`, `nix profile wipe-history`, `nix-collect-garbage`, etc.). See [Garbage collection](../04-store-and-build/garbage-collection.md).

### Classic vs modern CLI

**Same storage, different front ends.** [`nix-env`](../05-cli-and-tooling/classic-cli/nix-env.md) and [`nix profile`](../05-cli-and-tooling/modern-cli/nix-profile.md) both mutate the default user profile through the generation machinery above. `nix-env -i` / `-u` / `-e` and `nix profile install` / `remove` each produce a new generation and rewrite the profile symlink.

Prefer `nix profile` for flake-friendly installs and JSON-oriented tooling; `nix-env` remains common on older workflows and in docs that assume channels. Neither edits store paths in place—both only advance or rewind the profile pointer.

### Boundaries (what this page is not)

- **Not generation mechanics** — numbered snapshots and rollback semantics are [generation](generation.md).
- **Not the store model** — path identity and immutability are [store path](store-path.md).
- **Not NixOS system profiles** — boot entries and `nixos-rebuild` are [generations and boot](../09-nixos/architecture/generations-and-boot.md).

## Examples

```bash
# Inspect the default user profile layout (XDG or classic path)
ls -l ~/.nix-profile
ls -l "${XDG_STATE_HOME:-$HOME/.local/state}/nix/profiles/profile"* 2>/dev/null \
  || ls -l /nix/var/nix/profiles/per-user/"$USER"/profile*

# Classic: list generations and roll back
nix-env --list-generations
nix-env --rollback

# Modern (requires nix-command): history and rollback
nix profile history
nix profile rollback

# See what a generation keeps alive (store path from profile-N-link)
nix-store --query --requisites "$(readlink -f ~/.nix-profile)"
```

On NixOS, `nixos-rebuild list-generations` shows **system** profile generations; the boot loader can boot any listed generation—see [Generations and boot](../09-nixos/architecture/generations-and-boot.md).

## References

- [Nix manual — Profiles](https://nix.dev/manual/nix/stable/command-ref/files/profiles.html) — filesystem layout, manifests, and GC roots
- [Nix manual — User profile link](https://nix.dev/manual/nix/stable/command-ref/files/profiles.html#user-profile-link) — `~/.nix-profile` and XDG paths
- [Nix manual — Channels layout](https://nix.dev/manual/nix/stable/command-ref/files/channels.html) — channels profile and subscription files
- [Nix manual — `nix profile`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile.html) — modern profile commands (`nix-command`)
- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — system profile and activation

## See also

- [Generation](generation.md)
- [Store path](store-path.md)
- [Channel](channel.md)
- [Immutability and rollback](../01-philosophy/immutability-and-rollback.md)
- [Generations and boot](../09-nixos/architecture/generations-and-boot.md)
- [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md)
- [nix-env](../05-cli-and-tooling/classic-cli/nix-env.md)
- [Garbage collection](../04-store-and-build/garbage-collection.md)
