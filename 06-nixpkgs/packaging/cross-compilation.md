---
status: complete
---

# Cross Compilation

## Overview

**Cross-compilation** means building on one machine for another: the build runs on the **build platform**, but the installed product runs on the **host platform**. Nixpkgs expects packages to be written in a cross-friendly way so evaluation stays the same whether you are on a native or cross build—the main difference is which dependency slots and toolchains apply.

This page is an architecture-level packaging guide: platforms, dependency lists, and how to spot cross breakage. It does not cover bootstrapping stages, splicing, or remote builder setup in depth.

## Details

### Three platforms

Nixpkgs follows the GNU autoconf convention. Every [stdenv](../architecture/stdenv.md) derivation has three platform attributes:

| Platform | Meaning | Typical question |
|----------|---------|------------------|
| `buildPlatform` | Where the build executes | “What CPU/OS is running `make`?” |
| `hostPlatform` | Where the output runs | “What CPU/OS will `hello` run on?” |
| `targetPlatform` | What code a compiler *emits* | “What triple does this GCC target?” |

Access them as `stdenv.buildPlatform`, `stdenv.hostPlatform`, and `stdenv.targetPlatform`. For most libraries and applications, **target can be ignored**—it matters mainly for compilers and similar tools that produce machine code for a third platform.

On a native build, build and host match. When cross-compiling, they differ and stdenv wires a cross toolchain (wrappers, prefixed binutils, and so on).

### Dependency slots and platform offsets

Dependencies are categorized by **which platform they execute on** and **which platform they produce artifacts for**. The two lists you use daily map to the common case:

| Attribute | Offset (host → target) | Holds |
|-----------|------------------------|--------|
| `nativeBuildInputs` | build → host | Tools that run during the build and produce output for the host (compilers, `cmake`, `pkg-config`, setup hooks) |
| `buildInputs` | host → target | Libraries and headers linked into the **product** at run time |

When a dependency is itself a compiler or emits code for another stage, Nixpkgs adds more slots—`depsBuildBuild`, `depsBuildTarget`, `depsHostHost`, and others. The manual’s [dependency categorization](https://nixos.org/manual/nixpkgs/stable/#ssec-stdenv-dependencies) table lists all nine practical types.

**Wrong slot, silent on native:** putting a build tool in `buildInputs` or a runtime library in `nativeBuildInputs` often still works on native builds because stdenv is lenient. Cross builds fail or produce broken binaries because tools and libraries must come from the correct platform slice.

### `strictDeps`

Set `strictDeps = true` on a derivation (or rely on Nixpkgs defaults where enabled) to **disable lenient placement**. Each dependency is then exposed only through the slot where it belongs—matching cross behavior even when build and host are the same.

Use this when debugging cross failures or hardening a package: if the build breaks with `strictDeps = true`, fix the dependency lists rather than removing the flag.

### Writing cross-friendly packages

Patterns that keep native and cross evaluation aligned:

- **Sort by role, not by “needed at build time”:** anything executed on the build machine (including code generators and `makeWrapper`) belongs in `nativeBuildInputs`; anything linked into the installed artifact belongs in `buildInputs`.
- **Use stdenv-provided tool names:** cross builds expose prefixed tools (for example `${stdenv.cc.targetPrefix}cc`). Patches or `makeFlags` that hard-code unprefixed `cc`/`ld` break cross.
- **Gate tests on executability:** skip or emulate host-platform tests when the build machine cannot run host binaries—`stdenv.buildPlatform.canExecute stdenv.hostPlatform` is the usual condition.
- **Branch on platform when necessary:** `stdenv.hostPlatform`, `stdenv.buildPlatform`, and predicates from `lib.systems.inspect` are preferred over ad-hoc string checks on `system`.

You do **not** need to pick dependencies from `pkgsBuildHost` / `pkgsHostTarget` by hand in most packages: list them in the correct `*Inputs` attribute and Nixpkgs resolves the right package set when cross-compiling.

### Building for another platform (consumer view)

To **build** existing packages for another architecture, use the cross package sets under `pkgsCross.*` (for example `pkgsCross.aarch64-multiplatform.hello`). Instantiate Nixpkgs with a `crossSystem` when you need a custom triple. Hydra maintains some pre-built cross toolchains so you are not always compiling GCC from source.

That workflow is separate from **packaging** correctly: a cross-friendly `mkDerivation` should need few or no `if stdenv.hostPlatform != stdenv.buildPlatform` special cases. Offloading builds to another machine is covered under [remote builders](../../04-store-and-build/remote-builders.md).

## Examples

Minimal pattern: build tool vs runtime library (same as native, but cross depends on it):

```nix
{ lib, stdenv, fetchurl, pkg-config, zlib }:

stdenv.mkDerivation {
  pname = "example";
  version = "1.0.0";

  src = fetchurl { /* … */ };

  nativeBuildInputs = [ pkg-config ];
  buildInputs = [ zlib ];

  strictDeps = true;

  meta = { /* … */ };
}
```

When the build system must run a small C helper **on the build platform** (build → build), add a compiler from the build-stage package set:

```nix
{ stdenv, buildPackages, /* … */ }:

stdenv.mkDerivation {
  depsBuildBuild = [ buildPackages.stdenv.cc ];
  /* … */
}
```

Skip the test phase when host binaries cannot run on the builder:

```nix
stdenv.mkDerivation {
  doCheck = stdenv.buildPlatform.canExecute stdenv.hostPlatform;
  /* … */
}
```

Build an existing package for ARM from x86_64 Linux (illustrative):

```bash
nix-build '<nixpkgs>' -A pkgsCross.aarch64-multiplatform.hello
```

## References

- [Cross-compilation](https://nixos.org/manual/nixpkgs/stable/#chap-cross) — Nixpkgs manual (platforms, dependency theory, cookbook)
- [Specifying dependencies](https://nixos.org/manual/nixpkgs/stable/#ssec-stdenv-dependencies) — Nixpkgs manual (`nativeBuildInputs`, `buildInputs`, `strictDeps`, extended slots)
- [Cross-compilation tutorial](https://nix.dev/tutorials/cross-compilation.html) — nix.dev (hands-on build walkthrough)

## See also

- [Simple package](simple-package.md) — baseline `nativeBuildInputs` / `buildInputs` usage
- [stdenv](../architecture/stdenv.md) — standard environment and phases
- [mkDerivation](../architecture/mkDerivation.md) — derivation attributes and overrides
- [Derivation](../../02-concepts/derivation.md) — primitive below `mkDerivation`
- [Remote builders](../../04-store-and-build/remote-builders.md) — forwarding builds to other machines
