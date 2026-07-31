---
status: complete
---

# Simple Package

## Overview

Most upstream software that ships a Unix-style build (`./configure && make && make install`, or equivalent) is packaged in Nixpkgs with [`stdenv.mkDerivation`](../architecture/mkDerivation.md). You declare `pname` / `version`, fetch a fixed source, put tools and libraries in the right dependency slots, and let [stdenv](../architecture/stdenv.md) run the default [build phases](../../04-store-and-build/build-phases.md).

This page is the minimal walkthrough: one `callPackage`-style function, one tarball or Git tag, automatic phases, enough `meta` to land in the tree, and where that file lives under `pkgs/by-name/`.

## Details

### Function shape

Prefer the `callPackage` pattern: a function `{ lib, stdenv, fetchurl, … }:` whose arguments are filled from Nixpkgs’ package set. That keeps dependencies explicit and makes overrides predictable. See [callPackage](../../03-language/idioms/callPackage.md).

Inside, call `stdenv.mkDerivation` with at least `pname`, `version`, and `src`. Since [RFC 0035](https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md), Nixpkgs derives `name` as `"${pname}-${version}"` (see the manual’s [Using stdenv](https://nixos.org/manual/nixpkgs/stable/#sec-using-stdenv)).

### Source and hash

Use `fetchurl` / `fetchzip` for release archives, or `fetchFromGitHub` (and similar fetchers) for tagged sources. Every fixed-output fetch needs a `hash` (SRI `sha256-…`) or legacy `sha256`. After the first failed build, copy the hash Nix reports rather than guessing—the [nix.dev packaging tutorial](https://nix.dev/tutorials/packaging-existing-software/) walks through that loop with GNU Hello.

### `buildInputs` vs `nativeBuildInputs`

| Attribute | Holds | Examples |
|-----------|--------|----------|
| `nativeBuildInputs` | Tools that run on the **build** machine during the build | `pkg-config`, `cmake`, `makeWrapper`, `autoreconfHook` |
| `buildInputs` | Libraries and headers linked into the **product** | `zlib`, `openssl`, `libpng` |

Stdenv setup hooks wire these into `PATH`, `PKG_CONFIG_PATH`, compiler flags, and related variables. On cross builds the split is strict. Native builds are more forgiving when `strictDeps` is off, but misplacing tools vs libraries still bites once you cross-compile or tighten dependency tracking. See [dependency sections](https://nixos.org/manual/nixpkgs/stable/#ssec-stdenv-dependencies) for propagated inputs and other slots.

### Phases

For typical autotools or plain-Make projects you usually **do not** define phases yourself. Stdenv’s default builder runs unpack → patch → configure → build → install (and fixup) via `genericBuild`. Add `preInstall`, `postPatch`, or similar hooks for small fixes; replace a whole phase only when the upstream build system is non-standard.

### `meta`

Set at least:

- `description` — short, factual summary
- `license` — from `lib.licenses` (or a custom license set when needed)
- `platforms` — often `lib.platforms.unix` or a tighter list after you verify the build
- `maintainers` — handles from [maintainers-and-teams](../architecture/maintainers-and-teams.md)

`meta` is not a builder input; changing it alone does not rebuild the package.

### Landing in Nixpkgs (`pkgs/by-name`)

New top-level packages that use `pkgs.callPackage` should live under [`pkgs/by-name/`](https://github.com/NixOS/nixpkgs/tree/master/pkgs/by-name) whenever possible. Layout is:

```text
pkgs/by-name/<ab>/<name>/package.nix
```

`<ab>` is the lowercase two-letter prefix of the attribute name; `<name>` is the attribute (for example `pkgs/by-name/ex/example/package.nix` → `pkgs.example`). The directory is auto-discovered—no `all-packages.nix` entry for the default case. Language-scoped packages (`python3Packages.*`, and so on) and other exceptions stay in the category hierarchy; see the [by-name README](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/README.md) and [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md). Review expectations: [review process](../contribution/review-process.md).

## Examples

Illustrative only—placeholder hashes and URLs will not build until you substitute a real source and the hash Nix reports.

Minimal package from a tarball with one library dependency:

```nix
{ lib, stdenv, fetchurl, zlib }:

stdenv.mkDerivation {
  pname = "example";
  version = "1.0.0";

  src = fetchurl {
    url = "https://example.com/example-1.0.0.tar.gz";
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  buildInputs = [ zlib ];

  meta = with lib; {
    description = "Example library and CLI";
    homepage = "https://example.com/";
    license = licenses.mit;
    platforms = platforms.unix;
    maintainers = with maintainers; [ ];
  };
}
```

Same shape with a GitHub tag and a native build tool (`pkg-config` in `nativeBuildInputs`, library in `buildInputs`):

```nix
{ lib, stdenv, fetchFromGitHub, pkg-config, zlib }:

stdenv.mkDerivation {
  pname = "example";
  version = "2.0.0";

  src = fetchFromGitHub {
    owner = "org";
    repo = "example";
    rev = "v2.0.0";
    hash = "sha256-BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=";
  };

  nativeBuildInputs = [ pkg-config ];
  buildInputs = [ zlib ];

  meta = with lib; {
    description = "Example with pkg-config";
    license = licenses.gpl3Only;
    platforms = platforms.linux;
    maintainers = with maintainers; [ ];
  };
}
```

For a worked end-to-end build (GNU Hello + fixing the hash), follow the nix.dev tutorial in References.

## References

- [The Standard Environment (`stdenv`)](https://nixos.org/manual/nixpkgs/stable/#chap-stdenv) — Nixpkgs manual chapter
- [Using stdenv](https://nixos.org/manual/nixpkgs/stable/#sec-using-stdenv) — `pname` / `version`, phases, minimal attrs
- [Build-time vs. host-time dependencies](https://nixos.org/manual/nixpkgs/stable/#ssec-stdenv-dependencies) — `nativeBuildInputs` vs `buildInputs` and related slots
- [Packaging existing software](https://nix.dev/tutorials/packaging-existing-software/) — nix.dev tutorial (worked Hello example; use for a real hash loop)
- [pkgs/by-name README](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/README.md) — name-based package layout
- [Nixpkgs CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md) — where and how to add packages
- [RFC 0035 (pname/version)](https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md)

## See also

- [mkDerivation](../architecture/mkDerivation.md) — attribute reference and overrides
- [stdenv](../architecture/stdenv.md) — environment, phases, and hooks
- [Derivation](../../02-concepts/derivation.md) — primitive below `mkDerivation`
- [Build phases](../../04-store-and-build/build-phases.md) — default phase order
- [Multiple outputs](multiple-outputs.md) — splitting bin/lib/dev outputs
- [Patches and overrides](patches-and-overrides.md) — fixing upstream without forking
