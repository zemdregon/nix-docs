---
status: complete
---

# nix-channel

## Overview

`nix-channel` is the classic CLI for subscribing to remote Nix expression trees—most often [Nixpkgs](https://nixos.org/manual/nixpkgs/stable/) and NixOS release lines hosted at [channels.nixos.org](https://channels.nixos.org/). You **add** a name/URL pair, **update** to download the latest snapshot, and tools resolve packages through `NIX_PATH` or `<nixpkgs>` imports.

Channel state lives outside your project files, so two machines with the same config can evaluate different nixpkgs revisions after different `--update` runs. For pinned, reproducible inputs, see [Migration from channels](../../07-flakes/migration-from-channels.md) and [Pinning](../../06-nixpkgs/overlays-and-overrides/pinning.md). The [Channel](../../02-concepts/channel.md) concept page explains the distribution model; this page covers the command.

## Details

**Core operations.**

| Flag | Effect |
|------|--------|
| `--add url [name]` | Register a subscription. If `name` is omitted, Nix derives it from the URL (dropping a trailing `-stable` or `-unstable`). Does **not** download; run `--update` separately. |
| `--remove name` | Unsubscribe from `name`. |
| `--list` | Print subscribed channels as `name url` lines on stdout. |
| `--update [names…]` | Fetch tarballs for all channels (or only the names given) and create a new **generation** in the channels profile. |

Additional flags: `--list-generations` shows update history; `--rollback [generation]` restores the previous generation (same mechanism as [`nix-env`](nix-env.md) profile rollbacks on the channels profile).

**What a channel URL must provide.** The URL points at a directory containing `nixexprs.tar.gz`. That tarball unpacks to a single top-level directory with a `default.nix` entry point—the layout Hydra publishes for official channels.

**On-disk layout.** Subscriptions are recorded in `~/.nix-channels` (or `$XDG_STATE_HOME/nix/channels` when `use-xdg-base-directories` is enabled), one `url name` per line. After `--update`, symlinks under the channels profile (for example `$XDG_STATE_HOME/nix/profiles/channels`) expose each channel; legacy workflows also see `~/.nix-defexpr/channels/<name>`.

**Official channels.** Release lines are listed at [channels.nixos.org](https://channels.nixos.org/). Common subscriptions:

- `https://channels.nixos.org/nixpkgs-unstable` — rolling Nixpkgs (typical on non-NixOS systems)
- `https://channels.nixos.org/nixos-26.05` — stable NixOS release line (use the current YY.MM for your deployment)
- `https://channels.nixos.org/nixpkgs` — stable Nixpkgs aligned with the current NixOS stable branch

Do not treat arbitrary URL suffixes as official channels; stick to names published on channels.nixos.org.

**NIX_PATH and lookup.** After an update, evaluation resolves `<nixpkgs>` and similar lookup paths from the channels profile unless overridden. Set `NIX_PATH` explicitly, for example `nixpkgs=/path/to/nixpkgs:nixos=/path/to/nixos`, or pass `-I nixpkgs=…` per invocation; `-I` entries take precedence over `NIX_PATH`. An empty `NIX_PATH` disables search-path resolution. Channel-based lookup is **impure** relative to flakes: the exact revision depends on when you last ran `--update`, not on a lockfile in your repo.

**Per-user scope.** `nix-channel` is per Unix user. A non-root user's subscriptions do not change what root's `nixos-rebuild` sees; system upgrades on NixOS typically require `sudo nix-channel …` for the `nixos` channel.

**Caching.** Downloaded channel tarballs are cached; validity follows `tarball-ttl` (CLI flag or `nix.conf` setting).

**Relationship to flakes.** Flakes replace implicit `NIX_PATH` / `<nixpkgs>` with explicit `inputs` and a committed `flake.lock`. You can keep channel subscriptions for ad hoc [`nix-shell`](nix-shell.md) or legacy [`nix-env`](nix-env.md) while migrating projects to flakes; the flake lockfile becomes the source of truth for that repo. See [Migration from channels](../../07-flakes/migration-from-channels.md) for the step-by-step path and [Pinning](../../06-nixpkgs/overlays-and-overrides/pinning.md) when you need commit-level reproducibility without full flakes.

## Examples

Subscribe to unstable Nixpkgs, update, and use the channel in a shell:

```bash
nix-channel --add https://channels.nixos.org/nixpkgs-unstable nixpkgs
nix-channel --update
nix-shell -p hello --run hello
```

Inspect and remove a subscription:

```bash
nix-channel --list
# nixpkgs https://channels.nixos.org/nixpkgs-unstable

nix-channel --remove nixpkgs
```

Stable NixOS channel (run as root for system configuration):

```bash
sudo nix-channel --add https://channels.nixos.org/nixos-26.05 nixos
sudo nix-channel --update nixos
```

Rollback after a bad update:

```bash
nix-channel --list-generations
nix-channel --rollback
```

## References

- [Nix manual — `nix-channel`](https://nix.dev/manual/nix/stable/command-ref/nix-channel.html) — flags, files, and examples
- [Nix manual — channels layout](https://nix.dev/manual/nix/stable/command-ref/files/channels.html) — profiles and subscription files
- [Official NixOS channels](https://channels.nixos.org/) — stable and unstable release URLs

## See also

- [Channel](../../02-concepts/channel.md) — what channels are and how they differ from flakes
- [Migration from channels](../../07-flakes/migration-from-channels.md) — moving to flake inputs and lockfiles
- [Pinning](../../06-nixpkgs/overlays-and-overrides/pinning.md) — commit-level nixpkgs without floating channel HEAD
- [`nix-env`](nix-env.md) — classic profile installs from channel-resolved nixpkgs
