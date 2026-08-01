---
status: complete
last-checked: 2026-08
---

# Cross Compilation

## Overview

**Cross-compilation** means building on one machine for another: the build runs on the **build platform**, but the installed product runs on the **host platform**. Nixpkgs expects packages to be written in a cross-friendly way so evaluation stays the same whether you are on a native or cross build—the main difference is which dependency slots and toolchains apply.

Nixpkgs can be instantiated with `localSystem` alone (native) or also with `crossSystem` (packages run on the latter; building happens on the former). Named cross [package sets](../architecture/package-sets.md) live under `pkgsCross.*`.

## Boundaries

| This page covers | Defer elsewhere |
|------------------|-----------------|
| Platforms (`build` / `host` / `target`), dependency slots, `strictDeps` | Full nine-type theory and splicing internals — [Cross-compilation](https://nixos.org/manual/nixpkgs/stable/#chap-cross) (infrastructure sections) |
| Choosing a cross stdenv via `pkgsCross` / `crossSystem` | Nested language scopes (`python3Packages`, …) — [package sets](../architecture/package-sets.md); shell-oriented compilers — [language toolchains](../../11-development/language-toolchains.md) |
| Packaging failure modes and smoke-testing with `pkgsCross.*.hello` | Forwarding a *native* build to another machine’s CPU — [remote builders](../../04-store-and-build/remote-builders.md) |
| Emulator hooks documented in the cookbook (`emulator`, `qemu-user` dispatch) | Bootstrapping stages, Canadian Cross, `pkgsBuildTarget` graph — manual infrastructure chapter |

**Cross vs remote builders:** cross-compilation uses a cross toolchain so the *builder’s* CPU produces *host* binaries (`build ≠ host`). Remote builders schedule a derivation whose `system` matches a remote machine so that machine builds *natively* for itself. Same goal (artifacts for another platform), different mechanism.

## Details

### Three platforms

Nixpkgs follows the GNU autoconf convention. Every [stdenv](../architecture/stdenv.md) derivation has three platform attributes:

| Platform | Meaning | Typical question |
|----------|---------|------------------|
| `buildPlatform` | Where the build executes | “What CPU/OS is running `make`?” |
| `hostPlatform` | Where the output runs | “What CPU/OS will `hello` run on?” |
| `targetPlatform` | What code a compiler *emits* | “What triple does this GCC target?” |

Access them as `stdenv.buildPlatform`, `stdenv.hostPlatform`, and `stdenv.targetPlatform`. For most libraries and applications, **target can be ignored**—it matters mainly for compilers and similar tools that produce machine code for a third platform.

On a native build, build and host match. When cross-compiling, they differ and stdenv wires a cross toolchain (wrappers, prefixed binutils, and so on). Platform fields such as `system`, `config` (LLVM triple), and `lib.systems.inspect` predicates live on those attribute sets; prefer `lib.systems.inspect` predicates over ad-hoc `system` string checks.

### Dependency slots and platform offsets

Dependencies are categorized by **which platform they execute on** and **which platform they produce artifacts for**. The two lists you use daily map to the common case:

| Attribute | Offset (host → target) | Holds |
|-----------|------------------------|--------|
| `nativeBuildInputs` | build → host | Tools that run during the build and produce output for the host (compilers, `cmake`, `pkg-config`, setup hooks) |
| `buildInputs` | host → target | Libraries and headers linked into the **product** at run time |

When a dependency is itself a compiler or emits code for another stage, Nixpkgs adds more slots—`depsBuildBuild`, `depsBuildTarget`, `depsHostHost`, and others. The manual’s [dependency categorization](https://nixos.org/manual/nixpkgs/stable/#ssec-stdenv-dependencies) table lists all nine practical types. Adjacent sets (`buildPackages` / `pkgsBuildHost`, `pkgs` / `pkgsHostTarget`, …) are how those slots resolve under cross; most packages still only sort into `*Inputs` lists and let splicing pick the right slice.

### `strictDeps`

Set `strictDeps = true` on a derivation (or rely on Nixpkgs defaults where enabled) to **disable lenient placement**. Each dependency is then exposed only through the slot where it belongs—matching cross behavior even when build and host are the same.

Use this when debugging cross failures or hardening a package: if the build breaks with `strictDeps = true`, fix the dependency lists rather than removing the flag.

### Choosing a cross stdenv (`pkgsCross` / `crossSystem`)

Intent is a **build vs deploy** pair: `localSystem` (where evaluation/build runs; often inferred) and optional `crossSystem` (where packages should run). The three `*Platform` values on each derivation are interpolated from that pair; you do not pass `buildPlatform` / `hostPlatform` when importing Nixpkgs.

| Situation | How to pick | Notes (manual) |
|-----------|-------------|----------------|
| Named, curated host | `pkgsCross.<name>.<pkg>` (e.g. `pkgsCross.aarch64-multiplatform.hello`) | `pkgsCross` attrs match `lib.systems.examples` names; explore with `nix repl` / tab-complete—names are convenience labels, not always the LLVM `config` string |
| Same named example as `crossSystem` | `nix-build '<nixpkgs>' --arg crossSystem '(import <nixpkgs/lib>).systems.examples.<name>' -A <pkg>` | Manual’s preferred programmatic form for curated platforms |
| Custom triple (when inference is enough) | `import <nixpkgs> { crossSystem = { config = "<cpu>-<vendor>-<os>-<abi>"; }; }` or `--arg crossSystem '{ config = "…"; }'` | Manual notes many cases still need example platforms for sane defaults (tracked upstream); prefer `lib.systems.examples` when a match exists |
| Confirm host config for a `pkgsCross` set | `pkgsCross.<name>.stdenv.hostPlatform.config` | e.g. `aarch64-multiplatform` → `aarch64-unknown-linux-gnu` |

Prefer `localSystem` over the legacy `system` / `platform` import args. Hydra keeps a limited cross jobset (`pkgs/top-level/release-cross.nix`); targets on that list (e.g. `pkgsCross.raspberryPi.hello`) are more likely to fetch a pre-built cross GCC instead of compiling one from source.

### Writing cross-friendly packages

Patterns that keep native and cross evaluation aligned:

- **Sort by role, not by “needed at build time”:** anything executed on the build machine (including code generators and `makeWrapper`) belongs in `nativeBuildInputs`; anything linked into the installed artifact belongs in `buildInputs`.
- **Use stdenv-provided tool names:** cross builds expose prefixed tools (for example `${stdenv.cc.targetPrefix}cc`). Patches or `makeFlags` that hard-code unprefixed `cc`/`ld` break cross.
- **Gate tests on executability:** skip or emulate host-platform tests when the build machine cannot run host binaries—`stdenv.buildPlatform.canExecute stdenv.hostPlatform` is the usual condition; see failure modes for the emulator cookbook.
- **Branch on platform when necessary:** `stdenv.hostPlatform`, `stdenv.buildPlatform`, and predicates from `lib.systems.inspect` are preferred over ad-hoc string checks on `system`.

You do **not** need to pick dependencies from `pkgsBuildHost` / `pkgsHostTarget` by hand in most packages: list them in the correct `*Inputs` attribute and Nixpkgs resolves the right package set when cross-compiling.

Language ecosystems may add their own cross or static helpers on top of this (for example `pkgsStatic` shells); start from [language toolchains](../../11-development/language-toolchains.md) and the packaging surveys, not from inventing per-language cross APIs here.

### Failure modes

| Symptom / mistake | Likely cause | Fix (cookbook / stdenv) |
|-------------------|--------------|-------------------------|
| Works native, fails or links wrong under cross | Tool in `buildInputs` or library in `nativeBuildInputs` | Re-slot; enable `strictDeps = true` to surface lenient native placement |
| Cannot find `cc` / `ar` / `ld` | Build assumes unprefixed binutils | Use `${stdenv.cc.targetPrefix}…` (e.g. `makeFlags = [ "CC=${stdenv.cc.targetPrefix}cc" ]`) |
| Build needs a small C helper that runs on the builder | Missing build→build compiler | `depsBuildBuild = [ buildPackages.stdenv.cc ];` |
| Testsuite / Meson runs host binaries on the builder | Exec format error | `doCheck = stdenv.buildPlatform.canExecute stdenv.hostPlatform;` or add `mesonEmulatorHook` when `!canExecute` |
| Cross GCC rebuilds for hours | Target not on Hydra’s cross jobset / cold cache | Prefer `pkgsCross` attrs covered by `release-cross.nix` when possible |

**Emulation (manual cookbook):** every elaborated platform exposes `hostPlatform.emulator` / `emulatorAvailable`. Dispatch (from the manual) includes a no-op when `canExecute`, `wine` for Windows targets, **`qemu-user` for foreign Linux on a Linux builder**, `wasmtime` for WASI, and others. Prefer those helpers inside `checkPhase` / tests over hand-rolled `qemu` invocations. Outside the sandbox, the manual’s smoke pattern is build then run under the matching user-mode emulator (for many Linux targets, `qemu` from a shell provides `qemu-aarch64` and similar).

**Smoke test a target:** build a known-good package through the chosen cross set before debugging your own:

```bash
nix-build '<nixpkgs>' -A pkgsCross.aarch64-multiplatform.hello
```

(The manual notes this attr is a good cache.nixos.org candidate.) Substitute other `pkgsCross.*` names the same way; for Windows examples the cookbook points at `pkgsCross.mingwW64` with `wine`.

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

Run host tests under the platform emulator when available (manual cookbook):

```nix
stdenv.mkDerivation {
  doCheck = stdenv.hostPlatform.emulatorAvailable buildPackages;
  checkPhase = ''
    ${stdenv.hostPlatform.emulator buildPackages} ./my-binary --self-test
  '';
}
```

Consumer: cross-build GNU Hello for aarch64 Linux (manual / Hydra-friendly attr):

```bash
nix-build '<nixpkgs>' -A pkgsCross.aarch64-multiplatform.hello
```

Equivalent import with an explicit LLVM config (same host as that example):

```nix
let
  pkgs = import <nixpkgs> {
    crossSystem = { config = "aarch64-unknown-linux-gnu"; };
  };
in
pkgs.hello
```

Or pass a curated example platform:

```bash
nix-build '<nixpkgs>' \
  --arg crossSystem '(import <nixpkgs/lib>).systems.examples.aarch64-multiplatform' \
  -A hello
```

## References

- [Cross-compilation](https://nixos.org/manual/nixpkgs/stable/#chap-cross) — Nixpkgs manual (platforms, dependency theory, cookbook, `localSystem` / `crossSystem`)
- [Specifying dependencies](https://nixos.org/manual/nixpkgs/stable/#ssec-stdenv-dependencies) — Nixpkgs manual (`nativeBuildInputs`, `buildInputs`, `strictDeps`, extended slots)
- [Cross-compilation tutorial](https://nix.dev/tutorials/cross-compilation.html) — nix.dev (hands-on `pkgsCross` walkthrough)

## See also

- [Simple package](simple-package.md) — baseline `nativeBuildInputs` / `buildInputs` usage
- [Package sets](../architecture/package-sets.md) — `pkgs`, nested scopes, where `pkgsCross` sits
- [stdenv](../architecture/stdenv.md) — standard environment and phases
- [mkDerivation](../architecture/mkDerivation.md) — derivation attributes and overrides
- [Derivation](../../02-concepts/derivation.md) — primitive below `mkDerivation`
- [Remote builders](../../04-store-and-build/remote-builders.md) — native builds on another machine’s platform (not cross toolchains)
- [Language toolchains](../../11-development/language-toolchains.md) — shells and compilers outside packaging cross slots
