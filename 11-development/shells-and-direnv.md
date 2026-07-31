---
status: complete
---

# Shells and direnv

## Overview

A **dev shell** is a temporary environment with the compilers, libraries, and tools a project needs—without installing them into your user profile. Nixpkgs provides `pkgs.mkShell` (and `pkgs.mkShellNoCC` when no C compiler is required). You enter that environment with classic [`nix-shell`](../05-cli-and-tooling/classic-cli/nix-shell.md) or the experimental [`nix develop`](../05-cli-and-tooling/modern-cli/nix-build-develop-run.md) command. Flakes expose shells under `devShells.<system>.<name>` (usually `default`).

[direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md) plus [nix-direnv](https://github.com/nix-community/nix-direnv) load the same kind of environment automatically when you `cd` into the project, instead of typing `nix develop` each time. That is still a **session/directory-scoped** env—not a permanent profile install.

Three easy-to-confuse entry points:

| Command | Role |
|---------|------|
| `nix develop` / `nix-shell` | Enter a **dev shell** (`mkShell` / `devShells`) with build inputs and optional `shellHook` |
| `nix shell` | Put already-built **packages** on `$PATH` for one command or subshell—no `mkShell` setup |
| direnv + nix-direnv | Auto-load a flake `devShell` (`use flake`) or classic `shell.nix` (`use nix`) into the current shell |

## Details

### Defining the shell

`pkgs.mkShell` is a specialized `stdenv.mkDerivation` aimed at interactive use with `nix-shell` / `nix develop`. Common attributes (Nixpkgs manual):

| Attribute | Role |
|-----------|------|
| `packages` | Executable packages put on `$PATH` in the shell (preferred over listing them only in `buildInputs`) |
| `inputsFrom` | Pull build dependencies of the listed derivations into the shell |
| `shellHook` | Bash statements run by `nix-shell` / `nix develop` after `$stdenv/setup` (not during normal package builds) |
| `nativeBuildInputs` / `buildInputs` | Inherited `stdenv` attrs; still used for toolchains and libraries, especially when matching a package’s build env |

`pkgs.mkShellNoCC` uses `stdenvNoCC` instead of `stdenv`, so you avoid pulling a C compiler when the project does not need one.

Language-specific SDKs and wrappers belong in [language toolchains](language-toolchains.md); this page covers the shell container around them.

### Entering the shell

- **Flakes:** put an `mkShell` derivation at `devShells.<system>.default` (or a named attr). With no attribute, `nix develop` tries `devShells.<system>.default`, then `packages.<system>.default`. With a name (e.g. `nix develop .#ci`), it tries `devShells.<system>.<name>`, then `packages.<system>.<name>`, then `legacyPackages.<system>.<name>`. See [packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md).
- **Classic:** `shell.nix` (or `default.nix`) evaluating to an `mkShell` / derivation; run `nix-shell`. Defaults to `shell.nix` if present, else `default.nix`. `nix-shell -p …` is a quick one-off package set without a file.
- **`nix develop` is experimental** (Nix stable manual as of 2026: requires `nix-command`; flake refs also need `flakes`). It starts bash with an environment nearly identical to building the installable. Optional `--profile` records that env into a profile for later reuse; without that, leaving the shell drops the env.

### Temporary env vs profile install

| Approach | Lifetime | Typical command |
|----------|----------|-----------------|
| Dev shell | Until you exit / leave the directory | `nix develop`, `nix-shell`, direnv unload |
| Profile install | Until you uninstall | `nix profile add`, classic `nix-env -iA` |

Use a shell when tools are project-local or version-pinned with the repo. Install to a profile only for tools you want on `$PATH` everywhere. Higher-level wrappers such as [devenv / devshell](../05-cli-and-tooling/adjacent-tools/devenv-devshell.md) still sit on the same temporary-env idea.

### Automatic enter with direnv

With direnv and nix-direnv configured, a project `.envrc` containing `use flake` (or `use nix`) applies the flake `devShell` / `shell.nix` env to your **current** interactive shell on directory entry. nix-direnv implements these via `nix print-dev-env` (same family as `nix develop`), with caching and GC roots so dependencies survive garbage collection between visits. Details: [direnv / nix-direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md).

## Examples

**Minimal flake** with a default `mkShell`. Illustrative—`nixpkgs` pin and `system` must match your machine; needs experimental `nix-command` and `flakes`. Not evaluated in this vault:

```nix
{
  description = "dev shell example";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ pkgs.hello pkgs.git ];
        shellHook = ''
          echo "entered ${system} dev shell"
        '';
      };
    };
}
```

```bash
# needs experimental features: nix-command flakes
nix develop          # enters devShells.<system>.default
# or with direnv + nix-direnv already installed:
# echo 'use flake' > .envrc && direnv allow
```

**Classic `shell.nix`** (attrs match the Nixpkgs `mkShell` example; enter with `nix-shell`). Illustrative—needs a working `<nixpkgs>` channel or pin:

```nix
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = [ pkgs.gnumake ];
  inputsFrom = [ pkgs.hello ];
  shellHook = ''
    export DEBUG=1
  '';
}
```

Shared fixtures: classic [shell.nix](../meta/examples/shell.nix) (`use nix`) and flake [hello-flake/flake.nix](../meta/examples/hello-flake/flake.nix) (`use flake`) in the [example corpus](../meta/examples/README.md).

## References


- [Nixpkgs manual — `pkgs.mkShell`](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-mkShell) — `packages`, `inputsFrom`, `shellHook`, `mkShellNoCC`
- [Nix manual — `nix develop`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html) — flake `devShells` resolution, `--profile`, experimental `nix-command`
- [Nix manual — `nix-shell`](https://nix.dev/manual/nix/stable/command-ref/nix-shell.html) — classic interactive shell, `shellHook`, `-p`
- [direnv](https://direnv.net/) — directory-scoped env load/unload
- [nix-community/nix-direnv](https://github.com/nix-community/nix-direnv) — cached `use nix` / `use flake` via `nix print-dev-env`, GC roots

## See also

- [direnv / nix-direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md) — automatic project env load/unload
- [devenv / devshell](../05-cli-and-tooling/adjacent-tools/devenv-devshell.md) — higher-level shell tooling
- [nix build / develop / run](../05-cli-and-tooling/modern-cli/nix-build-develop-run.md) — CLI entry points for installables
- [nix-shell](../05-cli-and-tooling/classic-cli/nix-shell.md) — classic interactive shell
- [Packages, apps, devShells](../07-flakes/workflows/packages-apps-devShells.md) — flake output layout for shells
- [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md) — persistent profile installs (vs temporary shells)
- [Language toolchains](language-toolchains.md) — language SDKs inside a shell
