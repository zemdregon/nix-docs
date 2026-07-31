---
status: complete
---

# callPackage

## Overview

`callPackage` is a **nixpkgs** helper (`lib.customisation.callPackageWith`), not a language builtin. It turns recipe [functions](../syntax/functions.md) shaped like `{ dep1, dep2, ... }: …` into packages by filling each formal argument from a package set **by name**. The second attribute set supplies overrides or parameters the set cannot provide.

That convention is how nixpkgs stays a library of **parameterised recipes** rather than a pile of fully baked closures: one file per package, dependencies declared as function arguments, auto-wiring at the call site. Results get `.override` (via `makeOverridable`), so callers can re-invoke the same recipe with different arguments. Set-wide changes use [overlays](../../02-concepts/overlay.md); see [overlay vs override](../../02-concepts/overlay-vs-override.md).

## Details

### Recipe as function

Prefer one file per package. Formal arguments name dependencies and helpers from the package set (`stdenv`, `lib`, other packages). The body typically builds with [`mkDerivation`](../../06-nixpkgs/architecture/mkDerivation.md) or a language-specific builder. See [simple package](../../06-nixpkgs/packaging/simple-package.md).

`callPackage` accepts either a path (imported as the function) or an already-loaded function—same auto-fill either way.

### Auto-fill

`pkgs.callPackage ./pkg.nix { }` introspects the recipe with `lib.functionArgs`, intersects those names with the package set (`builtins.intersectAttrs`), and applies `auto // args`. Attributes in the second set win: they override package-set values or supply non-package parameters (for example a string, or a chosen `buildGoModule`).

Arguments that have defaults in the recipe and are **not** present in the auto-fill set keep those defaults unless you pass them in the second set. Names that exist neither on the set nor as defaults must be supplied in `args` or evaluation fails.

### `.override`

`callPackage` wraps the call in `makeOverridable`, so the result usually exposes `.override`: `pkg.override { someDep = other; }` re-runs the recipe with those substitutions merged over the original arguments. That is the usual **single-package** knob.

Do not confuse `.override` (recipe arguments) with `.overrideAttrs` (attributes passed to `mkDerivation`). Both may appear on the same derivation; see [overlay vs override](../../02-concepts/overlay-vs-override.md).

### `callPackageWith`

`lib.callPackageWith autoArgs` returns a `callPackage` whose auto-fill source is `autoArgs` instead of the full `pkgs`. Interdependent local sets use that fixed-point style (laziness lets `packages` refer to itself before it is fully forced—see [laziness](../semantics/laziness.md) and [rec and fixed points](rec-and-fixed-points.md)):

```nix
callPackage = pkgs.lib.callPackageWith (pkgs // packages);
packages = { a = callPackage ./a.nix {}; /* … */ };
```

Manual `inherit a;` into every dependent call works for tiny graphs and becomes error-prone as the set grows; `callPackageWith` is the nixpkgs-scale answer.

There is also `callPackagesWith` / `callPackages` for a recipe that returns an **attribute set** of derivations: `.override` is attached to each leaf, not only the outer set.

### Overlays

In `final: prev: { ... }`, call helpers on `prev` (`prev.callPackage ./pkg { }`) and take dependencies of *new* packages from `final` so they see the composed set. Details: [overlays pattern](overlays-pattern.md). Prefer this over wide `with pkgs;` or ad-hoc `import` sprawl—see [anti-patterns](anti-patterns.md) and [import and fetch](../builtins/import-and-fetch.md).

## Examples

**Bad → good: hand-wiring vs `callPackage`.**

```nix
# avoid — every dependency named twice; easy to drift from the recipe
let
  pkgs = import <nixpkgs> { };
  helloFn = import ./hello.nix;
in
helloFn {
  inherit (pkgs) writeShellScriptBin;
  audience = "people";
}

# prefer — names filled from pkgs; second set is only for overrides / extras
pkgs.callPackage ./hello.nix { audience = "people"; }
```

**Parameter + `.override`** (from [nix.dev](https://nix.dev/tutorials/callpackage.html)):

```nix
# hello.nix
{
  writeShellScriptBin,
  audience ? "world",
}:
writeShellScriptBin "hello" ''
  echo "Hello, ${audience}!"
''

# deps filled from pkgs; second set supplies parameters
pkgs.callPackage ./hello.nix { }
pkgs.callPackage ./hello.nix { audience = "people"; }

# same recipe, later tweak without re-calling callPackage
let
  hello = pkgs.callPackage ./hello.nix { audience = "people"; };
in
hello.override { audience = "folks"; }
```

**Custom set with `callPackageWith`:**

```nix
let
  callPackage = pkgs.lib.callPackageWith (pkgs // packages);
  packages = {
    a = callPackage ./a.nix { };
    b = callPackage ./b.nix { }; # may depend on a by name
  };
in
packages
```

## See also

- [Overlay vs Override](../../02-concepts/overlay-vs-override.md)
- [Overlays Pattern](overlays-pattern.md)
- [Anti-Patterns](anti-patterns.md)
- [Import and fetch](../builtins/import-and-fetch.md)
- [mkDerivation](../../06-nixpkgs/architecture/mkDerivation.md)
- [Rec and Fixed Points](rec-and-fixed-points.md)

## References

- [nix.dev — Package parameters and overrides with `callPackage`](https://nix.dev/tutorials/callpackage.html)
- [Nixpkgs manual — `lib.customisation.callPackageWith`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.customisation.callPackageWith)
- [Nixpkgs manual — Overriding](https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override)
- [Nixpkgs manual — Overlays](https://nixos.org/manual/nixpkgs/stable/#chap-overlays)
