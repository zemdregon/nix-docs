---
status: complete
---

# direnv / nix-direnv

## Overview

[direnv](https://direnv.net/) loads and unloads environment variables when you enter or leave a directory, driven by a project `.envrc` (authorized once with `direnv allow`). [nix-direnv](https://github.com/nix-community/nix-direnv) replaces direnv’s built-in `use_nix` / `use_flake` with a **faster, cached** implementation that also keeps **GC roots** for the shell derivation so dependencies are not garbage-collected between visits.

Together they complement [`nix develop`](../modern-cli/nix-build-develop-run.md) and classic `nix-shell`: instead of manually entering a shell each time, cd’ing into the project activates the same kind of environment. Flake-based `devShells` plus `use flake` is a common workflow.

## Details

### direnv

- Hooks into bash, zsh, fish, and other shells; before each prompt it looks for `.envrc` (and optionally `.env`) in the current or parent directories.
- Runs `.envrc` in a bash subshell and applies only the **exported environment diff** to your interactive shell (aliases/functions are not imported).
- Security: a new or changed `.envrc` must be allowed (`direnv allow`) before it loads.
- Provides a stdlib (`use_nix`, `use_flake`, `PATH_add`, …). Stock `use_nix` / `use_flake` re-evaluate more often and do not persist GC roots the way nix-direnv does.

### nix-direnv

Requires a working direnv install (it is not a substitute for direnv), bash ≥ 4.4, **Nix ≥ 2.4**, and **direnv ≥ 2.21.3** (upstream README, verified 2026-07; latest release tag **3.2.0**).

Notable behavior:

- **Caches** the evaluated shell environment after the first successful load, so later directory entries avoid full re-evaluation when inputs are unchanged.
- **Symlinks** the shell derivation into the user’s GC roots so build dependencies survive `nix-collect-garbage` while the project is in use.
- **`use flake`** is implemented via `nix print-dev-env` (same family as `nix develop`). Default is the flake’s `devShells.<system>.default`; you can pass a flake ref and extra flags (e.g. `use flake . --impure`).
- **`use nix`** targets `shell.nix` / `default.nix` (or an explicit file argument) and likewise uses `nix print-dev-env` under the hood.
- Watches common inputs automatically (`flake.nix` / `flake.lock` for flakes; the nix file for `use nix`) so edits trigger a reload.

Install options include Home Manager (`programs.direnv.nix-direnv.enable`), NixOS `programs.direnv`, sourcing nix-direnv’s `direnvrc` from `~/.config/direnv/direnvrc`, or `source_url` of a pinned `direnvrc` inside `.envrc`. Prefer installing nix-direnv system-wide or via Home Manager so every project’s `.envrc` can stay as simple as `use flake`.

### Relation to `nix develop`

`nix develop` starts an interactive bash with the package/devShell build environment on demand. direnv + nix-direnv apply that environment (or its equivalent via `print-dev-env`) to your **existing** shell when you enter the directory. Use `nix develop` for one-off or phase-oriented work; use direnv when you want the project env always on after `cd`.

## Examples

**Minimal flake project** (nix-direnv already sourced from your direnvrc):

```bash
# .envrc
use flake
```

```bash
direnv allow
# enter/leave the directory → env loads/unloads
```

**Classic `shell.nix`:**

```bash
# .envrc
use nix
```

**Pin nix-direnv from `.envrc`** (when not installed globally)—version and hash must match a released tag:

```bash
if ! has nix_direnv_version || ! nix_direnv_version 3.2.0; then
  source_url "https://raw.githubusercontent.com/nix-community/nix-direnv/3.2.0/direnvrc" \
    "sha256-hW6NC1JHue3IjZN3uDM6l6I2PMaauqd2D7hXYJ1Zfr4="
fi
use flake
```

**Explicit flake / impure:**

```bash
use flake ~/myflakes#project
# or
use flake . --impure
```

## References

- [direnv](https://direnv.net/) — project site and getting started
- [nix-community/nix-direnv](https://github.com/nix-community/nix-direnv) — README: cached `use_nix` / `use_flake`, GC roots, install methods; release **3.2.0** `source_url` example (verified 2026-07)
- [Nix manual — `nix develop`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html) — interactive build/devShell environment (related to `print-dev-env`; experimental `nix-command`)

## See also

- [Shells and direnv](../../11-development/shells-and-direnv.md) — development-oriented overview of shells + direnv
- [nix build / develop / run](../modern-cli/nix-build-develop-run.md) — `nix develop` and related installable commands
- [devenv / devshell](devenv-devshell.md) — higher-level project shell tooling
- [Packages, apps, devShells](../../07-flakes/workflows/packages-apps-devShells.md) — flake `devShells` outputs used by `use flake`
