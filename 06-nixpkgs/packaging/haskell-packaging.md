---
status: complete
---

# Haskell packaging

## Overview

Nixpkgs’ Haskell infrastructure has two jobs. The **primary** one is packaging Haskell software for the tree: a default GHC, Cabal-aware builders, and a large curated set under `haskellPackages`. The **secondary** one is limited support for Haskell *development* environments (prebuilt libraries on `cache.nixos.org`). Dev shells are useful when your project fits the default compiler and pinned versions; they are not a full substitute for `cabal-install` / Stack solvers. See [limitations](https://nixos.org/manual/nixpkgs/stable/#haskell-limitations) in the manual.

For other language builders, see the sibling survey [Python / Node / Rust / Go](python-node-rust-go.md). For DIY shells around compilers without a full package set, see [language toolchains](../../11-development/language-toolchains.md).

## Details

### Package sets and compilers

- **`haskellPackages`** — default GHC and the main Hackage-facing package set (alias of a `haskell.packages.*` set for the current default compiler).
- **`haskell.compiler.*`** — other GHC releases.
- **`haskell.packages.*`** — package sets built with those compilers (for example `haskell.packages.ghc948`). Non-default sets are tested less and cache fewer packages.

Attribute names match Hackage names. Many top-level tools (`ghc`, `cabal-install`, apps like `cachix`) are re-exported from `haskellPackages` for convenience. Nested language sets are a [package set](../architecture/package-sets.md) pattern, same idea as `python3Packages`.

### Version policy (not Cabal resolution)

Nixpkgs does **not** run Cabal dependency resolution the way `cabal-install` does. It picks **one** version per package name and wires named deps from the set:

| Case | Default version |
|------|-----------------|
| On the Stackage snapshot in use (usually current LTS) | Stackage version |
| Otherwise | Newest on the pinned Hackage snapshot (or a manual older pin when needed) |

When the newest Hackage version is not the default, a versioned attribute like `haskellPackages.foo_1_2_3` may exist; relying on those outside nixpkgs is discouraged (they churn). The builder checks that provided packages satisfy Cabal version bounds and fails if they do not—set `jailbreak = true` (or `haskell.lib.compose.doJailbreak`) to lift bounds. That still does not invent a solver plan.

`haskellPackages.callPackage` fills named Cabal deps from the set (same [callPackage](../../03-language/idioms/callPackage.md) idea as the rest of nixpkgs).

### Builder: `haskellPackages.mkDerivation`

Each Haskell package set exposes **`mkDerivation`**: a wrapper around `stdenv.mkDerivation` that runs the package’s **`Setup.hs`** via the Cabal *library*. It does **not** invoke the `cabal-install` binary. In practice expressions are often generated with `cabal2nix`; you still need the builder’s knobs for overrides.

Dependencies follow Cabal grouping, for example:

- `libraryHaskellDepends`, `executableHaskellDepends`, `testHaskellDepends`, …
- `*ToolDepends` → `nativeBuildInputs`; `*HaskellDepends` → `propagatedBuildInputs`; `*SystemDepends` / `*PkgconfigDepends` → `buildInputs`

That is different from a bare [simple package](simple-package.md) that only lists `buildInputs` / `nativeBuildInputs`.

### Development shells

Useful patterns (feasibility depends on matching default versions):

- **`pkg.env`** — every `mkDerivation` result exposes `passthru.env` (GHC via **`ghcWithPackages`** with deps in the package DB). Example: `nix-shell -A haskellPackages.random.env`.
- **`haskellPackages.ghcWithPackages (ps: [ … ])`** — custom GHC + selected libraries.
- **`haskellPackages.shellFor { packages = hpkgs: [ … ]; … }`** — multi-package / `cabal.project` shells; add `cabal-install`, HLS, etc. via `nativeBuildInputs`.

These are convenience environments, not a mirror of every packaging detail. For general language shells outside this set, see [language toolchains](../../11-development/language-toolchains.md).

### Overrides and overlays

High-level options:

- **Single package inputs:** `haskellPackages.nix-tree.override { brick = haskellPackages.brick_0_67; }`
- **Cabal builder args:** `haskell.lib.compose.overrideCabal` (and helpers like `doJailbreak`, `dontHaddock`)
- **Package set:** `haskellPackages.extend (hfinal: hprev: { … })`, or nixpkgs [overlays](../overlays-and-overrides/writing-overlays.md) that replace `haskell.packages.<ghc>` with `.override { overrides = hfinal: hprev: { … }; }` so dependents see pinned versions through the fixed point

Keep Haskell set overrides consistent with the same compiler scope. Concept background: [overlay](../../02-concepts/overlay.md).

### Alternative: haskell.nix

[haskell.nix](https://input-output-hk.github.io/haskell.nix/) can generate package sets from Cabal/Stack plans. It is **completely incompatible** with `haskellPackages`—survey only here; do not mix the two ecosystems in one dependency graph.

## Examples

GHC with a few libraries (ad-hoc env):

```nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.haskellPackages.ghcWithPackages (ps: with ps; [
  aeson
  lens
])
```

Minimal local package via `callPackage` (after `cabal2nix ./. > my-project.nix`):

```nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.haskellPackages.callPackage ./my-project.nix { }
```

Then `nix-build` or `nix-shell -A env` on that expression. For a batteries-included shell, prefer `shellFor` as in the [development environments](https://nixos.org/manual/nixpkgs/stable/#haskell-development-environments) section.

Extend the set so dependents see a jailbroken library (stand-in name; use a real attr from your set):

```nix
{ pkgs ? import <nixpkgs> { } }:

let
  hp = pkgs.haskellPackages.extend (
    hfinal: hprev: {
      turtle = pkgs.haskell.lib.compose.doJailbreak hprev.turtle;
    }
  );
in
hp.ghcWithPackages (ps: [ ps.aeson ps.turtle ])
```

## References

- [Nixpkgs manual — Haskell](https://nixos.org/manual/nixpkgs/stable/#haskell)
- [Nixpkgs manual — Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support)
- [haskell.nix](https://input-output-hk.github.io/haskell.nix/) (incompatible alternative; survey only)

## See also

- [Python / Node / Rust / Go](python-node-rust-go.md) — other language packaging survey
- [Simple package](simple-package.md) — generic `stdenv.mkDerivation` walkthrough
- [Package sets](../architecture/package-sets.md) — nested scopes like `haskellPackages`
- [callPackage](../../03-language/idioms/callPackage.md) — named dependency injection
- [Writing overlays](../overlays-and-overrides/writing-overlays.md) — reshaping package sets
- [Language toolchains](../../11-development/language-toolchains.md) — compilers and shells map
