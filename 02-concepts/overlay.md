---
status: complete
---

# Overlay

## Overview

An **overlay** is a function that composes modifications on top of a package set. In nixpkgs it has the shape `final: prev: { ... }`: it receives the final fixed-point package set and the result of previous layers, then returns attribute overrides and new packages to merge in.

Overlays are how nixpkgs and NixOS apply set-wide customization without editing the upstream tree. They are the primary mechanism for extending the package graph functionally—see [Functional Package Management](../01-philosophy/functional-package-management.md). For package-level tweaks on a single derivation, see [Overlay vs Override](overlay-vs-override.md).

## Details

**Shape and naming.** An overlay is a two-argument function. Newer code uses `final` and `prev`; older code often uses `self` and `super`. Use `final` for dependencies of packages you define in the overlay (the composed set). Use `prev` to refer to packages from earlier layers or to call nixpkgs helpers such as `callPackage`.

**Composition.** Nixpkgs evaluates overlays in order; each overlay extends the result of the previous ones. Later overlays replace top-level attributes from earlier ones unless they explicitly reference `prev`. Nested attribute sets are not merged recursively—`{ foo = { a = 1; }; }` followed by `{ foo = { b = 2; }; }` replaces `foo` entirely.

**Where they apply.** Pass overlays when importing nixpkgs (`import nixpkgs { overlays = [ ... ]; }`), via `pkgs.extend`, or on NixOS through `nixpkgs.overlays`. User-level overlays can live in `~/.config/nixpkgs/overlays.nix` or under `~/.config/nixpkgs/overlays/`.

**Relationship to overrides.** Overlays often *use* `.override` or `.overrideAttrs` on individual packages inside the returned set—for example, to swap a BLAS provider across the whole set. The overlay is the set-level composition layer; overrides are the package-level building blocks. See [Overlay vs Override](overlay-vs-override.md).

## Examples

**Pin Python across the set.**

```nix
final: prev: {
  python3 = prev.python312;
}
```

**Override one package's arguments inside an overlay.**

```nix
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    pname = old.pname + "-patched";
  });
}
```

**Apply overlays when importing nixpkgs.**

```nix
import <nixpkgs> {
  overlays = [
    (final: prev: { myTool = prev.callPackage ./my-tool.nix { }; })
  ];
}
```

## References

- [Nixpkgs manual — Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays) — defining, installing, and composing overlays
- [Nixpkgs manual — Overriding](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override) — `.override` and `.overrideAttrs` used inside overlays

## See also

- [Overlay vs Override](overlay-vs-override.md)
- [Functional Package Management](../01-philosophy/functional-package-management.md)
- [Writing Overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md)
- [Overlays Pattern](../03-language/idioms/overlays-pattern.md)
