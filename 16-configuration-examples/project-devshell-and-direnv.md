---
status: complete
last-checked: 2026-08
---

# Project devShell and direnv

## Overview

This walkthrough is a **picture-perfect project flake**: one `devShells.<system>.default` built with `pkgs.mkShell`, plus a `.envrc` that auto-loads that shell through [direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md) and [nix-direnv](https://github.com/nix-community/nix-direnv). The same tools appear whether you run `nix develop` manually or `cd` into the tree with direnv enabled.

Pins such as `nixos-26.05` and `system = "x86_64-linux"` are illustrative—adjust for your machine. Flake workflows need experimental [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md). For shell mechanics and CLI comparison, see [shells and direnv](../11-development/shells-and-direnv.md); for flake output layout, see [packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md).

## Details

### Domains composed

| Domain | Role in this example |
|--------|----------------------|
| [Language idioms](../03-language/idioms/README.md) | `let` / attrset shape of `outputs` |
| [Garbage collection](../04-store-and-build/garbage-collection.md) | Why nix-direnv GC roots matter |
| [nix build / develop / run](../05-cli-and-tooling/modern-cli/nix-build-develop-run.md) | `nix develop` vs `nix shell` |
| [direnv / nix-direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md) | Auto-enter via `.envrc` |
| [Packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md) | `devShells.<system>.default` |
| [`nix-command` / `flakes`](../08-experimental-features/flakes.md) | Experimental features for flake shells |
| [Shells and direnv](../11-development/shells-and-direnv.md) | Teaching page this walkthrough composes |
| [Language toolchains](../11-development/language-toolchains.md) | SDKs inside `packages` |

### File layout

A minimal flake-backed dev project looks like this:

```text
my-project/
├── flake.nix          # devShells.<system>.default = pkgs.mkShell { … }
├── flake.lock         # locked nixpkgs input (commit after first eval)
├── .envrc             # use flake  (or use nix for classic shell.nix)
└── src/               # application source (optional)
```

Classic (non-flake) projects swap `flake.nix` / `flake.lock` for a single [`shell.nix`](../meta/examples/shell.nix) and use `use nix` in `.envrc`. Shared fixtures: [hello-flake/flake.nix](../meta/examples/hello-flake/flake.nix) (`use flake`) and [shell.nix](../meta/examples/shell.nix) (`use nix`) in the [example corpus](../meta/examples/README.md).

### Defining `devShells.default`

Expose the shell under the conventional flake path `devShells.<system>.default`. The value is a derivation from `pkgs.mkShell` (Nixpkgs manual: [`pkgs.mkShell`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-mkShell)):

| Attribute | Use in this walkthrough |
|-----------|-------------------------|
| `packages` | **Preferred** for executables on `$PATH` (`git`, `rustc`, linters) |
| `nativeBuildInputs` / `buildInputs` | Libraries and build-time deps when mirroring a package’s build env |
| `inputsFrom` | Pull another derivation’s build inputs into the shell |
| `shellHook` | Bash run on enter (`export`, messages)—not evaluated during normal package builds |

Put language SDKs in `packages` (or scoped wrappers like `python3.withPackages`) and link to [language toolchains](../11-development/language-toolchains.md) for ecosystem-specific shapes—this page does not repeat every language table.

The `outputs` function in `flake.nix` is ordinary Nix: `let` bindings for `system` and `pkgs`, then an attrset for `devShells` (see [03-language idioms](../03-language/idioms/README.md) for `let`/`rec` patterns). No special flake syntax beyond declaring `inputs` and returning `devShells.${system}.default`.

### Three ways to get tools (do not confuse them)

| Entry point | What it does | When to use |
|-------------|--------------|-------------|
| **`nix develop`** | Starts **bash** with the full `mkShell` / build environment (`shellHook`, stdenv, inputs) | One-off hacking, CI scripts, debugging build env |
| **`nix shell`** | Puts **already-built package** binaries on `$PATH`—no `mkShell`, no `shellHook` | Temporary “I need `hello` on PATH once” |
| **direnv + nix-direnv** | Applies the flake `devShell` (via `nix print-dev-env`) to your **current** shell on directory entry | Day-to-day work—env follows `cd` |

`nix develop` requires experimental **`nix-command`**; flake refs (`.`, `.#ci`) also need **`flakes`**. Enable both in `nix.conf` or pass `--extra-experimental-features 'nix-command flakes'`. Details: [nix build / develop / run](../05-cli-and-tooling/modern-cli/nix-build-develop-run.md).

Resolution when you omit `#name`: `nix develop` tries `devShells.<system>.default`, then `packages.<system>.default`. Named shells: `nix develop .#ci` → `devShells.<system>.ci`, then package fallbacks. See [packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md).

Classic `nix-shell` (no flakes) reads `shell.nix` or `default.nix` in the project root; see [nix-shell](../05-cli-and-tooling/classic-cli/nix-shell.md).

### direnv and nix-direnv

[direnv](https://direnv.net/) watches for `.envrc` and applies an environment diff when you enter the directory (authorized once with `direnv allow`). [nix-direnv](https://github.com/nix-community/nix-direnv) implements `use flake` and `use nix` with:

- **Caching** — after the first successful load, later visits avoid full re-evaluation when inputs are unchanged.
- **GC roots** — the shell derivation is symlinked into the user’s GC roots so its closure survives [`nix-collect-garbage`](../04-store-and-build/garbage-collection.md) between visits.

Under the hood, `use flake` calls `nix print-dev-env` on the flake’s default `devShell`—the same family as `nix develop`, but merged into your existing shell instead of spawning a subshell. Full behavior: [direnv / nix-direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md).

Install nix-direnv globally (NixOS `programs.direnv`, Home Manager, or a pinned `source_url` in `.envrc`) so project `.envrc` files can stay as short as `use flake`.

### Temporary env vs profile install

Dev shells (manual or direnv) are **directory/session-scoped**. They are not the same as `nix profile add`, which permanently links packages into a user profile. Use a shell when tools are project-pinned; use a profile only for tools you want everywhere.

### Failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `experimental feature 'nix-command' is disabled` | Modern CLI off | Enable `nix-command` (+ `flakes` for `.#`) in `nix.conf` or per command |
| `error: flake … doesn't provide attribute 'devShells.…'` | Missing or wrong `system` key | Match `system` to `nix eval --impure --expr builtins.currentSystem`; add that key under `devShells` |
| direnv: “command not found: use” / stale env | nix-direnv not loaded | Source nix-direnv’s `direnvrc` globally or pin it from `.envrc` |
| Tools vanish after GC | Shell env not rooted (stock direnv `use_flake`) | Use **nix-direnv**; it registers GC roots |
| “Works in `nix develop`, fails in CI build” | Shell tools don’t match packaging builder | Align toolchain pins; see [language toolchains](../11-development/language-toolchains.md) |
| `.envrc` blocked | Security gate | Run `direnv allow` after reviewing `.envrc` |

## Examples

**`flake.nix`** — default dev shell with `packages` and a `shellHook`. Illustrative; not evaluated in this vault. Needs `nix-command` and `flakes`:

```nix
{
  description = "my-project dev shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.git
          pkgs.gnumake
          # add language SDKs here — see language-toolchains.md in the wiki
        ];
        shellHook = ''
          echo "dev shell (${system}) — run make, git, …"
        '';
      };
    };
}
```

**`.envrc`** — auto-enter with nix-direnv (assumes nix-direnv is installed or sourced from `~/.config/direnv/direnvrc`):

```bash
use flake
```

Optional: pin nix-direnv inside the project when it is not global—see [direnv / nix-direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md).

**Activate and check:**

```bash
# one-time: lock the nixpkgs input
nix flake update   # or nix flake lock after editing inputs

# manual enter (experimental features required)
nix develop

# automatic enter (direnv + nix-direnv installed)
direnv allow
cd .               # env loads; leaving unloads

# discover outputs
nix flake show

# sanity: tools on PATH inside the shell
which git && git --version
```

**Classic alternative** — no flake; [`shell.nix`](../meta/examples/shell.nix) at repo root:

```nix
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = [ pkgs.hello pkgs.git ];
  shellHook = ''
    echo "entered classic mkShell"
  '';
}
```

```bash
# .envrc
use nix

nix-shell          # manual enter without direnv
```

**Contrast `nix shell`** (does not load this project’s `mkShell`):

```bash
nix shell nixpkgs#hello --command hello   # hello on PATH only; no shellHook
```

## References

- [Nixpkgs manual — `pkgs.mkShell`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-mkShell) — `packages`, `inputsFrom`, `shellHook`
- [Nix manual — `nix develop`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html) — devShell resolution, experimental `nix-command`
- [direnv](https://direnv.net/) — directory-scoped environment load/unload
- [nix-community/nix-direnv](https://github.com/nix-community/nix-direnv) — cached `use flake` / `use nix`, GC roots via `print-dev-env`

## See also

- [Shells and direnv](../11-development/shells-and-direnv.md) — dev shell concepts and CLI comparison
- [Packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md) — flake output layout for `devShells`
- [direnv / nix-direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md) — install, caching, GC roots
- [nix build / develop / run](../05-cli-and-tooling/modern-cli/nix-build-develop-run.md) — `nix develop` vs `nix shell` vs `nix run`
- [Language toolchains](../11-development/language-toolchains.md) — SDKs inside `mkShell`
- [Garbage collection](../04-store-and-build/garbage-collection.md) — why nix-direnv registers GC roots
- [nix-command](../08-experimental-features/nix-command.md) · [flakes](../08-experimental-features/flakes.md) — enabling experimental features
- [Example corpus](../meta/examples/README.md) — [hello-flake](../meta/examples/hello-flake/flake.nix), [shell.nix](../meta/examples/shell.nix)
