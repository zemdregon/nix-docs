---
status: complete
---

# mkDerivation

## Overview

`stdenv.mkDerivation` is the primary Nixpkgs package constructor. It wraps Nix’s primitive [`derivation`](../../02-concepts/derivation.md) with [stdenv](stdenv.md)’s default builder and `genericBuild`, so most packages get a standard `./configure; make; make install` workflow (or language-specific hooks) without writing a custom builder script.

Packagers pass an attribute set (or a fixed-point function returning one) describing sources, dependencies, build phases, and metadata. The result is a derivation value that Nix can realize into store paths. For a minimal packaging walkthrough, see [Simple package](../packaging/simple-package.md).

## Details

**Minimum identity and source.** Specifying a `name` and a `src` is the absolute minimum Nix requires. Prefer `pname` and `version` ([RFC 0035](https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md)); `mkDerivation` then sets `name` to `"${pname}-${version}"` by default.

**Fixed-point arguments.** Preferred style is to pass a function so overrides see the final attribute set:

```nix
stdenv.mkDerivation (finalAttrs: {
  pname = "example";
  version = "1.0";
  src = ./.;
  configureFlags = lib.optionals finalAttrs.withFeature [ "--with-feature" ];
  withFeature = true;
})
```

The `finalAttrs` parameter is the attribute set after all `overrideAttrs` layers—not a `rec` binding, which is unaware of overriding. `finalAttrs.finalPackage` is the resulting package (output paths, `.overrideAttrs`, and so on).

**Common attributes.** Typical fields include `src` / `srcs`, `buildInputs`, `nativeBuildInputs`, `propagatedBuildInputs`, phase hooks (`preInstall`, `postPatch`, …), and `meta`. See the manual’s [stdenv attribute reference](https://nixos.org/manual/nixpkgs/stable/#ssec-stdenv-attributes) for the full list and dependency-slot naming.

**`meta` and `passthru`.** Meta-attributes are not passed to the builder; changing `meta` (license, description, platforms) does not trigger a rebuild. `passthru` holds extra attributes on the package value—commonly `passthru.tests` wired through `finalAttrs.finalPackage` (see [tests and passthru](../packaging/tests-and-passthru.md)).

**`__structuredAttrs`.** When enabled, attributes intended as environment variables for the builder belong in the `env` attribute set; attributes local to the build script stay outside `env` so they remain structured shell variables. The manual treats this as the preferred default, and all new top-level packages must enable it. `passAsFile` is disabled when structured attrs are on.

**Overrides.** Prefer `.overrideAttrs` over `.overrideDerivation`. `overrideAttrs` re-processes attributes through `mkDerivation` (so flags like `separateDebugInfo` and input lists like `nativeBuildInputs` work correctly). See [Overlay vs Override](../../02-concepts/overlay-vs-override.md) for when to override one package versus changing the whole set.

**Phases.** `stdenv.mkDerivation` sets the derivation’s builder to a script that loads stdenv’s `setup.sh` and calls `genericBuild`. Unless you supply `builder`, `buildCommand`, or `buildCommandPath`, that runs the usual [build phases](../../04-store-and-build/build-phases.md).

## Examples

**GNU Hello–shaped package** (`pname` / `version` / `finalAttrs`, hash verified against current Nixpkgs `hello`):

```nix
stdenv.mkDerivation (finalAttrs: {
  pname = "hello";
  version = "2.12.3";
  src = fetchurl {
    url = "mirror://gnu/hello/hello-${finalAttrs.version}.tar.gz";
    hash = "sha256-DV9gFUOC/uELEUocNOeF2LH0kgc64tOm97FHaHs2aqA=";
  };
})
```

**Override-friendly flag via `finalAttrs`.**

```nix
stdenv.mkDerivation (finalAttrs: {
  pname = "mylib";
  version = "0.1";
  src = ./.;
  withDocs = true;
  buildInputs = lib.optionals finalAttrs.withDocs [ doxygen ];
})
```

**`passthru.tests` using `finalPackage`.**

```nix
{ stdenv, runCommand }:

stdenv.mkDerivation (finalAttrs: {
  pname = "mytool";
  version = "1.0";
  src = ./.;
  passthru.tests.smoke = runCommand "smoke" { } ''
    ${finalAttrs.finalPackage}/bin/mytool --version | grep ${finalAttrs.version}
    touch $out
  '';
})
```

**Structured environment variables.**

```nix
stdenv.mkDerivation {
  pname = "example";
  version = "1.0";
  src = ./.;
  __structuredAttrs = true;
  env.CUSTOM_FLAG = "1";
}
```

## References

- [Nixpkgs manual — Using stdenv](https://nixos.org/manual/nixpkgs/stable/#sec-using-stdenv)
- [Nixpkgs manual — Fixed-point arguments of mkDerivation](https://nixos.org/manual/nixpkgs/stable/#mkderivation-recursive-attributes)
- [Nixpkgs manual — `.overrideAttrs`](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-overrideAttrs)
- [Nixpkgs manual — `__structuredAttrs`](https://nixos.org/manual/nixpkgs/stable/#var-stdenv-__structuredAttrs)
- [Nixpkgs manual — Meta-attributes](https://nixos.org/manual/nixpkgs/stable/#chap-meta)
- [RFC 0035 — Package naming](https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md)

## See also

- [stdenv](stdenv.md)
- [Simple package](../packaging/simple-package.md)
- [callPackage](../../03-language/idioms/callPackage.md)
- [Build phases](../../04-store-and-build/build-phases.md)
- [Overlay vs Override](../../02-concepts/overlay-vs-override.md)
