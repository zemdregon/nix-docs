---
status: complete
---

# Channel

## Overview

A **channel** is a named, updatable subscription to a remote set of Nix expressions—most often Nixpkgs—managed with [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md). You point a short name at a URL (typically under [channels.nixos.org](https://channels.nixos.org/)), run `nix-channel --update`, and evaluation finds the downloaded tree via `NIX_PATH` / `<nixpkgs>`.

Channels are the classic distribution mechanism. They contrast with [flakes](flake.md), which pin inputs in a lockfile: both remain relevant. Deep comparison lives in [Flakes vs Channels](../comparisons/flakes-vs-channels.md); migration in [Migration from Channels](../07-flakes/migration-from-channels.md).

## Details

**Name and URL.** A subscription pairs a name with a remote URL. The URL must serve a directory containing `nixexprs.tar.gz`; that tarball’s top-level directory provides `default.nix` as the channel entry point. Official lines include `nixpkgs-unstable` and stable NixOS release channels (`nixos-YY.MM`). `--add` only records the subscription; you must `--update` to download.

**Downloaded contents.** `--update` fetches each subscribed channel and installs a new **generation** in the channels [profile](profile.md). `--rollback` (or `--list-generations`) restores an earlier generation if an update is unwanted. Subscriptions themselves are listed in `~/.nix-channels` (or the XDG channels file when enabled).

**How evaluation finds the expressions.** After an update, channel contents appear under the channels profile (often linked from `~/.nix-defexpr/channels`). Classic tools resolve `<nixpkgs>` through `NIX_PATH` or `-I`. The channel’s current contents are **external** to any expression that imports them—Nix’s own docs note that this can limit reproducibility.

**Pinning limits.** A channel URL tracks a release line, not a single Git commit. Two machines that `--update` on different days can evaluate different revisions under the same channel name. Flakes record exact revisions in `flake.lock`; channels have no equivalent first-class lockfile (you can still pin with fetchers or other tools outside the channel model).

## Examples

```bash
# Subscribe (does not download yet), then update
nix-channel --add https://channels.nixos.org/nixpkgs-unstable nixpkgs
nix-channel --update

# Use the active nixpkgs channel
nix-shell -p hello --run hello

# Inspect and roll back
nix-channel --list
nix-channel --list-generations
nix-channel --rollback
```

## References

- [Nix manual — `nix-channel`](https://nix.dev/manual/nix/stable/command-ref/nix-channel.html) — subscribe, update, rollback; channel URL layout
- [Nix manual — channels layout](https://nix.dev/manual/nix/stable/command-ref/files/channels.html) — on-disk profiles and subscribed-channel files
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — locked-input alternative to channels
- [Official NixOS channels](https://channels.nixos.org/) — stable and unstable release URLs

## See also

- [Flake (concept)](flake.md) — pinned inputs and lockfiles
- [Flakes vs Channels](../comparisons/flakes-vs-channels.md) — when to use which
- [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md) — CLI surface in this wiki
- [Profile](profile.md) — generations and rollback (channels use the same idea)
- [Migration from Channels](../07-flakes/migration-from-channels.md) — moving a workflow to flakes
