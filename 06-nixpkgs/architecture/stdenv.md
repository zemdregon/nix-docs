---
status: complete
---

# stdenv

## Overview

**stdenv** is Nixpkgs’ standard build environment: a preconfigured toolchain and bash-driven workflow that automates typical Unix builds (`./configure; make; make install`). Package definitions use [`stdenv.mkDerivation`](mkDerivation.md) instead of the primitive [`derivation`](../../02-concepts/derivation.md) function so builds get compilers, coreutils, phase scripts, and dependency setup hooks without reimplementing them.

In `pkgs/top-level`, `stdenv` is already in scope for most package functions. Outside that context—custom overlays, flakes, or standalone expressions—pass `stdenv` as a function argument (often via [`callPackage`](../../03-language/idioms/callPackage.md)).

## Details

### mkDerivation attributes

At minimum, `stdenv.mkDerivation` needs a package identity and source: historically `name` and `src`. Prefer `pname` and `version` ([RFC 0035](https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md)); Nixpkgs then sets `name` to `"${pname}-${version}"`.

Split dependencies by role:

- `nativeBuildInputs` — tools that run during the build (compilers helpers, `pkg-config`, `cmake`, setup hooks such as `makeWrapper`)
- `buildInputs` — libraries and other host dependencies linked or copied into the result

Stdenv setup hooks expose these on `PATH`, in compiler include/library paths, and through tool-specific variables (for example `PKG_CONFIG_PATH`). On native builds the placement is often forgiving; under cross-compilation or `strictDeps`, the split matters.

### Phases

The default builder loads `pkgs/stdenv/generic/setup.sh` and runs `genericBuild`, which walks an ordered list of [build phases](../../04-store-and-build/build-phases.md): unpack, patch, configure, build, check, install, fixup, installCheck, dist, plus insertion slots (`prePhases`, `preConfigurePhases`, …). Each phase is a bash function (or a string attribute with the same name). Prefer `pre*` / `post*` hooks (for example `postInstall`) over replacing whole phases.

To replace a phase entirely, define the phase and call `runHook preX` / `runHook postX` so upstream hooks still run. Setting the full `phases` attribute is discouraged for packaging—it is easy to omit `fixupPhase` (shebang rewriting, strip, and related fixups). Use a temporary `phases` subset mainly when [debugging builds](../../04-store-and-build/debugging-builds.md).

### Package setup hooks

A dependency may ship `$out/nix-support/setup-hook`. When that package appears in an input list, stdenv sources the hook so the dependency can initialize the build environment (extend `PATH`, register env hooks for headers/libraries, and so on) without every consumer repeating boilerplate.

Setup hooks run as a side effect of depending on a package—listing the same dependency twice can run a hook twice—so well-written hooks aim to be idempotent. Stdenv itself always runs several built-in hooks during `fixupPhase` (move docs under `share/`, compress man pages, strip, patch shebangs). Language and tool packages add more (for example `pkg-config`, Autotools, Python); put those packages in `nativeBuildInputs` when the hook must run at build time.

### Toolchain and flags

Stdenv supplies the usual build tools: GCC (via wrappers), `make`, `patch`, `coreutils`, and related utilities. Set `enableParallelBuilding = true` to pass parallel flags to `make` and similar tools (up to `build-cores` workers). Some generators (`cmake`, `meson`, `qmake`) enable it by default unless set to `false`.

New top-level packages should set `__structuredAttrs = true`, which passes attributes via structured shell/JSON files (`NIX_ATTRS_SH_FILE` / `NIX_ATTRS_JSON_FILE`) instead of flattening everything into string environment variables. Builder-facing env vars then belong under the `env` attribute.

### Debugging builds

Use `nix-shell` on the derivation, point `$out` (and other outputs) at writable paths, and run `genericBuild` or individual phase functions interactively. The [sandbox](../../04-store-and-build/builders-and-sandboxes.md) inside `nix-build` may differ from an unrestricted shell: paths, network, and impure host tools behave differently, so reproduce failures with the same command you use in CI when possible.

## Examples

Minimal package using `pname`, `version`, and a host library:

```nix
{ lib, stdenv, fetchurl, zlib }:

stdenv.mkDerivation {
  pname = "example";
  version = "1.0";

  src = fetchurl {
    url = "https://example.com/example-1.0.tar.gz";
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  buildInputs = [ zlib ];

  # Optional: run tests during checkPhase
  doCheck = true;
}
```

Append steps after the default `installPhase`:

```nix
postInstall = ''
  install -Dm644 README -t $out/share/doc/example
'';
```

Replace `buildPhase` while preserving hooks:

```nix
buildPhase = ''
  runHook preBuild
  gcc foo.c -o foo
  runHook postBuild
'';
```

## See also

- [mkDerivation](mkDerivation.md) — attribute set accepted by `stdenv.mkDerivation`
- [Build phases](../../04-store-and-build/build-phases.md) — default phase order and overrides
- [Debugging builds](../../04-store-and-build/debugging-builds.md) — interactive `genericBuild` and phase subsets
- [Builders and sandboxes](../../04-store-and-build/builders-and-sandboxes.md) — how derivations execute
- [derivation](../../02-concepts/derivation.md) — low-level store object stdenv builds on
- [callPackage](../../03-language/idioms/callPackage.md) — wiring `stdenv` into package functions

## References

- [Nixpkgs manual — Standard environment](https://nixos.org/manual/nixpkgs/stable/#chap-stdenv)
- [Nixpkgs manual — Using stdenv](https://nixos.org/manual/nixpkgs/stable/#sec-using-stdenv)
- [Nixpkgs manual — Phases](https://nixos.org/manual/nixpkgs/stable/#sec-stdenv-phases)
- [Nixpkgs manual — Package setup hooks](https://nixos.org/manual/nixpkgs/stable/#ssec-setup-hooks)
- [RFC 0035 — Package naming (`pname` / `version`)](https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md)
