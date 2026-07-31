---
status: complete
---

# Fetchers and pinning

## Overview

Nixpkgs **fetchers** (`fetchurl`, `fetchzip`, `fetchFromGitHub`, and the rest of the `fetch*` family) download upstream sources as [fixed-output derivations](../../02-concepts/fixed-output-derivation.md) (FODs). Each call declares a content hash; Nix fetches at build time and fails if the bytes do not match. **Pinning** is the broader workflow of recording which revision or artifact your project depends on—either inline in a package expression, in a lock file managed by a tool like [npins](https://github.com/andir/npins), or via [flake inputs](../../07-flakes/anatomy/lockfile.md).

This page covers the fetcher family, how it differs from [builtins fetchers](../../03-language/builtins/import-and-fetch.md), and common pinning strategies for nixpkgs itself and other dependencies.

## Details

### The `fetch*` family

Nixpkgs fetchers live under `pkgs.fetchurl`, `pkgs.fetchFromGitHub`, and related attributes. They wrap `stdenv.mkDerivation` (or equivalent) with `outputHash*` set so the result is a FOD. Typical uses in [simple packages](simple-package.md):

| Fetcher | Typical source |
|---------|------------------|
| `fetchurl` | Single file (tarball, patch, binary) |
| `fetchzip` | Archive unpacked to a directory |
| `fetchpatch` | Patch file with optional normalization |
| `fetchFromGitHub` / `fetchFromGitLab` | Git host archives or git snapshots |
| `fetchgit` | Arbitrary git URLs |
| `fetchCargoVendor` / language-specific fetchers | Ecosystem lockfiles (Rust, npm, …) |

Prefer modern SRI hashes (`hash = "sha256-…"`) over legacy `sha256 = "…"` when writing new expressions. The [Nixpkgs Fetchers chapter](https://nixos.org/manual/nixpkgs/stable/#chap-pkgs-fetchers) documents each helper.

**Updating hashes:** The manual recommends the **fake-hash loop** unless you know how a fetcher hashes its output: set `hash` to `""`, `lib.fakeHash`, `lib.fakeSha256`, or `lib.fakeSha512`, build, and copy the hash from the mismatch error. Alternatives include `nix-prefetch-url`, `nix-prefetch-git`, and other `nix-prefetch-*` tools (hash printed to stdout, often nix-base32), `nix-prefetch-url '<flake>' -A src` for a package’s `src`, and upstream checksums when the format matches. In nixpkgs maintenance, [nix-update](https://github.com/Mic92/nix-update) can bump `version`/`src` and refresh fetcher attrs.

**Footgun:** An FOD’s store output is keyed by the declared hash, not the URL. If you change `url` or `rev` but leave the old `hash`, Nix can still satisfy the derivation from the existing store path—stale content, no new download. Reset the hash (fake-hash loop) whenever the locator changes.

For packaging patterns that combine fetchers with local changes, see [patches and overrides](patches-and-overrides.md).

### Builtins vs Nixpkgs fetchers

| | **Builtins** (`fetchTarball`, `fetchGit`, …) | **Nixpkgs fetchers** (`pkgs.fetchurl`, …) |
|---|---------------------------------------------|-------------------------------------------|
| When | Evaluation time | Build time (derivation) |
| Output | Store path returned directly | FOD derivation; use as `src` like any other input |
| Needs `pkgs` | No | Yes (from an imported nixpkgs) |
| Typical role | Bootstrap / pin nixpkgs itself | Package `src` inside expressions |

Using a pkgs fetcher as `src = fetchurl { … }` is ordinary dependency wiring, not [import from derivation](../../02-concepts/import-from-derivation.md). IFD is when evaluation *reads* a derivation’s output (for example `import` of a generated `.nix`); avoid conflating the two.

Bootstrapping nixpkgs almost always starts with a builtin or pre-built tarball; package definitions inside nixpkgs use pkgs fetchers. See [import and fetch](../../03-language/builtins/import-and-fetch.md) for builtin semantics and purity restrictions.

### Pinning strategies

| Strategy | Lock artifact | Updates | Best for |
|----------|---------------|---------|----------|
| **Open-coded hashes** | None—hashes live in `.nix` files | Fake-hash loop, `nix-prefetch-*`, or `nix-update` | Single fetchers inside nixpkgs expressions, one-off tarballs |
| **npins** | `npins/sources.json` (+ generated `default.nix`) | `npins update`, `npins add`, … | Non-flake repos pinning nixpkgs, git repos, channels, PyPI, tarballs |
| **Flakes** | `flake.lock` | `nix flake update`, `nix flake lock` | Flake-first projects; transitive input closure |
| **niv** (legacy) | `nix/sources.json` | `niv update` | Older repos; [npins](https://github.com/andir/npins) is the usual successor (`npins import-niv`) |
| **nvfetcher** | Tool-specific (often YAML + Nix) | Updater oriented at nixpkgs fetcher attrs | Maintainers refreshing many package src hashes in nixpkgs-style expressions |

**npins** (primary non-flake pin manager): `npins init` writes `npins/sources.json` and a small importer. Default fetches use **builtins** (eval-time paths, no extra derivation)—GitHub/GitLab pins use `fetchTarball` rather than `fetchGit`. Passing `{ pkgs = …; }` to a pin switches to **Nixpkgs fetchers** and returns a FOD derivation. It tracks git branches/tags, Nix channels (including `programs.sqlite` and other channel artifacts), PyPI, tarballs, and more; `npins import-flake` can migrate from an existing lockfile.

**Flakes** pin inputs declaratively in `flake.nix` and record resolved revisions in [lockfile.md](../../07-flakes/anatomy/lockfile.md). That replaces channel-style `nix-channel` workflows for many users; see [migration from channels](../../07-flakes/migration-from-channels.md).

**Pinning nixpkgs without flakes:** import a locked nixpkgs path, then `callPackage` as usual:

```nix
let
  sources = import ./npins;
  pkgs = import sources.nixpkgs { };
in
pkgs.callPackage ./mypackage.nix { }
```

The exact `sources.nixpkgs` value is whatever npins recorded (channel tarball URL + hash, git rev, etc.). Overlays that pin versions of specific packages are a separate concern—see [overlays pinning](../overlays-and-overrides/pinning.md).

## Examples

**`fetchFromGitHub` in a package** (placeholder hash—substitute after a failed build reports the real SRI hash):

```nix
{ lib, stdenv, fetchFromGitHub }:

stdenv.mkDerivation {
  pname = "example";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "example";
    repo = "example";
    rev = "v1.0.0";
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  meta = with lib; {
    description = "Example fetched from GitHub";
    license = licenses.mit;
  };
}
```

**Minimal npins import** (after `npins init` / `npins add channel nixpkgs-unstable`):

```nix
let
  sources = import ./npins;
  pkgs = import sources.nixpkgs { };
in
{
  inherit pkgs;
  # Optional: FOD derivation instead of eval-time path
  # myTool = sources.myTool { inherit pkgs; };
}
```

Commit `npins/sources.json` (and usually `npins/default.nix`) so CI and collaborators resolve the same nixpkgs revision.

## References

- [Nixpkgs manual — Fetchers](https://nixos.org/manual/nixpkgs/stable/#chap-pkgs-fetchers) — `fetch*` helpers, fake-hash loop, `nix-prefetch-*`
- [npins README](https://github.com/andir/npins) — lock format, commands, builtins vs `pkgs` fetchers
- [nix-update](https://github.com/Mic92/nix-update) — bump nixpkgs package versions and refresh src hashes
- [Nix reference manual — fetchers and import](https://nix.dev/manual/nix/stable/language/builtins.html) — builtin `fetchTarball`, `fetchGit`, …

## See also

- [Simple package](simple-package.md) — `callPackage` + fetcher in a minimal derivation
- [Patches and overrides](patches-and-overrides.md) — changing fetched sources after unpack
- [Overlays pinning](../overlays-and-overrides/pinning.md) — pinning package versions via overlays
- [Fixed-output derivation](../../02-concepts/fixed-output-derivation.md) — why hashes fix store paths
- [Import from derivation](../../02-concepts/import-from-derivation.md) — when FOD outputs affect evaluation
- [Import and fetch (builtins)](../../03-language/builtins/import-and-fetch.md) — eval-time fetchers
- [Flake lockfile](../../07-flakes/anatomy/lockfile.md) — flake input pinning
- [Migration from channels](../../07-flakes/migration-from-channels.md) — channels vs flakes vs lock tools
