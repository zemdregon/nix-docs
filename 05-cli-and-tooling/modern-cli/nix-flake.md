---
status: complete
---

# nix flake

## Overview

**`nix flake`** is the Nix 3 CLI subtree for creating, inspecting, locking, and fetching [flakes](../../07-flakes/README.md). Subcommands operate on **flake references** (flakerefs) such as `.`, `github:NixOS/nixpkgs`, or registry ids like `nixpkgs`; see [Registries and refs](../../07-flakes/registries-and-refs.md) for URL forms and `#output` selection.

The command tree is part of the unified [`nix`](../../08-experimental-features/nix-command.md) entry point and remains **experimental** (Nix stable manual, 2026): subcommand names, flags, and output formats can change between releases. Enable both **`nix-command`** and **`flakes`** in `nix.conf` or pass `--extra-experimental-features 'nix-command flakes'`. Schema, inputs/outputs, and lockfile semantics live under [07-flakes](../../07-flakes/README.md)—this page covers the CLI surface only. To build, run, or enter dev shells from flake outputs, see [`nix build` / `develop` / `run`](nix-build-develop-run.md).

## Details

Most subcommands take a **flakeref** argument (default `.` for the current directory when omitted). Several support **`--json`** for machine-readable output. Lockfile-related commands share flags such as `--commit-lock-file`, `--override-input`, and `--no-write-lock-file`; see the manual for the full set.

**`lock` vs `update`.** [`nix flake lock`](#lock) adds missing lock entries without changing existing ones. [`nix flake update`](#update) refreshes locked revisions—by default **all** inputs when no names are given.

### Subcommands

| Subcommand | Purpose |
|------------|---------|
| [`show`](#show) | Print the flake's `outputs` tree (packages, checks, overlays, …) |
| [`metadata`](#metadata) | Resolve a flakeref, fetch it, and print metadata (URL, revision, inputs, store path) |
| [`info`](#metadata) | Alias for `metadata` |
| [`check`](#check) | Verify the flake evaluates and build its `checks` (and validate output types) |
| [`lock`](#lock) | Create or extend `flake.lock` with entries for every input in `flake.nix` |
| [`update`](#update) | Update one or more named inputs (or all) in `flake.lock` |
| [`init`](#init) | Scaffold a flake in the current directory from a template |
| [`new`](#new) | Create a new directory and run `init` there |
| [`clone`](#clone) | Git or Mercurial clone of the repository behind a flakeref |
| [`prefetch`](#prefetch) | Fetch the source tree for a flakeref into the store (need not be a flake) |
| [`prefetch-inputs`](#prefetch-inputs) | Recursively fetch a flake’s inputs (and transitive inputs) into the store |
| [`archive`](#archive) | Copy a flake and all its inputs to a store (local or remote) |

#### show

Lists top-level attributes from the flake's `outputs`, with nested detail for standard outputs (`packages`, `checks`, `devShells`, …). Useful for discovering `#attr` paths before `nix build` or `nix run`.

```bash
nix flake show .
nix flake show nixpkgs --legacy    # include legacyPackages
nix flake show . --json
```

#### metadata

Resolves the flakeref (via registries when indirect), fetches the locked source, and prints resolved/locked URLs, description, store path, revision, last-modified time, and the input tree. With `--json`, includes the full `flake.lock` contents under `locks`.

```bash
nix flake metadata dwarffs
nix flake metadata . --json | jq .path
```

#### check

Evaluates the flake and, unless `--no-build` is set, builds derivations under `checks.<system>`. Also type-checks standard outputs (`packages`, `devShells`, `apps`, `overlays`, `nixosModules`, …). Common in CI (`nix flake check` in the project root).

```bash
nix flake check
nix flake check --no-build github:NixOS/patchelf
```

#### lock

Updates `flake.lock` so every input declared in `flake.nix` has a lock entry. Existing entries that are already up to date are left unchanged—use `update` to bump revisions.

```bash
nix flake lock
nix flake lock ./my-project
```

#### update

Operates on the flake in the current directory by default; pass **`--flake`** for another path. With no input names, updates **all** inputs (equivalent to recreating the lock from scratch). Name one or more inputs to update only those.

```bash
nix flake update
nix flake update nixpkgs
nix flake update nixpkgs --flake ~/repos/my-flake
```

#### init

Copies a [template](../../07-flakes/workflows/templates.md) into the current directory without overwriting existing files. Default template is `templates#templates.default`; list choices with `nix flake show templates`. Select with `-t` / `--template`.

```bash
nix flake init
nix flake init -t templates#simpleContainer
```

#### new

Creates **`dest-dir`** (must not exist), then runs `init` inside it.

```bash
nix flake new hello
nix flake new hello -t templates#trivial
```

#### clone

Clones the Git or Mercurial repository for a flakeref into **`--dest`** / `-f` (required destination path).

```bash
nix flake clone dwarffs --dest dwarffs
```

#### prefetch

Downloads and unpacks the source denoted by a flakeref into the Nix store. The target need not contain `flake.nix`. `--json` returns `hash` and `storePath`; `-o` creates an out-link symlink.

```bash
nix flake prefetch dwarffs --json
nix flake prefetch https://example.com/src.tar.xz -o ./src
```

#### prefetch-inputs

Fetches the flake’s inputs (recursively, including transitive inputs) so they are already in the store for later evaluation. Useful before offline or remote work that must not hit the network for input fetches.

```bash
nix flake prefetch-inputs .
```

#### archive

Fetches the flake and **transitive inputs** into a store—local by default, or another store with **`--to`** (e.g. `file:///tmp/cache`, `ssh://host`). `--dry-run --json` lists store paths without copying. Used for offline evaluation or seeding a remote builder.

```bash
nix flake archive .
nix flake archive --to file:///tmp/my-cache dwarffs
```

## Examples

Typical workflow in a new or existing repository:

```bash
# Enable once in nix.conf: experimental-features = nix-command flakes

nix flake init                          # or: nix flake new myproj && cd myproj
nix flake lock                          # create flake.lock for declared inputs
nix flake show .                        # discover packages.checks.devShells
nix flake check                         # CI-style evaluate + build checks
nix flake update nixpkgs                # bump one input
```

Inspect a remote flake without cloning:

```bash
nix flake metadata nixpkgs
nix flake show nixpkgs
```

## See also

- [flake.nix schema](../../07-flakes/anatomy/flake-nix-schema.md) — inputs, outputs, and on-disk format
- [Lockfile](../../07-flakes/anatomy/lockfile.md) — `flake.lock` graph and locking semantics
- [Registries and refs](../../07-flakes/registries-and-refs.md) — flakeref syntax and registry resolution
- [flakes (experimental feature)](../../08-experimental-features/flakes.md) — enabling the flakes flag
- [nix-command (experimental feature)](../../08-experimental-features/nix-command.md) — unified CLI prerequisite
- [nix build / develop / run](nix-build-develop-run.md) — build and run flake outputs

## References

- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) (stable; experimental interface)
- [Nix manual — new CLI overview](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html)
- [`nix flake show`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-show.html)
- [`nix flake metadata`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-metadata.html)
- [`nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html)
- [`nix flake lock`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-lock.html)
- [`nix flake update`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-update.html)
- [`nix flake init`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-init.html)
- [`nix flake new`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-new.html)
- [`nix flake clone`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-clone.html)
- [`nix flake prefetch`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-prefetch.html)
- [`nix flake prefetch-inputs`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-prefetch-inputs.html)
- [`nix flake archive`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-archive.html)
