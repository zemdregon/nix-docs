---
status: complete
---

# Packages, Apps, devShells

## Overview

Most day-to-day flake work is exposing three conventional **output families** for each supported **system** (e.g. `x86_64-linux`): **`packages`**, **`apps`**, and **`devShells`**. Packages are [derivations](../../02-concepts/derivation.md) you build with `nix build`; apps are lightweight runnable definitions for `nix run`; dev shells are environment derivations you enter with `nix develop`.

Flake installables and these subcommands are still **experimental** (Nix stable manual as of 2026): they need the [`flakes`](../../08-experimental-features/flakes.md) and [`nix-command`](../../08-experimental-features/nix-command.md) features. Enable both in `nix.conf` (`experimental-features = nix-command flakes`) or per invocation with `--extra-experimental-features 'nix-command flakes'`. Command flags and defaults can still change between releases.

This page is the **workflow**—what to expose, how the CLI picks defaults, and how to sanity-check outputs. Installable syntax and flags live in [nix build / develop / run](../../05-cli-and-tooling/modern-cli/nix-build-develop-run.md). How inputs wire into those attrsets lives in [inputs and outputs](../anatomy/inputs-and-outputs.md) and the [flake.nix schema](../anatomy/flake-nix-schema.md). For the broader [flake](../../02-concepts/flake.md) model, start with the concept page. Shell contents (`mkShell`, direnv) are covered in [shells and direnv](../../11-development/shells-and-direnv.md).

## Details

### Conventional output paths

Nix 3 commands expect flake outputs under fixed attribute paths:

| Output family | Attribute shape | Primary CLI |
|---------------|-----------------|-------------|
| Package | `packages.<system>.<name>` | `nix build .#<name>` |
| App | `apps.<system>.<name>` | `nix run .#<name>` |
| Dev shell | `devShells.<system>.<name>` | `nix develop .#<name>` |

Each value under `packages` and `devShells` must be a **derivation**. Each value under `apps` must be an **app definition**: an attrset with `type = "app"` and `program` set to a store path of an executable (often `${pkg}/bin/<name>`). The only optional app field documented by the Nix manual is `meta.description`.

### Default and named resolution

When you omit `#<name>`, each command tries a short list for the **current system**:

| Command | Lookup order (no `#name`) |
|---------|---------------------------|
| `nix build` | `packages.<system>.default` |
| `nix run` | `apps.<system>.default`, then `packages.<system>.default` |
| `nix develop` | `devShells.<system>.default`, then `packages.<system>.default` |

With a name (`.#foo`), `nix run` tries `apps`, then `packages`, then `legacyPackages`; `nix develop` tries `devShells`, then `packages`, then `legacyPackages`. For `nix build` and most other installables, a named attr is searched under `packages.<system>`, `legacyPackages.<system>`, and as a bare top-level path. Prefer an explicit `default` under the plural conventional paths so bare `nix build` / `nix run` / `nix develop` behave predictably.

An attrpath that starts with `.` skips those prefixes entirely (e.g. `.#.packages.x86_64-linux.hello`), which is useful when you need a non-default path without the packages/legacyPackages search.

### Running packages without apps

If `nix run` resolves to a derivation rather than an app, it executes `$out/bin/<name>` using the first of `meta.mainProgram`, `pname`, or the name component of `name` (e.g. `hello-2.12` → `hello`). An `apps` entry is only needed when you want a different executable path or a clear `nix run` default separate from the package. Pass program arguments after `--` (e.g. `nix run . -- --help`).

### `self` and inputs

The `outputs` function receives each declared input plus **`self`** (this flake’s own outputs and source tree). Typical patterns:

- **`nixpkgs.legacyPackages.<system>`** (or `import nixpkgs { inherit system; }`) for packaged tools and `mkShell`.
- **`self.packages.<system>.<name>`** when an app’s `program`, a check, or a shell should refer to a package defined in the same flake—avoid duplicating the derivation expression.
- **`self.outPath` / `self.rev`** when you need this flake’s source or lock metadata inside a derivation.

Keep packages as the source of truth; point apps and shells at them via `self` rather than rebuilding the same attr twice. See [inputs and outputs](../anatomy/inputs-and-outputs.md) for `follows`, non-flake inputs, and registry indirection.

### Systems are explicit

Flake outputs are **not** auto-parameterized by system. You list each supported system in the attrset (e.g. `packages.x86_64-linux.default = …`). A small raw flake with one or two hard-coded systems is enough for many projects and matches what `nix flake show` displays.

When you need several systems without repeating bodies, fold over a list with `nixpkgs.lib.genAttrs` (or equivalent). Optional helpers such as **flake-utils** (`eachDefaultSystem`) or a **nix-systems** input that supplies the system list are common in the wild—they are conveniences, not requirements. Prefer whatever keeps the flake readable for your team; do not treat a particular framework as part of the flake schema.

### Typical sources

Packages usually come from `nixpkgs.legacyPackages.<system>` (after declaring `nixpkgs` as an input) or from custom `pkgs.mkDerivation` / language helpers in `outputs`. Dev shells are commonly `pkgs.mkShell { … }` with `packages` / `buildInputs` / `nativeBuildInputs` and optional `shellHook`—details in [shells and direnv](../../11-development/shells-and-direnv.md). Apps wrap an already-built program path; they do not replace a package—they tell `nix run` which executable to invoke.

### Validation and discovery

`nix flake check` evaluates packages and `devShells` as derivations and apps as app definitions. It is the quick CI-friendly pass before publishing; related CI-oriented outputs live in [checks and hydraJobs](checks-and-hydraJobs.md). Legacy output names (`defaultPackage.<system>`, `defaultApps.<system>`, `devShell.<system>`) still work but emit **warnings**—prefer the plural conventional paths above.

`nix flake show` lists available packages, apps, and dev shells per system. Use it after adding outputs to confirm attribute paths before documenting them in a README or template.

## Examples

**Minimal raw flake** exposing a default package, a runnable app, and a dev shell (single system; no framework):

```nix
{
  description = "hello package, app, and dev shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.${system}.default = pkgs.hello;

      apps.${system}.default = {
        type = "app";
        program = "${self.packages.${system}.default}/bin/hello";
        meta.description = "GNU Hello";
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [ self.packages.${system}.default ];
      };
    };
}
```

**Multi-system without a framework** (same bodies via `genAttrs`; add or drop systems in one place):

```nix
outputs = { self, nixpkgs }:
  let
    systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" ];
    forAllSystems = nixpkgs.lib.genAttrs systems;
  in {
    packages = forAllSystems (system: {
      default = nixpkgs.legacyPackages.${system}.hello;
    });
    # apps / devShells likewise: forAllSystems (system: { default = …; })
  };
```

**CLI usage** (from the flake directory, on a listed system, with `nix-command` and `flakes` enabled):

```bash
nix build          # packages.<system>.default → ./result
nix run            # apps.…default, else packages.…default
nix run . -- arg   # pass args to the program after --
nix develop        # devShells.…default, else packages.…default
nix flake check    # verifies derivations and app defs
nix flake show     # lists packages / apps / devShells
```

**Multiple named outputs:** add `packages.<system>.cli = …` and build with `nix build .#cli`. The app’s `program` can reference any package output via `self`, not only `default`.

Shared fixture (packages + devShell only): [hello-flake/flake.nix](../../meta/examples/hello-flake/flake.nix) in the [example corpus](../../meta/examples/README.md).

## References


- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — flake format and conventional output attributes
- [Nix manual — Installables](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html#installables) — default and prefixed attr lookup for flake outputs
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — validation of packages, apps, and dev shells (experimental)
- [Nix manual — `nix build`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-build.html) — building flake package outputs (experimental)
- [Nix manual — `nix run`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-run.html) — apps, package fallback, `mainProgram` (experimental)
- [Nix manual — `nix develop`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html) — entering flake dev shells (experimental)
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — high-level introduction
- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — `flakes` / `nix-command` flags

## See also

- [nix build / develop / run](../../05-cli-and-tooling/modern-cli/nix-build-develop-run.md) — installables, flags, and CLI comparison
- [Inputs and outputs](../anatomy/inputs-and-outputs.md) — how `outputs` receives inputs and `self`
- [checks and hydraJobs](checks-and-hydraJobs.md) — other flake output families for CI
- [shells and direnv](../../11-development/shells-and-direnv.md) — `mkShell`, shell contents, direnv
- [flakes (experimental feature)](../../08-experimental-features/flakes.md) — enabling the feature flag
- [flake.nix schema](../anatomy/flake-nix-schema.md) — required keys and output layout
