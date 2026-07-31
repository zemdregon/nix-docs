---
status: complete
---

# Overlay vs Override

## Overview

**Overlays** and **overrides** both customize nixpkgs, but at different scopes. An [overlay](overlay.md) is a set-level function `final: prev: { ... }` that composes changes across the whole package graph. An **override** (`.override` or `.overrideAttrs`) adjusts one package's function arguments or `mkDerivation` attributes and returns a single new derivation.

Choose overlays when many packages—or everything that depends on a shared dependency—must see the same change. Choose overrides for local, one-off tweaks to a specific package. The two compose naturally: overlays often call `.override` / `.overrideAttrs` on `prev` packages to propagate a change set-wide.

## Details

**Override — single package.** `.override` re-invokes the package function with different arguments (for example, enabling an optional feature). `.overrideAttrs` changes the attribute set passed to `stdenv.mkDerivation` (patches, `buildInputs`, `pname`, and so on). Both return one derivation; nothing else in `pkgs` changes unless you wire that derivation in yourself.

**Overlay — package set.** An overlay returns a partial attribute set that nixpkgs merges into the fixed point. Anything that reads `final.someAttr` after composition picks up your change—useful for swapping BLAS/LAPACK providers, pinning `python3`, or adding a new package that other overlays can depend on via `final`.

**When to use which.**

| Goal | Prefer |
| --- | --- |
| Change one package for a single `callPackage`, shell, or module | `.override` / `.overrideAttrs` |
| Replace a dependency everywhere it is pulled from `pkgs` | Overlay (often calling `.override` inside) |
| Add a new package to the set | Overlay |
| Patch `hello` once in a dev shell | `.overrideAttrs` |
| Pin `python3` for the whole system or project | Overlay |

**Composition.** Overrides nest: `pkg.override { ... }.overrideAttrs { ... }`. Overlays stack in list order; later overlays replace top-level attrs with shallow merge—nested attrsets are not merged recursively (see [Overlay](overlay.md)). A common pattern is an overlay that overrides several related attributes so downstream packages stay consistent—see the nixpkgs manual's BLAS/LAPACK examples.

Shared overlay fixture: [overlay-snippet.nix](../meta/examples/overlay-snippet.nix) in the [example corpus](../meta/examples/README.md).

**Legacy note.** `packageOverrides` is an older, less flexible hook equivalent to an overlay with only `prev`. Prefer overlays for anything you might share or layer.

### Boundaries (what this page is not)

- **Not overlay composition theory** — stacking order and shallow merge are [overlay](overlay.md) and [overlays pattern](../03-language/idioms/overlays-pattern.md).
- **Not `callPackage` mechanics** — argument threading is [callPackage](../03-language/idioms/callPackage.md).
- **Not legacy `packageOverrides` migration** — see [packageOverrides](../06-nixpkgs/overlays-and-overrides/packageOverrides.md).

## Examples

**Override — local patch to one package.**

```nix
pkgs.hello.overrideAttrs (old: {
  patches = (old.patches or [ ]) ++ [ ./hello-fix.patch ];
})
```

**Overlay — same change visible set-wide.**

```nix
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    patches = (old.patches or [ ]) ++ [ ./hello-fix.patch ];
  });
}
```

**Override inside `callPackage` — only this build sees it.**

```nix
pkgs.callPackage ./my-app.nix {
  openssl = pkgs.openssl.override { ... };
}
```

**Overlay — swap a shared provider for all dependents.**

```nix
final: prev: {
  blas = prev.blas.override { blasProvider = final.mkl; };
  lapack = prev.lapack.override { lapackProvider = final.mkl; };
}
```

## References

- [Nixpkgs manual — Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays) — set-level composition
- [Nixpkgs manual — Overriding](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override) — `.override`, `.overrideAttrs`, and using overrides inside overlays

## See also

- [Overlay](overlay.md)
- [Functional Package Management](../01-philosophy/functional-package-management.md)
- [Writing Overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md)
- [Overlays Pattern](../03-language/idioms/overlays-pattern.md)
- [callPackage](../03-language/idioms/callPackage.md)
- [packageOverrides](../06-nixpkgs/overlays-and-overrides/packageOverrides.md)
- [overlay-snippet.nix](../meta/examples/overlay-snippet.nix) — corpus fixture
- [Example corpus](../meta/examples/README.md)
