---
status: complete
---

# Patches and Overrides

## Overview

**Patches** change upstream source before the build runs. In nixpkgs they are usually listed in the `patches` attribute on [`mkDerivation`](../architecture/mkDerivation.md); [`patchPhase`](../../04-store-and-build/build-phases.md) applies each entry after unpack. **Overrides** customize an already-defined package without editing nixpkgs: `.override` changes the package function’s arguments, `.overrideAttrs` changes attributes passed to `mkDerivation`, and [overlays](../overlays-and-overrides/writing-overlays.md) apply changes across the whole package set.

Use overrides for local or experimental fixes; upstream durable fixes belong as patches inside the nixpkgs expression (or as PRs to nixpkgs). See [Overlay vs Override](../../02-concepts/overlay-vs-override.md) for scope: one package versus the entire `pkgs` fixed point.

## Details

### The `patches` attribute

Set `patches` to a list of patch files. During `patchPhase`, stdenv runs `patch -p1` on each file in order (unless `dontPatch = true`). Entries can be:

- **Local paths** — `./fix-build.patch` next to `default.nix`, or paths under `nix/` in a flake.
- **Fetched patches** — `fetchpatch` / `fetchpatch2` for remote URLs with a fixed-output hash (same idea as `fetchurl` for sources).

Patches must apply cleanly to the unpacked `src`. If upstream changes line context, the build fails at patch time rather than silently building broken code.

**`postPatch`.** Shell hook run at the end of `patchPhase`, after all `patches` are applied. Use it for small sed rewrites or generated fixes that are awkward as standalone patch files—not as a substitute for upstreamable diffs when a patch file would be clearer.

### `.override` vs `.overrideAttrs`

Both return a new package value; neither mutates nixpkgs.

| Mechanism | What it changes | Typical use |
| --- | --- | --- |
| `.override { … }` | Arguments to the package function (from `callPackage`) | Enable optional features, swap a dependency argument |
| `.overrideAttrs (old: { … })` | Attributes passed to `stdenv.mkDerivation` | Add patches, change `version`/`src`/`hash`, tweak `buildInputs`, set `postPatch` |

Prefer `.overrideAttrs` over the legacy `.overrideDerivation`: `overrideAttrs` re-runs attribute processing inside `mkDerivation` so dependency lists, structured attrs, and stdenv helpers stay consistent. See the manual’s [overrideAttrs](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-overrideAttrs) section.

**Nesting.** `pkg.override { … }.overrideAttrs (old: { … })` is common: first adjust callPackage args, then adjust derivation attrs. Inside `overrideAttrs`, merge with `(old.patches or [ ]) ++ [ … ]` so you do not drop upstream patches.

### Overlays vs one-off overrides

An overlay replaces or wraps a package for every consumer of `pkgs` that goes through the composed fixed point. A bare `.overrideAttrs` in a dev shell or module affects only that reference unless you assign it back into an overlay yourself.

Rule of thumb: patch `hello` once in a shell → `.overrideAttrs`. Pin or patch a library everywhere it is pulled from `pkgs` → overlay (often calling `.overrideAttrs` on `prev.thatPackage`). Details: [writing overlays](../overlays-and-overrides/writing-overlays.md).

### `fetchpatch` and `fetchpatch2`

Remote patches should be fixed-output fetches so the hash pins content:

```nix
fetchpatch {
  url = "https://github.com/org/repo/pull/123.patch";
  hash = "sha256-…";
}
```

`fetchpatch2` is the same helper with a newer `patchutils` (hash-incompatible with `fetchpatch`). Prefer `fetchpatch2` for new remote patches; keep `fetchpatch` when matching an existing hash. The fetcher API is documented under [fetchpatch](https://nixos.org/manual/nixpkgs/stable/#fetchpatch).

### Local overrides vs upstreaming

| Approach | When |
| --- | --- |
| `.overrideAttrs` in a flake, shell, or NixOS module | Quick fix, private fork, or waiting on an upstream release |
| Patch file + PR to nixpkgs | Fix benefits all users; version/hash live with the package |
| Upstream project accepts the patch | Drop the nixpkgs patch on the next version bump |

Local overrides do not require a nixpkgs PR but duplicate maintenance: every bump of the base package may break your patch or override. Upstreamed patches ride with `version`/`src` updates in nixpkgs and show up in `nix-update`/`maint-scripts` workflows.

## Examples

**Add a local patch to an existing package.**

```nix
pkgs.someApp.overrideAttrs (old: {
  patches = (old.patches or [ ]) ++ [ ./0001-fix-build.patch ];
})
```

**Fetch a remote patch with a pinned hash.**

```nix
pkgs.openssl.overrideAttrs (old: {
  patches = (old.patches or [ ]) ++ [
    (fetchpatch2 {
      url = "https://example.com/openssl-fix.patch";
      hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
    })
  ];
})
```

**Override version and source (e.g. pre-release).**

```nix
pkgs.myTool.overrideAttrs (old: {
  version = "2.0-rc1";
  src = fetchFromGitHub {
    owner = "org";
    repo = "my-tool";
    rev = "v2.0-rc1";
    hash = "sha256-…";
  };
  patches = [ ]; # drop patches that only applied to the old version
})
```

**`postPatch` tweak after standard patches.**

```nix
pkgs.foo.overrideAttrs (old: {
  postPatch = (old.postPatch or "") + ''
    substituteInPlace Makefile --replace '-O2' '-O1'
  '';
})
```

**Package definition with bundled patches** (see also [simple package](simple-package.md)):

```nix
stdenv.mkDerivation (finalAttrs: {
  pname = "example";
  version = "1.0";
  src = fetchurl { url = "…"; hash = "…"; };
  patches = [
    ./0001-upstream-fix.patch
    (fetchpatch2 { url = "…"; hash = "…"; })
  ];
})
```

## See also

- [Overlay vs Override](../../02-concepts/overlay-vs-override.md) — scope: single package vs whole set
- [Writing overlays](../overlays-and-overrides/writing-overlays.md) — set-level customization
- [mkDerivation](../architecture/mkDerivation.md) — constructor and `overrideAttrs`
- [Build phases](../../04-store-and-build/build-phases.md) — `patchPhase` in the default pipeline
- [Simple package](simple-package.md) — minimal packaging walkthrough

## References

- [Overrides and extensions](https://nixos.org/manual/nixpkgs/stable/#chap-overrides) — nixpkgs manual chapter
- [`.override`](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override) — changing callPackage arguments
- [`.overrideAttrs`](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-overrideAttrs) — changing mkDerivation attributes
- [`patchPhase`](https://nixos.org/manual/nixpkgs/stable/#ssec-patch-phase) — when and how patches run
- [`fetchpatch`](https://nixos.org/manual/nixpkgs/stable/#fetchpatch) — fixed-output patch fetchers (`fetchpatch2` is the newer variant in nixpkgs)
