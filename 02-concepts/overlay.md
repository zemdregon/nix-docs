---
status: complete
---

# Overlay

## Overview

An **overlay** is a function that composes modifications on top of a package set. In nixpkgs it has the shape `final: prev: { ... }`: it receives the final fixed-point package set and the result of previous layers, then returns attribute overrides and new packages to merge in.

Overlays are how nixpkgs and NixOS apply set-wide customization without editing the upstream tree. They are the primary mechanism for extending the package graph functionally—see [Functional Package Management](../01-philosophy/functional-package-management.md). For fixed-point mechanics, stacking order, and `extends`, see [Overlays Pattern](../03-language/idioms/overlays-pattern.md). For install paths and longer how-tos, see [Writing Overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md). For package-level tweaks on a single derivation, see [Overlay vs Override](overlay-vs-override.md).

## Details

### Naming (`final` / `prev` vs `self` / `super`)

An overlay is a two-argument function. Newer code uses `final` and `prev`; older code often uses `self` and `super`. The roles are the same either way:

| Argument | Legacy name | Meaning |
| --- | --- | --- |
| `final` | `self` | The composed package set **after** this overlay and all later overlays—the fixed point |
| `prev` | `super` | The set from nixpkgs and overlays **before** this one |

Use **`prev`** for the package you are replacing and for helpers already on the previous stage (`callPackage`, `fetchFromGitHub`, …). Use **`final`** for dependencies of packages you define or override so downstream code in the composed set sees the updated attrs. Swapping the two is a common footgun; see [Overlays Pattern](../03-language/idioms/overlays-pattern.md).

### Composition order

Nixpkgs evaluates overlays **left to right** in the list. Each overlay extends the result of the previous ones. If two overlays both set the same top-level name, the **later** one wins. Put foundational pins (interpreters, BLAS/LAPACK providers, stdenv tweaks) before overlays that depend on those attrs via `final`.

```nix
import <nixpkgs> {
  overlays = [
    (final: prev: { python3 = prev.python312; })          # runs first
    (final: prev: { myApp = prev.myApp.override {        # runs second;
      python3 = final.python3;                            # sees pinned python3
    }; })
  ];
}
```

Under the hood, layers compose with `lib.composeManyExtensions` and `lib.extends`; details are in [Overlays Pattern](../03-language/idioms/overlays-pattern.md).

### Shallow merge pitfall

Overlay results merge with shallow `//`, **not** deep recursion. A later overlay that sets a top-level attr replaces the entire value from an earlier overlay—nested keys are not merged.

```nix
# overlay 1
final: prev: { foo = { a = 1; version = "1.0"; }; }

# overlay 2 — replaces foo entirely; `a` is gone
final: prev: { foo = { b = 2; }; }
# composed top-level foo => { b = 2; } only
```

To keep nested keys, merge manually (`prev.python3.pkgs // { myPkg = ...; }`) or override a specific nested attr instead of replacing the whole parent set. This is the main structural footgun when stacking overlays.

### Where to apply

| Mechanism | Scope / notes |
| --- | --- |
| `import nixpkgs { overlays = [ ... ]; }` | Project or one-off import; **path-based overlay lookup is skipped** when `overlays` is passed |
| `pkgs.extend` / `pkgs.appendOverlays` | Recompute the fixed point on an existing `pkgs`; costly—prefer `overlays` at import time |
| NixOS `nixpkgs.overlays` | System evaluation only; does not affect standalone `nix-env` or ad-hoc `import <nixpkgs>` unless you share the same list |
| `~/.config/nixpkgs/overlays.nix` | User list of overlays (used when `overlays` is **not** passed to import) |
| `~/.config/nixpkgs/overlays/` | Directory of `.nix` files (lexicographic order); **error if both this and `overlays.nix` exist** |
| `<nixpkgs-overlays>` on `NIX_PATH` | Highest-priority path lookup when `overlays` is not passed |

Reuse one overlay list for NixOS and user config when you want `nix-build`, `nix-shell`, and the system to stay aligned. Full install paths and legacy `packageOverrides` are covered in [Writing Overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md).

### Overlays vs overrides

An overlay is **set-level**: it returns a fragment of `pkgs` that nixpkgs folds into the fixed point, so anything resolving through `final.someAttr` picks up your change. `.override` and `.overrideAttrs` are **package-level**: they adjust one derivation's function arguments or `mkDerivation` attrs and return a single new derivation—nothing else in `pkgs` changes unless you wire that value in.

Overlays often *call* `.override` / `.overrideAttrs` on `prev` packages to propagate a tweak set-wide (for example, swapping a BLAS provider or patching `hello` everywhere). See [Overlay vs Override](overlay-vs-override.md).

## Examples

**Pin Python across the set.**

```nix
final: prev: {
  python3 = prev.python312;
}
```

**Override one package's arguments inside an overlay** (same shape as [../meta/examples/overlay-snippet.nix](../meta/examples/overlay-snippet.nix)):

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

**Add a package that depends on the composed set.**

```nix
final: prev: {
  myCli = prev.callPackage ./tools/my-cli.nix {
    inherit (final) lib openssl python3;
  };
}
```

## References

- [Nixpkgs manual — Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays) — chapter overview
- [Nixpkgs manual — Defining overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-definition) — `final` / `prev`, return shape, canonical examples
- [Nixpkgs manual — Installing overlays](https://nixos.org/manual/nixpkgs/stable/#sec-overlays-install) — import, NixOS, path lookup, `overlays.nix`
- [Nixpkgs manual — Overriding](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override) — `.override` and `.overrideAttrs` used inside overlays

## See also

- [Overlay vs Override](overlay-vs-override.md) — set-level vs package-level scope
- [Overlays Pattern](../03-language/idioms/overlays-pattern.md) — fixed point, `extends`, shallow merge, anti-patterns
- [Writing Overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md) — install paths, stacking, NixOS + user config
- [Package Sets](../06-nixpkgs/architecture/package-sets.md) — how `pkgs` is composed
- [Functional Package Management](../01-philosophy/functional-package-management.md) — why overlays fit the model
