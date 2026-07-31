---
status: complete
---

# nix-env

## Overview

`nix-env` is the classic CLI for managing **user environments**: mutable [profiles](../../02-concepts/profile.md) of installed packages, versioned as numbered [generations](../../02-concepts/generation.md). Install, upgrade, remove, and query operations each create a new generation from the current one; older generations stay on disk for rollback.

The command reads packages from a default Nix expression (typically `~/.nix-defexpr`, which includes subscribed [channels](../../02-concepts/channel.md) via a symlink maintained by [`nix-channel`](nix-channel.md)). For new ad hoc package management, prefer [`nix profile`](../modern-cli/nix-profile.md); `nix-env` remains common in older docs and channel-based workflows.

## Details

**One operation per invocation.** `nix-env` takes exactly one operation flag. The day-to-day set:

| Flag | Short | Operation |
|------|-------|-----------|
| `--install` | `-i` | Add packages to the active profile (new generation) |
| `--uninstall` | `-e` | Remove packages by symbolic derivation name (new generation) |
| `--upgrade` | `-u` | Replace installed paths with newer versions from the active expression |
| `--query` | `-q` | Show installed or available packages |

Generation management uses separate operations: `--list-generations`, `--switch-generation`, `--rollback`, and `--delete-generations`.

**Active profile.** By default, changes apply to the profile linked at `~/.nix-profile` (or `$XDG_STATE_HOME/nix/profile` when XDG base directories are enabled). Use `--profile` / `-p` to target another profile under the user's profiles directory. Each mutation appends a generation; the profile name symlink points at `profile-N-link`, which references an immutable store path—see [Profile](../../02-concepts/profile.md).

**Package sources.** Unless overridden, derivations come from the default Nix expression. `--file` / `-f` selects another expression (local path, `<nixpkgs>`, or an `http(s)://` tarball URL). With [channels](../../02-concepts/channel.md), [`nix-channel`](nix-channel.md) exposes subscriptions under `~/.nix-defexpr/channels`, so attributes like `nixpkgs.hello` resolve after `nix-channel --update`.

**Name vs attribute selectors.** Without `--attr`, arguments are extended regular expressions matched against the *name* part of symbolic derivation names (for example `firefox` or `firefox-32.0`). With `--attr` / `-A`, arguments are **attribute paths** into the active expression—faster and unambiguous when multiple derivations share a name. List attribute paths with:

```bash
nix-env -qaP
```

(`-q` query, `-a` available, `-P` attribute paths—the long forms are `--query --available --attr-path`.)

**Query modes.** `--query` defaults to `--installed` (packages in the current profile generation). `--available` / `-a` lists derivations from the active expression. Useful query modifiers include `--status` / `-s` (installed/present/substitute markers) and `--compare-versions` / `-c` (installed vs available).

**Upgrade semantics.** `--upgrade` builds a new generation; paths with no newer match are left unchanged (not an error). Version comparison flags include `--lt` (default), `--leq`, `--eq`, and `--always`. Attribute-path upgrades are typical on channel setups, e.g. `nix-env -uA nixpkgs.gcc`.

**Shared profile layout with `nix profile`.** Both tools manage profiles under the same on-disk layout. `nix-env` records state in `manifest.nix`; `nix profile` uses `manifest.json`. You can mix tools on the same profile, but sticking to one CLI per workflow avoids surprises.

## Examples

Channel-based install and query (needs a channel / nixpkgs on `NIX_PATH`; may substitute or build):

```bash
nix-channel --update
nix-env -iA nixpkgs.hello
nix-env -q hello          # installed
nix-env -qa '.*vim.*'     # search available names
nix-env -qaP | grep hello # attribute paths for -A
```

Upgrade and remove:

```bash
nix-env -u firefox        # by name regex
nix-env -uA nixpkgs.firefox
nix-env -e firefox        # uninstall by name
```

Generations:

```bash
nix-env --list-generations
nix-env --rollback
nix-env --switch-generation 42
```

Inspect without changing state:

```bash
nix-env -iA nixpkgs.hello --dry-run
```

## References

- [Nix manual — `nix-env`](https://nix.dev/manual/nix/stable/command-ref/nix-env.html)

## See also

- [`nix profile`](../modern-cli/nix-profile.md) — modern profile management
- [Profile](../../02-concepts/profile.md) — symlink farms and GC roots
- [Generation](../../02-concepts/generation.md) — numbered snapshots and rollback
- [Channel](../../02-concepts/channel.md) — classic nixpkgs distribution
- [`nix-channel`](nix-channel.md) — subscribe and update channel snapshots
