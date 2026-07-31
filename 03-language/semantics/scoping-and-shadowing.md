---
status: complete
---

# Scoping and Shadowing

## Overview

Nix uses **lexical scoping**: a name resolves to the binding established by the nearest enclosing construct that introduced it. Functions, `let`, and `rec` attribute sets add names to the lexical environment; normal attribute sets do not. The `with` expression is a special case — it adds **soft** bindings that can be overridden by `let`, function parameters, and other non-`with` bindings.

Understanding which constructs introduce bindings — and which merely read values — prevents subtle name-resolution bugs in large expressions and nixpkgs-style call patterns.

## Details

### What introduces lexical bindings

| Construct | Names in scope |
|-----------|----------------|
| Function `{ x, y ? x }: …` | Pattern names (and `@`-pattern names) for the **entire** function expression, including default values |
| `let … in …` | All let-bound names in the let block and in the body |
| `rec { … }` | Attribute names refer to each other inside the set |
| `{ … }` (non-`rec`) | Attribute names are **not** in lexical scope outside attribute values |
| `with set; body` | Set attributes available in `body` only (soft bindings) |
| `inherit` / `inherit (src) …` | Copies names into a `let` or attrset definition from outer scope or `src` |
| `set.${name}` | **Not** a binding — dynamic attribute **selection** only |

### Normal attrsets vs `rec`

In a non-recursive attribute set, `x = y;` refers to `y` from the **surrounding** lexical scope (if any), not to another attribute in the same set:

```nix
let y = 10; in { x = y; }.x   # => 10
```

Without an outer `y`, `{ x = y; }` is a free-variable error. With `rec`, attributes are added to the lexical scope of the set body:

```nix
rec { x = y; y = 123; }.x     # => 123
```

See [lists and attrsets](../syntax/lists-and-attrsets.md) for construction syntax.

### Function pattern scope

All bindings from a function pattern are visible throughout the function expression — not only in the body after `:`:

```nix
{ x, y ? [ x ] }: { inherit y; }
```

Here `y`'s default `[ x ]` may refer to `x` because both are in the same pattern scope. The same applies to `@`-patterns: `args` is bound to the argument as passed (defaults applied only when the body reads the corresponding name).

See [functions](../syntax/functions.md) for pattern forms and default-value semantics.

### `inherit`

Inside a `let` block or attribute set, `inherit foo;` is shorthand for `foo = foo;`, copying from the **outer** lexical scope. `inherit (set) a b;` copies `set.a` and `set.b`. This only works because the surrounding `let` (or the fact that you are defining bindings) puts the right-hand names in scope.

### `with`: soft bindings and shadowing

A `with set; body` expression makes the attributes of `set` available while evaluating `body`. These are **soft** bindings:

1. **Non-`with` bindings win.** A `let`, lambda parameter, or other binding introduced outside `with` shadows attributes brought in by `with`, even if the `with` appears textually closer to the use site.
2. **Nested `with` shadows outer `with`.** An inner `with` hides same-named attributes from an outer `with`.
3. **Rewriting rule.** The manual gives an equivalence: each `with` can be thought of as a `let` that binds the set's attributes, and those converted lets nest **outside** explicit `let` bindings — so explicit bindings end up inner and take priority.

The [let-in and with](../syntax/let-in-and-with.md) page covers syntax; the examples below focus on resolution order.

### Dynamic attribute selection is not scoping

Selecting `set.${var}` or defining `${var} = value` in a set uses the **value** of `var` to pick or name an attribute. That does not introduce `var`'s referent as a new binding in the surrounding expression:

```nix
let name = "foo"; in { foo = 1; }.${name}   # => 1 (lookup by value of name)
```

Do not confuse this with `with` or `inherit`.

## Examples

### `let` wins over `with`

```nix
let a = "from-let";
in with { a = "from-with"; }; a
# => "from-let"
```

The `with` binding never overrides the explicit `let`.

### Nested `let` and `with` — manual equivalence

The manual states that:

```nix
let a = 3; in with { a = 1; }; let a = 4; in with { a = 2; }; a
```

is equivalent to:

```nix
let a = 1; in let a = 2; in let a = 3; in let a = 4; in a
# => 4
```

Reading inside-out: converted `with` layers (`1`, then `2`) sit **outside** the explicit `let`s (`3`, then `4`). The innermost binding wins, so `a` is `4`.

### Inner `with` shadows outer `with`

```nix
with { a = "outer"; };
with { a = "inner"; };
a
# => "inner"
```

Both layers are `with`; the inner set's `a` hides the outer one.

### `rec` vs outer scope

```nix
let x = "outer"; in
rec {
  x = "inner-rec";
  y = x;
}.y
# => "inner-rec"
```

Inside `rec`, the attribute `x` is in scope for sibling values. The outer `let x` is shadowed by the recursive attribute.

### Non-`rec` set uses outer `x`

```nix
let x = "outer"; in
{
  y = x;
}.y
# => "outer"
```

Without `rec`, `x` in the attribute value resolves to the enclosing `let`.

### Default values see sibling pattern bindings

```nix
let f = { x, y ? x + 1 }: y;
in f { x = 10; }
# => 11
```

`y`'s default expression runs in the function's pattern scope, so `x` is available.

## See also

- [let-in and with](../syntax/let-in-and-with.md) — syntax and common `with` patterns
- [Functions](../syntax/functions.md) — parameter patterns and defaults
- [Lists and attrsets](../syntax/lists-and-attrsets.md) — `rec`, `inherit`, attrset construction
- [Anti-patterns](../idioms/anti-patterns.md) — when to avoid `with`

## References

- [Nix language syntax — let, inherit, with, rec, functions](https://nix.dev/manual/nix/stable/language/syntax.html)
