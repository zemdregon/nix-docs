---
status: complete
---

# let-in and with

## Overview

Nix provides two scoping constructs beyond function parameters and attribute sets: **let-in** for local bindings, and **with** for bringing an attribute set's fields into lexical scope. Both support `inherit` and `inherit (set)` like [attrset](lists-and-attrsets.md) definitions. Prefer `let` when you need named locals — it is explicit about which names exist. Reserve `with` for short scopes where the set is obvious; mixed `let`/`with` shadowing is easy to misread (see below and [scoping and shadowing](../semantics/scoping-and-shadowing.md)).

## Details

### let-in

A let-expression binds one or more names, then evaluates a body:

```nix
let
  x = "foo";
  y = "bar";
in x + y
```

This evaluates to `"foobar"`. Bindings in the same `let` block share scope: later bindings may refer to earlier ones, and all bindings may refer to each other mutually (similar to `rec` within that block). The body may use any of the let-bound names.

`inherit` and `inherit (src-set) a b …` work in `let` the same way they do in attribute sets — they copy names from the surrounding scope or from another set into the let block.

### Obsolete `let { … body = …; }` form

An older syntax wraps bindings in a recursive attribute set with a mandatory `body` attribute:

```nix
let {
  foo = bar;
  bar = "baz";
  body = foo;
}
```

This evaluates to `"baz"`. The form is recursive (like `rec { … }`) and should not be used in new code. Prefer `let … in …`.

### with

A with-expression introduces the attributes of its first operand into the scope of its second:

```nix
with e1; e2
```

If `e1` evaluates to an attribute set, the names of that set become available when evaluating `e2`:

```nix
let as = { x = "foo"; y = "bar"; };
in with as; x + y
```

This evaluates to `"foobar"`. A common pattern is `with (import ./defs.nix); …`, which makes attributes from that file available as if they were local `let` bindings.

### Prefer let for clarity

`let` lists every introduced name next to its definition. `with` dumps an entire set into scope, so readers (and tools) cannot tell at a glance which free names came from the set versus outer bindings. Prefer `let inherit (set) a b;` or explicit `let a = set.a;` when only a few names are needed. Prefer `set.attr` selection when a single use is enough.

### Shadowing rules

Bindings from `with` do **not** shadow bindings introduced by other means — `let`, function parameters, and other non-`with` bindings always win. For example, the manual states that:

```nix
let a = 3; in with { a = 1; }; let a = 4; in with { a = 2; }; …
```

is equivalent to:

```nix
let a = 1; in let a = 2; in let a = 3; in let a = 4; in …
```

Rewritten as nested `let`s, the with layers become the outer bindings (`a = 1`, then `a = 2`), and the explicit `let`s sit closer to the body (`a = 3`, then `a = 4`), so `a` resolves to `4`. In short: non-with bindings take priority over with bindings because they end up inner in the equivalent nested-let form.

Nested `with` expressions **do** shadow outer `with` bindings — the inner set's attributes hide same-named attributes from an outer `with`.

Pitfall: a typo or renamed attribute in a `with` set can silently pick up an outer binding of the same name instead of failing, because the `with` binding never overrides that outer name. See [scoping and shadowing](../semantics/scoping-and-shadowing.md) for the full picture.

## Examples

Local helpers with mutual reference (verified: `"2.1"`):

```nix
let
  minor = 1;
  major = minor + 1;
in "${toString major}.${toString minor}"
```

Inherit from an outer scope inside `let` (verified: `{ x = 123; y = 456; }`):

```nix
let x = 123;
in let
  inherit x;
  y = 456;
in { inherit x y; }
```

Non-with binding wins over `with` (verified: `"from-let"`):

```nix
let a = "from-let";
in with { a = "from-with"; }; a
```

Inner `with` shadows outer `with` (verified: `"inner"`):

```nix
with { a = "outer"; };
with { a = "inner"; };
a
```

Selective inherit instead of a broad `with` (verified: `{ names = [ "a" "b" ]; }`):

```nix
let
  x = { a = 1; b = 2; };
  inherit (builtins) attrNames;
in
{
  names = attrNames x;
}
```

## See also

- [Lists and attrsets](lists-and-attrsets.md) — attrset syntax and `inherit`
- [Functions](functions.md) — parameter bindings and default values
- [Scoping and shadowing](../semantics/scoping-and-shadowing.md) — let/with interaction in depth
- [Anti-patterns](../idioms/anti-patterns.md) — when to avoid `with`

## References

- [Nix language syntax — let, inherit, with](https://nix.dev/manual/nix/stable/language/syntax.html)
