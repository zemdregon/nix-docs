---
status: complete
last-checked: 2026-08
---

# Language Toolchains

## Overview

Nixpkgs ships **language-specific builders and package sets** so compilers, interpreters, and dependency fetchers live in the store—not on an impure host. For day-to-day work, put those tools in a [dev shell](shells-and-direnv.md) (`mkShell` / flake `devShells`). For shipping packages, use the packaging leaves under [06-nixpkgs/packaging](../06-nixpkgs/packaging/README.md).

This page is a **map**: which entry points exist, how shells relate to packaging, and when community overlays are worth considering. It is **not** a packaging tutorial—builders, FODs, and set-specific knobs live on the packaging pages linked below.

## Details

### Packaging vs development

| Goal | Typical API | What you get |
|------|-------------|--------------|
| Build a package | `buildPythonPackage`, `buildGoModule`, `rustPlatform.buildRustPackage`, `haskellPackages.mkDerivation`, `php.buildComposerProject2`, … | Derivation with locked deps and install layout |
| Work on a project | `pkgs.mkShell` with `packages` / `nativeBuildInputs` | Compilers, linters, language servers on `PATH` |
| Ad-hoc interpreter env | e.g. `python3.withPackages`, `haskellPackages.ghcWithPackages` | Scoped runtime without a full app derivation |

Both paths sit on [stdenv](../06-nixpkgs/architecture/stdenv.md). Shells do not replace builders: a shell that only exposes `cargo` still needs `buildRustPackage` (or equivalent) for reproducible CI and nixpkgs-style packaging.

### Nixpkgs language entry points

Canonical survey: [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) in the Nixpkgs manual. Common builders (shell tools vs packaging):

| Ecosystem | Dev shell tools (examples) | Package builders |
|-----------|----------------------------|------------------|
| Python | `python3`, `python3Packages.…` | `buildPythonPackage` / `buildPythonApplication`, `python.withPackages` — [Python](https://nixos.org/manual/nixpkgs/stable/#python); packaging: [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Rust | `rustc`, `cargo`, `rust-analyzer` (from nixpkgs) | `rustPlatform.buildRustPackage` — [Rust](https://nixos.org/manual/nixpkgs/stable/#rust); packaging: [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Go | `go`, `gopls` | `buildGoModule` — [Go](https://nixos.org/manual/nixpkgs/stable/#sec-language-go); packaging: [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Node / JS | `nodejs`, `npm` / yarn tools as needed | `buildNpmPackage` (and related hooks) — [JavaScript](https://nixos.org/manual/nixpkgs/stable/#language-javascript); packaging: [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Haskell | `haskellPackages.ghcWithPackages`, `cabal-install`, HLS | `haskellPackages.mkDerivation` / `callPackage` — [Haskell](https://nixos.org/manual/nixpkgs/stable/#haskell); packaging: [Haskell packaging](../06-nixpkgs/packaging/haskell-packaging.md) |
| JVM / Gradle | `jdk`, `gradle`, tools from `javaPackages` | Ant/`jdk` derivations; Gradle via `mitmCache` / `deps.json` — [Java](https://nixos.org/manual/nixpkgs/stable/#sec-language-java), [Gradle](https://nixos.org/manual/nixpkgs/stable/#gradle); packaging: [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md) |
| PHP / Composer | `php`, `php.packages.composer`, `php.withExtensions` | `php.buildComposerProject2` (`vendorHash`) — [PHP](https://nixos.org/manual/nixpkgs/stable/#sec-php); packaging: [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md) |

Nested scopes (`python3Packages`, `haskellPackages`, `php.extensions`, …) are the same [package set](../06-nixpkgs/architecture/package-sets.md) pattern: pick one scope and stay in it for both shell and packaging.

Higher-level shell frameworks ([devenv / other wrappers](../05-cli-and-tooling/adjacent-tools/devenv-devshell.md)) still pull these same packages; they do not invent a separate language infra.

### Failure modes

| Failure | What goes wrong |
|---------|-----------------|
| Shell vs packaging mismatch | Dev shell has `cargo` / `go` / a JDK, but CI packages with a different builder or toolchain pin → “works in `nix develop`, fails in `nix build`”. Align shell tools with the builder’s platform (`rustPlatform`, versioned `go_*`, same `haskellPackages` / GHC). |
| Host rustup / Go / npm | Tools from the impure host PATH drift across machines and diverge from store compilers packaging will use. Prefer nixpkgs (or a pinned overlay) for anything you expect to reproduce. |
| Wrong package set scope | Mixing `python3Packages` with another interpreter’s set, or default `haskellPackages` with a different `haskell.packages.ghc*` compiler, yields missing attrs, ABI/version clashes, or Cabal bound failures. Stay inside one [package set](../06-nixpkgs/architecture/package-sets.md). |

### Boundaries

- **This page:** which APIs to reach for in a shell, and how they relate to packaging.
- **Not here:** full builder options, FOD hashes, Gradle `deps.json` refresh, Cabal overrides, Composer `vendorHash`—see [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md), [Haskell packaging](../06-nixpkgs/packaging/haskell-packaging.md), [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md).
- If a flake `devShell` pulls **private inputs**, auth belongs in Nix config / CI secrets—see [Private flakes and CI](private-flakes-and-ci.md).

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

```nix
# flake.nix (excerpt) — Haskell GHC + libraries from haskellPackages
{
  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      ghc = pkgs.haskellPackages.ghcWithPackages (ps: [ ps.aeson ps.turtle ]);
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ ghc pkgs.cabal-install ];
      };
    };
}
```

For actually *building* projects as derivations, use the packaging leaves—shells alone do not lock Cargo/npm/Go/Composer graphs the way those helpers do.

## References

- [Nixpkgs manual — Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support)
- [Nixpkgs manual — Python](https://nixos.org/manual/nixpkgs/stable/#python)
- [Nixpkgs manual — Rust](https://nixos.org/manual/nixpkgs/stable/#rust)
- [Nixpkgs manual — Go](https://nixos.org/manual/nixpkgs/stable/#sec-language-go)
- [Nixpkgs manual — JavaScript](https://nixos.org/manual/nixpkgs/stable/#language-javascript)
- [Nixpkgs manual — Haskell](https://nixos.org/manual/nixpkgs/stable/#haskell)
- [Nixpkgs manual — Java](https://nixos.org/manual/nixpkgs/stable/#sec-language-java)
- [Nixpkgs manual — Gradle](https://nixos.org/manual/nixpkgs/stable/#gradle)
- [Nixpkgs manual — PHP](https://nixos.org/manual/nixpkgs/stable/#sec-php)
- [nix-community/fenix](https://github.com/nix-community/fenix) (community; optional)
- [oxalica/rust-overlay](https://github.com/oxalica/rust-overlay) (community; optional)

## See also

- [Shells and direnv](shells-and-direnv.md)
- [Python / Node / Rust / Go packaging](../06-nixpkgs/packaging/python-node-rust-go.md)
- [Haskell packaging](../06-nixpkgs/packaging/haskell-packaging.md)
- [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md)
- [Package sets](../06-nixpkgs/architecture/package-sets.md)
- [Private flakes and CI](private-flakes-and-ci.md) — when shell flakes need private inputs
- [stdenv](../06-nixpkgs/architecture/stdenv.md)
- [devenv / adjacent shell tools](../05-cli-and-tooling/adjacent-tools/devenv-devshell.md)
