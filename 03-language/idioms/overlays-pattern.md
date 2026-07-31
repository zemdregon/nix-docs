---
status: complete
---

# Overlays Pattern

## Overview

An **overlay** is a two-argument function `final: prev: { ... }` that returns a fragment of a package set—replacements and new attributes. Nixpkgs folds a list of overlays into one [fixed-point](rec-and-fixed-points.md) set: layers compose **left to right**, each stage sees earlier results as `prev`, and `final` is the completed fixed point after every layer.

This page is the **language / nixpkgs composition idiom**—`final` vs `prev`, stacking order, shallow merge, and `extends` / `composeManyExtensions`. It is not the same as `.override` / `.overrideAttrs`, which change one package and return a single derivation; see [Overlay vs Override](../../02-concepts/overlay-vs-override.md). For the concept and when to reach for overlays, see [Overlay](../../02-concepts/overlay.md). For install paths and longer how-tos, see [Writing overlays](../../06-nixpkgs/overlays-and-overrides/writing-overlays.md).

## Details

### Shape

Newer code names the arguments `final` / `prev`; older code often uses `self` / `super`. Same roles either way. The return value should look like a slice of `pkgs` (top-level names to derivations or nested sets), similar in spirit to `pkgs/top-level/all-packages.nix`.

### `final` vs `prev`

| Argument | Meaning | Use for |
| --- | --- | --- |
| `final` | The composed set after this overlay **and** all later overlays (the fixed point) | Dependencies of packages you define or override |
| `prev` | The set from nixpkgs and overlays **before** this one | The package you are replacing; helpers already on the previous stage (`callPackage`, …) |

Canonical pattern from the nixpkgs manual—take the original recipe and helpers from `prev`, resolve dependencies against `final`:

```nix
final: prev: {
  boost = prev.boost.override { python = final.python3; };
  rr = prev.callPackage ./pkgs/rr { stdenv = final.stdenv_32bit; };
}
```

`prev` does not contain attributes introduced by this overlay or by later ones. `final` does—laziness makes that safe (see [Laziness](../semantics/laziness.md)). Swapping the two is a common footgun; see [Anti-patterns](anti-patterns.md).

### Composition

Overlays in a list apply in order. Later overlays replace **top-level** attrs from earlier ones. Nested attrsets are not merged recursively—composition uses `//` (shallow). To keep nested keys, merge manually (`prev.python3.pkgs // { ... }`) or override a specific attr.

Under the hood, `lib.extends overlay f` builds a new fixed-point function; `lib.fix` evaluates it. Several overlays stack with `lib.composeManyExtensions` (or `composeExtensions` for two). List order matches `overlays = [ ... ]`.

### Overlay vs override

`.override` re-invokes a package function with different arguments; `.overrideAttrs` changes the `mkDerivation` attrset. Both return **one** derivation. An overlay wires such changes into the package set so everything that reads `final.someAttr` sees them. Prefer overlays for set-wide consistency; prefer a bare override for a one-off in a shell or module. Details: [Overlay vs Override](../../02-concepts/overlay-vs-override.md).

### Where to apply

- `import nixpkgs { overlays = [ ... ]; }` — when `overlays` is passed, nixpkgs does **not** look up path-based overlay files
- NixOS: `nixpkgs.overlays` (system evaluation only; does not affect standalone `nix-env` / ad-hoc imports unless you share the same list)
- User path lookup (only if `overlays` was not passed): `<nixpkgs-overlays>` on `NIX_PATH`, else `~/.config/nixpkgs/overlays.nix` **or** `~/.config/nixpkgs/overlays/` (error if both exist)
- Runtime: `pkgs.extend` / `appendOverlays` — these recompute the fixed point and are costly; avoid inside nixpkgs itself

### `packageOverrides`

The older [`config.packageOverrides`](../../06-nixpkgs/overlays-and-overrides/packageOverrides.md) is roughly an overlay that only sees `prev`. Prefer overlays.

## Examples

**Minimal concrete overlay** (same shape as the nixpkgs Overlays chapter):

```nix
final: prev: {
  hello = prev.hello.overrideAttrs (old: {
    pname = old.pname + "-patched";
  });
  myTool = prev.callPackage ./my-tool.nix { };
}
```

Wire it in with `import nixpkgs { overlays = [ thatOverlay ]; }` or NixOS `nixpkgs.overlays`. Dependents that resolve through the composed set see `hello` / `myTool` from `final`.

**Fixed-point composition** (from `lib.fixedPoints`; verified with `nix-instantiate --eval --strict`):

```nix
f = final: { a = 1; b = final.a + 2; };

# lib.fix f => { a = 1; b = 3; }
# after overlay:
lib.fix (lib.extends (final: prev: { a = prev.a + 10; }) f)
# => { a = 11; b = 13; }
```

`a` is updated via `prev`; `b` still depends on `final.a`, so it picks up `11`. Stacking more layers is the same idea with `lib.composeManyExtensions [ ov1 ov2 ... ]` before `extends`.

**Shallow merge pitfall** (`composeManyExtensions` uses `//`):

```nix
# later overlay replaces the whole attr — nested keys from earlier are gone
final: prev: { foo = { b = 2; }; }
# if an earlier overlay set foo = { a = 1; }, result is only { b = 2; }
```

## See also

- [Overlay](../../02-concepts/overlay.md) — definition and when to use overlays
- [Overlay vs Override](../../02-concepts/overlay-vs-override.md) — set-level vs package-level
- [callPackage](callPackage.md) — usual way to introduce packages inside an overlay
- [Anti-patterns](anti-patterns.md) — `final`/`prev` mixups, shallow `//`, costly `extend`
- [rec and Fixed Points](rec-and-fixed-points.md) — `fix` / recursive sets without overlays
- [Writing overlays](../../06-nixpkgs/overlays-and-overrides/writing-overlays.md) — install paths and longer nixpkgs guide

## References

- [Nixpkgs Manual — Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays)
- [lib.fixedPoints (`fix`, `extends`, `composeManyExtensions`)](https://nixos.org/manual/nixpkgs/stable/#sec-functions-library-fixedPoints)
- [nixpkgs `lib/fixed-points.nix`](https://github.com/NixOS/nixpkgs/blob/master/lib/fixed-points.nix)
