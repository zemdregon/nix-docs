---
status: complete
---

# Lists and Attrsets

## Overview

Lists and attribute sets are the two composite value types in the Nix language. Lists hold ordered sequences of values; attribute sets hold named fields. Both appear throughout Nixpkgs and NixOS configuration, and most [functions](functions.md) take or return one of these shapes.

## Details

### Lists

A list is written with square brackets and **whitespace-separated** elements (no commas):

```nix
[ 123 ./foo.nix "abc" (f { x = y; }) ]
```

Function calls inside a list must be parenthesized. Without parentheses, `[ f { x = y; } ]` is a five-element list (function, then set), not a call result.

Lists are **lazy in element values** (elements are not evaluated until needed) but **strict in length** (the list structure is known at construction). Index with `builtins.elemAt`; concatenate with `++` (see [operators](operators.md)):

```nix
builtins.elemAt [ "a" "b" "c" ] 1  # => "b"
[ 1 2 ] ++ [ 3 4 ]                 # => [ 1 2 3 4 ]
```

### Attribute sets

An attribute set is `{ name = expr; ... }`. Names must be unique within a set; **order is irrelevant**. Values are arbitrary expressions, each terminated by `;`.

Nested structure can be written inline with **attribute paths**:

```nix
{ a.b.c = 1; a.b.d = 2; }
```

is equivalent to `{ a = { b = { c = 1; d = 2; }; }; }`.

### Selection and membership

- **Select:** `set.attr` — missing attributes are an error unless a default is given: `set.attr or default`.
- **Has attribute:** `set ? attrpath` — tests whether the path exists (see [operators](operators.md)).

Attribute names can be string literals or identifiers. **String interpolation** works in both selection and definition:

```nix
let bar = "foo"; in { ${bar} = 123; }.foo  # => 123
```

If an interpolated name evaluates to `null`, that attribute is **omitted** rather than raising an error:

```nix
{ ${if false then "bar" else null} = true; }  # => {}
```

### Update (`//`)

`left // right` merges two attribute sets. The result has every attribute from either side; on duplicate names, the **right** operand wins. The merge is **shallow**: nested sets under the same key are replaced wholesale, not deep-merged.

```nix
{ a = 1; b = 2; } // { b = 3; c = 4; }  # => { a = 1; b = 3; c = 4; }
```

Both operands are forced to WHNF before the merge; attribute *values* inside are not forced by `//` itself. Details and precedence: [operators](operators.md).

### `rec`, `inherit`, and callable sets

**Recursive sets** (`rec { ... }`) put each attribute in scope for the others, like a mutual [let-in](let-in-and-with.md) binding. Without `rec`, `x = y;` refers to `y` in the surrounding scope, not another field in the same set. Unbounded mutual references cause infinite recursion at evaluation time.

**`inherit`** desugars to ordinary bindings:

```nix
inherit x;              # => x = x;
inherit (src) a b;      # => a = src.a; b = src.b;
```

A set with a **`__functor`** attribute whose value is callable can be applied like a function; the set itself is passed as the first argument:

```nix
let add = { __functor = self: x: x + self.x; };
    inc = add // { x = 1; };
in inc 1   # => 2  (like add.__functor add 1)
```

This pattern attaches metadata to callable values without special-casing callers.

## Examples

Minimal list and set:

```nix
{
  items = [ "nginx" "postgres" ];
  cfg = {
    host = "localhost";
    port = 5432;
  };
}
```

`rec` so attributes refer to each other (see [rec and fixed points](../idioms/rec-and-fixed-points.md)):

```nix
rec { x = y; y = 123; }.x  # => 123
```

`inherit` from the surrounding scope and from another set:

```nix
let x = 123; src = { a = 1; b = 2; };
in { inherit x; inherit (src) a b; }  # => { x = 123; a = 1; b = 2; }
```

Dynamic attribute name with conditional omission:

```nix
let enableFeature = true;
    name = if enableFeature then "feature" else null;
in { ${name} = true; }  # => { feature = true; }
```

Shallow merge (nested keys under `a` are replaced, not combined):

```nix
{ a = { b = 1; }; } // { a = { c = 3; }; }  # => { a = { c = 3; }; }
```

## See also

- [Functions](functions.md) — set patterns and argument destructuring
- [Let-in and with](let-in-and-with.md) — lexical scope vs `rec` and `inherit`
- [Operators](operators.md) — selection, `or`, `?`, `//`, `++`
- [Attrset, list, string builtins](../builtins/attrset-list-string.md) — `elemAt`, `attrNames`, …
- [Rec and fixed points](../idioms/rec-and-fixed-points.md) — recursive attrsets in practice
- [Overlay](../../02-concepts/overlay.md) — merging sets with `//` in overlays

## References

- [Nix manual — Language constructs (lists, attrsets, rec, inherit)](https://nix.dev/manual/nix/stable/language/syntax.html)
- [Nix manual — Data types](https://nix.dev/manual/nix/stable/language/types.html)
- [Nix manual — Operators (selection, `?`, `//`, `++`)](https://nix.dev/manual/nix/stable/language/operators.html)
