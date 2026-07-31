---
status: complete
---

# rec and Fixed Points

## Overview

`rec { … }` makes attribute names available inside the same set so definitions can refer to each other. The same idea, made explicit, is a fixed point: compute `x` such that `x = f x`. Nixpkgs builds package sets and overlays on that pattern — `lib.fix`, `extends`, and friends — so layers can see both the previous package set and the final one. Prefer `let … in` over `rec` when the goal is only local binding clarity; use fixed-point functions when you need extension and override.

## Details

### Recursive attribute sets

In a normal attrset, names on the left are not in scope on the right. With `rec`, they are:

```nix
rec {
  foo = "foo";
  foobar = foo + "bar";
}
```

That is the same idea as naming the set and referring through the name:

```nix
let
  self = {
    foo = "foo";
    foobar = self.foo + "bar";
  };
in
  self
```

Without `rec`, `foobar = foo` would look only at the surrounding lexical scope.

### Infinite recursion and shadowing

Mutual self-reference that never bottoms out fails:

```nix
rec {
  x = y;
  y = x;
}.x
# → infinite recursion encountered
```

A subtler trap is shadowing an outer binding: the RHS of an attr in `rec` binds to the attr being defined, not the outer `let`:

```nix
let a = 1; in rec { a = a; }
# → infinite recursion (RHS `a` is the attr, not the let)
```

[nix.dev best practices](https://nix.dev/guides/best-practices.html) recommend avoiding `rec` and using `let … in` instead, naming the set when you need self-reference (`argset.a` rather than bare `a`).

### When `let` is clearer than `rec`

Use `let` when attributes need outer values but do not need to form an overridable fixed point:

```nix
let
  a = 1;
in {
  a = a;
  b = a + 2;
}
```

`rec` is fine for small self-contained examples, but it makes name resolution harder to read and easy to break by accident. Once the set must be extended (overlays, package overrides), switch to an explicit `f: …` fixed-point function instead of growing a `rec`.

### `lib.fix` — explicit fixed points

`lib.fix f` returns `x` such that `x = f x`. `f` must be lazy: it should produce a value that can be partially evaluated (attrset, list, or function) so one part of `x` can be used while defining another:

```nix
lib.fix (self: {
  foo = "foo";
  foobar = self.foo + "bar";
})
```

Under the hood this is `let self = f self; in self`. Mutual recursion among packages, and tools like [`callPackage`](callPackage.md), rely on [laziness](../semantics/laziness.md): selecting one attr does not force the whole set.

### Overlays as layers on fixed points

An overlay is `final: prev: { … }`. `extends overlay f` wraps a fixed-point function `f`; `lib.fix (extends overlay f)` evaluates the composed stage:

- `final` — the result after all overlays in this composition
- `prev` — the previous stage (before this overlay)

That is how nixpkgs package sets grow: base `pkgs` as `final: { … }`, then overlays that can both replace packages (`prev.foo`) and depend on the eventual set (`final.bar`). See [overlays pattern](overlays-pattern.md) and [overlay (concept)](../../02-concepts/overlay.md).

### `fix'`, `makeExtensible`, composition

| Helper | Role |
|--------|------|
| `fix'` | Like `fix`, but stores the original recursive function as `__unfix__` — used for deep override |
| `makeExtensible` | Fixed point plus an `.extend` method for applying overlays later |
| `composeManyExtensions` | Compose a list of overlays into one; merge is shallow `//` (nested attrs are replaced, not deep-merged) |

`composeExtensions` does the two-overlay case; `composeManyExtensions` is the list form used when stacking many overlays in order.

## Examples

**`rec` vs explicit self:**

```nix
# syntactic
rec { x = 1; y = x + 1; }

# equivalent explicit naming
let self = { x = 1; y = self.x + 1; }; in self
```

**Prefer `let` to avoid shadowing:**

```nix
# fragile
let a = 1; in rec { a = a + 1; }  # infinite recursion

# clear
let a = 1; in { a = a + 1; }      # { a = 2; }
```

**Fixed point + overlay:**

```nix
let
  inherit (lib) fix extends;
  f = final: {
    a = 1;
    b = final.a + 2;
  };
  overlay = final: prev: {
    a = prev.a + 10;
    c = final.a + final.b;
  };
in
  fix (extends overlay f)
# → { a = 11; b = 13; c = 24; }
```

**Composable overlays (shallow `//`):** later overlays see earlier ones as `prev`; `final` sees the whole stack. Nesting is not deep-merged unless an overlay reconstructs nested keys itself.

## See also

- [Lists and attrsets](../syntax/lists-and-attrsets.md)
- [let-in and with](../syntax/let-in-and-with.md)
- [Laziness](../semantics/laziness.md)
- [Scoping and shadowing](../semantics/scoping-and-shadowing.md)
- [Overlays pattern](overlays-pattern.md)
- [callPackage](callPackage.md)
- [Overlay (concept)](../../02-concepts/overlay.md)

## References

- [Language syntax — Recursive sets (Nix manual)](https://nix.dev/manual/nix/stable/language/syntax.html#recursive-sets)
- [lib.fixedPoints (nixpkgs manual)](https://nixos.org/manual/nixpkgs/stable/#sec-functions-library-fixedPoints) — `fix`, `extends`, `composeManyExtensions`
- [Best practices — `rec` / `with` (nix.dev)](https://nix.dev/guides/best-practices.html)
- [nixpkgs `lib/fixed-points.nix`](https://github.com/NixOS/nixpkgs/blob/master/lib/fixed-points.nix)
