---
status: complete
---

# nix-shell

## Overview

`nix-shell` is the classic Nix CLI for starting an interactive shell with a Nix-managed environment. It has two main modes: enter the **build environment of a derivation** (dependencies built, derivation attributes exported, `stdenv` setup sourced) or, with `-p` / `--packages`, enter a lightweight environment where named Nixpkgs packages are on `PATH` and related flags are set—without evaluating a project expression.

The command remains widely used for packager debugging, shebang scripts, and legacy workflows. On current Nix, the experimental **`nix develop`** and **`nix shell`** subcommands cover most new use cases; see [nix build / develop / run](../modern-cli/nix-build-develop-run.md) for the modern equivalents.

## Details

### Derivation build environment (default mode)

Given a Nix expression path (defaulting to `shell.nix`, then `default.nix` in the current directory), `nix-shell` **builds the derivation’s dependencies but not the derivation itself**, then starts a shell where:

- Environment variables from the derivation are set.
- `$stdenv/setup` has been sourced (the same setup [stdenv](../../06-nixpkgs/architecture/stdenv.md) uses during real builds).
- `shellHook`, if defined, runs after setup—only in `nix-shell`, not in ordinary `nix-build` runs.

Select an attribute with `-A` / `--attr`, pass function arguments with `--arg` / `--argstr`, and add search paths with `-I` like other classic commands (`nix-build`, `nix-instantiate`).

This mode is the usual way to reproduce a package’s build inputs and phase helpers when debugging [build phases](../../04-store-and-build/build-phases.md).

### Package environment (`-p` / `--packages`)

With `-p`, `nix-shell` does **not** read your project’s `default.nix`. Instead it looks up attribute names (or full Nix expressions valid in a `buildInputs` list) from Nixpkgs on `NIX_PATH` / `-I` and sets up an environment containing those packages:

```bash
nix-shell -p sqlite xorg.libX11
```

Use this for ad hoc tool shells (`nix-shell -p git jq`), one-off interpreters, or quick access to a compiler toolchain. It is closer to **`nix shell -p …`** on the modern CLI than to **`nix develop`**.

`-p` accepts overrides and arbitrary expressions, not only top-level attribute names—for example `git.override { withManual = false; }`.

### `--pure` and `IN_NIX_SHELL`

By default, `nix-shell` is **impure**: your existing shell environment (locale, `PATH`, secrets in env vars) remains. `IN_NIX_SHELL` is set to `impure`.

`--pure` clears almost the entire environment before starting the shell so it more closely matches an isolated Nix build. A few variables (`HOME`, `USER`, `DISPLAY`, among others) are kept; use `--keep name` to retain additional variables under `--pure`. `IN_NIX_SHELL` becomes `pure`.

Pure mode reduces “works in my shell” drift but does **not** fully replicate the [build sandbox](../../04-store-and-build/builders-and-sandboxes.md): network policy, `$TMPDIR` behavior, and host paths outside the store closure can still differ from `nix-build`. Reproduce CI failures with the same command and flags you use in production builds when possible.

The shell binary itself comes from `NIX_BUILD_SHELL` or `<nixpkgs>`’s `bashInteractive`, not from your impure `PATH`, so `--pure` alone does not guarantee a bit-identical builder environment.

### `--run` and `--command`

Both run a command inside the `nix-shell` environment instead of dropping straight into an interactive prompt:

| Flag | Shell | Typical use |
|------|-------|-------------|
| `--run cmd` | Non-interactive | CI scripts, one-shot commands; Ctrl-C exits the shell |
| `--command cmd` | Interactive | Run setup then stay in the shell (`return` at the end prevents implicit `exit`) |

Example from the manual: export debug flags, then continue interactively:

```bash
nix-shell '<nixpkgs>' -A pan --pure \
  --command 'export NIX_DEBUG=1; export NIX_CORES=8; return'
```

For automation, prefer `--run`:

```bash
nix-shell -p nixpkgs-review --run "nixpkgs-review wip"
```

### Packager debugging with `genericBuild`

To debug an [stdenv](../../06-nixpkgs/architecture/stdenv.md) package interactively:

1. Enter the derivation’s shell: `nix-shell -A myPackage` (or `nix-shell path/to/expression.nix -A attr`).
2. Run the full phase pipeline: **`genericBuild`** (defined after sourcing setup).
3. Or run individual phase functions step by step—`unpackPhase`, `patchPhase`, `configurePhase`, `buildPhase`, etc.—in [build phase](../../04-store-and-build/build-phases.md) order.

When a phase is overridden via an environment variable (some Nixpkgs packages export `configurePhase=…`), the manual recommends:

```bash
eval ${configurePhase:-configurePhase}
```

Set `phases` temporarily to stop after a subset (for example only through `configurePhase`) when isolating failures. Combine with `nix-build -K` / `--keep-failed` when you need the partial build tree from a failed non-interactive build; see [Debugging builds](../../04-store-and-build/debugging-builds.md).

`shellHook` is useful for dev-only setup (generating code, pointing at local config) that should not run during normal store builds.

### Relation to `nix develop` and `nix shell`

These are **different commands** (`nix-shell` vs `nix shell`—note the space). Requires the [`nix-command`](../../08-experimental-features/nix-command.md) experimental feature on older installs; increasingly default on current Nix.

| Classic | Modern | Role |
|---------|--------|------|
| `nix-shell` / `nix-shell -A pkg` on a derivation | `nix develop` / `nix develop .#pkg` | Dev shell from `mkDerivation`, `mkShell`, or flake `devShell` |
| `nix-shell -p hello` | `nix shell -p hello` | Ephemeral environment with packages, no project eval |
| `nix-shell --run '…'` | `nix develop --command …` or `nix shell … --command …` | One-shot command in the environment |

Modern commands work naturally with **flakes** (`.#attr`, lockfile-pinned inputs) and share UX with `nix build` and `nix run`. `nix-shell` remains the classic interface for `NIX_PATH` / channel workflows, `#!` shebang scripts, and expressions without a `flake.nix`.

For day-to-day project shells and [direnv integration](../../11-development/shells-and-direnv.md), prefer `nix develop` on new projects; keep `nix-shell` knowledge for Nixpkgs packaging and legacy configs.

### Shebang interpreter

`nix-shell` can act as a `#!` interpreter: multiple `#! nix-shell` lines pass options (`-i`, `-p`, `-I`) so scripts pull dependencies from Nixpkgs without a separate install step. This pattern predates `nix run` and is still common in small utilities and CI snippets.

## Examples

Enter the build environment for a Nixpkgs attribute and run phases manually (realization of dependencies may substitute or build):

```bash
nix-shell '<nixpkgs>' -A hello
# inside the shell:
genericBuild   # full stdenv pipeline
# or stepwise:
eval ${unpackPhase:-unpackPhase}
cd "$sourceRoot"
eval ${buildPhase:-buildPhase}
```

Ad hoc tools without a project expression:

```bash
nix-shell -p go git
```

Pure shell with a one-shot command:

```bash
nix-shell --pure -p rustc cargo --run 'cargo test'
```

Project `shell.nix` (classic layout; modern equivalent is often a flake `devShells` + `nix develop`):

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [ nodejs python3 ];
  shellHook = ''
    echo "Dev shell ready"
  '';
}
```

```bash
nix-shell   # reads ./shell.nix
```

## References

- [Nix manual — nix-shell](https://nix.dev/manual/nix/stable/command-ref/nix-shell.html)

## See also

- [nix build / develop / run](../modern-cli/nix-build-develop-run.md) — modern CLI counterparts
- [Build phases](../../04-store-and-build/build-phases.md) — phase order and hooks used inside derivation shells
- [stdenv](../../06-nixpkgs/architecture/stdenv.md) — standard environment `nix-shell` sources for package builds
- [Debugging builds](../../04-store-and-build/debugging-builds.md) — logs, `-K`, and interactive phase debugging
- [Shells and direnv](../../11-development/shells-and-direnv.md) — project dev shells and directory loading
