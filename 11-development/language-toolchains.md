---
status: complete
---

# Language Toolchains

## Overview

Nixpkgs ships **language-specific builders and package sets** so compilers, interpreters, and dependency fetchers live in the store—not on an impure host. For day-to-day work, put those tools in a [dev shell](shells-and-direnv.md) (`mkShell` / flake `devShells`). For shipping packages, use the builders surveyed in [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md).

This page is a **map**: which entry points exist, how shells relate to packaging, and when community overlays are worth considering. It is not a full packaging tutorial.

## Details

### Packaging vs development

| Goal | Typical API | What you get |
|------|-------------|--------------|
| Build a package | `buildPythonPackage`, `buildGoModule`, `rustPlatform.buildRustPackage`, `buildNpmPackage`, … | Derivation with locked deps and install layout |
| Work on a project | `pkgs.mkShell` with `packages` / `nativeBuildInputs` | Compilers, linters, language servers on `PATH` |
| Ad-hoc interpreter env | e.g. `python3.withPackages (ps: [ … ])` | Scoped runtime without a full app derivation |

Both paths sit on [stdenv](../06-nixpkgs/architecture/stdenv.md). Shells do not replace builders: a shell that only exposes `cargo` still needs `buildRustPackage` (or equivalent) for reproducible CI and nixpkgs-style packaging.

**Do not rely on host toolchains** (`rustup`, system `go`, global `npm`) for anything you expect to reproduce. Impure PATH tools drift across machines; store-provided compilers keep evaluation and builds aligned with what packaging will see.

### Nixpkgs language entry points

Canonical survey: [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) in the Nixpkgs manual. Common builders:

| Ecosystem | Dev shell tools (examples) | Package builders |
|-----------|----------------------------|------------------|
| Python | `python3`, `python3Packages.…` | `buildPythonPackage` / `buildPythonApplication`, `python.withPackages` — [Python](https://nixos.org/manual/nixpkgs/stable/#python) |
| Rust | `rustc`, `cargo`, `rust-analyzer` (from nixpkgs) | `rustPlatform.buildRustPackage` — [Rust](https://nixos.org/manual/nixpkgs/stable/#rust) |
| Go | `go`, `gopls` | `buildGoModule` — [Go](https://nixos.org/manual/nixpkgs/stable/#sec-language-go) |
| Node / JS | `nodejs`, `npm` / yarn tools as needed | `buildNpmPackage` (and related hooks) — [JavaScript](https://nixos.org/manual/nixpkgs/stable/#language-javascript) |

Prefer the **same package set / platform** in the shell that packaging will use (same `python3Packages` scope, matching `rustPlatform`, versioned `go_*` when the project pins Go). Mismatched toolchains are a common “works in shell, fails in CI” failure mode.

Higher-level shell frameworks ([devenv / other wrappers](../05-cli-and-tooling/adjacent-tools/devenv-devshell.md)) still pull these same packages; they do not invent a separate language infra.

### Community Rust overlays (optional)

Nixpkgs Rust is enough for many projects. When you need **specific nightly/stable pins**, `rust-toolchain.toml` fidelity, or rust-analyzer variants outside what your nixpkgs channel ships, community overlays are common:

- [nix-community/fenix](https://github.com/nix-community/fenix) — toolchain profiles and flake-friendly packages.
- [oxalica/rust-overlay](https://github.com/oxalica/rust-overlay) — binary-distributed toolchains with a large historical archive.

Treat them as **extra inputs**, not as the default story: pin the overlay flake/input, document why nixpkgs Rust was insufficient, and keep packaging (`buildRustPackage`) on a clearly chosen `rustPlatform` or overridden toolchain. Overlay APIs change; follow their READMEs rather than copying stale blog snippets.

## Examples

Minimal `mkShell` shapes—compilers from nixpkgs only. Expand with linters/LSPs as needed; see [shells-and-direnv.md](shells-and-direnv.md) for direnv wiring.

```nix
# flake.nix (excerpt) — Python + tooling from one interpreter scope
{
  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      py = pkgs.python3.withPackages (ps: [ ps.requests ps.pytest ]);
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ py pkgs.ruff ];
      };
    };
}
```

```nix
# flake.nix (excerpt) — Rust via nixpkgs
{
  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.rustc
          pkgs.cargo
          pkgs.rustfmt
          pkgs.clippy
          pkgs.rust-analyzer
        ];
      };
    };
}
```

For actually *building* those projects as derivations, use the builders in [python-node-rust-go.md](../06-nixpkgs/packaging/python-node-rust-go.md)—shells alone do not lock Cargo/npm/Go module graphs the way those helpers do.

## References

- [Nixpkgs manual — Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support)
- [Nixpkgs manual — Python](https://nixos.org/manual/nixpkgs/stable/#python)
- [Nixpkgs manual — Rust](https://nixos.org/manual/nixpkgs/stable/#rust)
- [Nixpkgs manual — Go](https://nixos.org/manual/nixpkgs/stable/#sec-language-go)
- [Nixpkgs manual — JavaScript](https://nixos.org/manual/nixpkgs/stable/#language-javascript)
- [nix-community/fenix](https://github.com/nix-community/fenix) (community; optional)
- [oxalica/rust-overlay](https://github.com/oxalica/rust-overlay) (community; optional)

## See also

- [Shells and direnv](shells-and-direnv.md)
- [Python / Node / Rust / Go packaging](../06-nixpkgs/packaging/python-node-rust-go.md)
- [stdenv](../06-nixpkgs/architecture/stdenv.md)
- [devenv / adjacent shell tools](../05-cli-and-tooling/adjacent-tools/devenv-devshell.md)
