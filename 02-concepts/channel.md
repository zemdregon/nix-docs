---
status: complete
---

# Channel

## Overview

A **channel** is a named, updatable subscription to a remote set of Nix expressions—most often Nixpkgs—managed with [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md). You point a short name at a URL (typically under [channels.nixos.org](https://channels.nixos.org/)), run `nix-channel --update`, and evaluation finds the downloaded tree via `NIX_PATH` / `<nixpkgs>`.

Channels are the classic distribution mechanism. They contrast with [flakes](flake.md), which pin inputs in a lockfile: both remain relevant. Deep comparison lives in [Flakes vs Channels](../comparisons/flakes-vs-channels.md); migration in [Migration from Channels](../07-flakes/migration-from-channels.md).

## Details

### Subscription vs download

Two separate steps keep the *intent* (what you want) distinct from the *contents* (what is on disk):

| Step | Command | What changes |
|------|---------|--------------|
| Subscribe | `nix-channel --add URL NAME` | Appends a line to the subscribed-channels file |
| Download | `nix-channel --update` [NAME…] | Fetches tarballs and creates a new channels [profile](profile.md) [generation](generation.md) |

`--add` only records the pairing of name and URL. It does **not** fetch anything. If you omit `NAME`, Nix derives one from the last URL path component (stripping `-stable` / `-unstable` suffixes). `--remove NAME` drops a subscription; `--list` prints name/URL pairs.

The URL must point at a directory that serves `nixexprs.tar.gz`. That tarball unpacks to a single top-level directory containing `default.nix`—the channel entry point. Official lines include `nixpkgs-unstable` and stable NixOS release channels (`nixos-YY.MM`).

### Subscribed-channels file

Subscriptions live outside the store:

- `~/.nix-channels` (classic default)
- `$XDG_STATE_HOME/nix/channels` when `use-xdg-base-directories = true` in `nix.conf`

Each line is `URL NAME`. This file is the source of truth for *what* to update; it does not hold expression contents.

### On-disk layout after `--update`

`nix-channel --update` uses the same [profile](profile.md) machinery as `nix-env`. Each successful update appends a generation to the **channels profile**:

| Layout | Path (typical) |
|--------|----------------|
| Channels profile (user) | `$XDG_STATE_HOME/nix/profiles/channels` when XDG is enabled; otherwise `/nix/var/nix/profiles/per-user/$USER/channels` |
| Channels profile (root) | `$NIX_STATE_DIR/profiles/per-user/root/channels` |

The profile is a symlink farm: one symlink per subscribed channel name, each pointing at the unpacked channel tree in the store. Older generations remain until pruned or collected.

On many installs, `~/.nix-defexpr/channels` is a symlink into that profile so classic tools can discover channels without custom `NIX_PATH` wiring. The exact default `nix-path` / `NIX_PATH` layout depends on your Nix version and config; explicit `-I` or `NIX_PATH` always overrides.

Downloaded tarballs are also **cached**; TTL is controlled by `tarball-ttl` in `nix.conf` or `--tarball-ttl` on the command line.

### How evaluation resolves `<nixpkgs>`

Classic commands (`nix-build`, `nix-shell`, `nix-instantiate`) resolve lookup paths such as `<nixpkgs>` through the configured search path:

1. Entries from `-I` / `--include` (highest precedence)
2. The `NIX_PATH` environment variable (colon-separated `prefix=path` entries)
3. The `nix-path` setting in `nix.conf`

A typical default includes `nixpkgs=…` pointing at the active channels profile entry (or `~/.nix-defexpr/channels`). In Nix code, `<nixpkgs>` desugars to `builtins.findFile builtins.nixPath "nixpkgs"`.

Because the channel snapshot lives **outside** any expression that imports it, the Nix manual warns that this limits reproducibility: the same `.nix` file can evaluate differently after someone runs `--update` on another machine or day. Flake workflows instead declare inputs inside the project and record exact revisions in `flake.lock`.

### Pinning limits

A channel URL identifies a **release line**, not a single Git commit. `https://channels.nixos.org/nixpkgs-unstable` always means “whatever the channel builders published most recently for unstable,” so:

- Two machines with the same channel name can evaluate different nixpkgs revisions if they updated on different days.
- Re-running `--update` advances the line; there is no first-class lockfile in the channel model.
- `--rollback` restores an earlier **channels profile generation**, not a commit hash checked into your project.

For reproducible configs without flakes, pin inside the expression (`builtins.fetchTarball` / `fetchGit` with a hash), use helper tools (niv, npins), or set `NIX_PATH` to a fixed tarball URL or local checkout under version control. See [pinning in nixpkgs](../06-nixpkgs/overlays-and-overrides/pinning.md).

### Channels profile as a GC root

Each channels profile [generation](generation.md) is registered as a [GC root](../04-store-and-build/garbage-collection.md): the profile symlink chain and generation links keep the unpacked channel trees and their dependencies reachable. That is why `--list-generations` and `--rollback` work—the previous generation’s store closure is still rooted until you delete those generations or run garbage collection that prunes them.

Pruning old channel generations (via `nix-env -p …/channels --delete-generations` or broader GC with `--delete-old`) frees disk space but removes rollback targets for deleted generations.

### Boundaries (what this page is not)

- **Not flake inputs or lockfiles** — pinned project deps are [flake](flake.md) / [lockfile](../07-flakes/anatomy/lockfile.md) territory.
- **Not the `nix-channel` CLI reference** — flags and subcommands live on [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md).
- **Not reproducible pinning without flakes** — hash-pinned fetches and helper tools are [pinning](../06-nixpkgs/overlays-and-overrides/pinning.md).

## Examples

```bash
# Subscribe (does not download yet), then update
nix-channel --add https://channels.nixos.org/nixpkgs-unstable nixpkgs
nix-channel --update

# Use the active nixpkgs channel (default NIX_PATH / ~/.nix-defexpr layout)
nix-shell -p hello --run hello

# Explicit lookup path (overrides or supplements defaults)
export NIX_PATH=nixpkgs=$HOME/.nix-defexpr/channels/nixpkgs
nix-instantiate --eval '<nixpkgs>' -A lib.version

# One-shot override without changing the environment
nix-shell -I nixpkgs=$HOME/.nix-defexpr/channels/nixpkgs -p git --run 'git --version'

# Inspect subscriptions, generations, and roll back an update
nix-channel --list
nix-channel --list-generations
nix-channel --rollback
```

After `--update`, compare revisions before and after a rollback:

```bash
nix-instantiate --eval '<nixpkgs>' -A lib.version
nix-channel --rollback
nix-instantiate --eval '<nixpkgs>' -A lib.version
```

## References

- [Nix manual — `nix-channel`](https://nix.dev/manual/nix/stable/command-ref/nix-channel.html) — subscribe, update, rollback; channel URL layout; external-state reproducibility note
- [Nix manual — channels layout](https://nix.dev/manual/nix/stable/command-ref/files/channels.html) — channels profile paths and subscribed-channels file
- [Nix manual — `NIX_PATH`](https://nix.dev/manual/nix/stable/command-ref/common-env-vars.html#envvar-NIX_PATH) — lookup-path resolution for `<nixpkgs>`
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — locked-input alternative to channels
- [Official NixOS channels](https://channels.nixos.org/) — stable and unstable release URLs

## See also

- [Flake (concept)](flake.md) — pinned inputs and lockfiles
- [Flakes vs Channels](../comparisons/flakes-vs-channels.md) — when to use which
- [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md) — CLI surface in this wiki
- [Profile](profile.md) — generations and rollback (channels use the same idea)
- [Generation](generation.md) — numbered snapshots shared by user, system, and channels profiles
- [Garbage collection](../04-store-and-build/garbage-collection.md) — how profile generations act as GC roots
- [Pinning](../06-nixpkgs/overlays-and-overrides/pinning.md) — reproducible nixpkgs without moving channels
- [Migration from Channels](../07-flakes/migration-from-channels.md) — moving a workflow to flakes
