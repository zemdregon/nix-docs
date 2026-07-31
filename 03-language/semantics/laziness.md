---
status: complete
---

# Laziness

## Overview

Nix is a **lazy** (call-by-need) language: an expression is evaluated only when its value is needed for the result being demanded. Once a value is computed, it is **memoized** and shared — the same `let` binding or function argument is not re-evaluated on reuse. This differs from strict languages where subexpressions run eagerly, and it shapes how attribute sets, lists, and control flow behave in real configs.

Laziness is not uniform: some constructs force subexpressions to weak head normal form (WHNF) before proceeding. Knowing where evaluation stops and where it is forced prevents surprise when reading or profiling Nix code. See [evaluation-model.md](evaluation-model.md) for the broader reduction story.

## Details

### Call-by-need and sharing

When the evaluator needs a value, it reduces the corresponding expression to WHNF and caches the result. Function parameters and `let`-bound names behave this way: the right-hand side runs at most once per binding site, and only if something actually reads that name.

Unused [let bindings](../syntax/let-in-and-with.md) and unused attribute fields therefore cost nothing beyond constructing the binding or attribute name — their values are never forced. Large nixpkgs attribute sets rely on this: importing `pkgs` does not build every package; only referenced attributes are evaluated.

### Lists

Lists are **lazy in their elements** but **strict in their length**. Constructing `[ a b c ]` allocates a list of three slots without evaluating `a`, `b`, or `c`. Indexing or otherwise demanding an element forces that element only. Operations that need every element — such as `map`, `filter`, or comparing two lists for equality — eventually force all elements they touch.

See [lists and attrsets](../syntax/lists-and-attrsets.md) for construction syntax.

### Attribute sets

Building an attribute set `{ name = expr; … }` returns a set value **before** evaluating the attribute values. Selecting `set.name` (or using `set.name or default`) forces `expr` for that attribute only; other fields stay suspended.

The update operator `//` is **strict in both operands' WHNF**: each side must be an attribute set in WHNF before the merge proceeds. It does not force the *values inside* those sets beyond what WHNF requires for the set itself.

### Control flow and conditionals

Logical operators short-circuit:

- `&&` evaluates the left operand; if it is `false`, the result is `false` without evaluating the right.
- `||` evaluates the left operand; if it is `true`, the result is `true` without evaluating the right.
- `->` (implication) forces the antecedent; if it is `false`, the result is `true` without evaluating the consequent.

An [if expression](../syntax/conditionals-and-asserts.md) forces its condition to a boolean, then evaluates **only the chosen branch**. The other branch is never evaluated.

`assert condition; body` forces `condition` to a boolean (and aborts if it is `false`), then evaluates `body`. The condition is always evaluated; the body is evaluated only if the assertion passes.

### Evaluation order

Nix does not guarantee left-to-right evaluation of independent subexpressions. A function application may evaluate the argument before the function, or the reverse, depending on what the evaluator needs first. This rarely matters for pure code but explains counterintuitive ordering in small examples.

For instance, in `wrap (1 + 2)`, the call to `wrap` can produce `{ wrapped = … }` before the addition `1 + 2` is forced — if `wrap`'s body does not use its argument immediately, the argument stays suspended until something selects into the result and demands it.

## Examples

### Unused fields stay cheap

```nix
let
  heavy = builtins.trace "computing heavy" (1 + 1);
in { used = 42; unused = heavy; }.used
```

Evaluating this yields `42`. The trace for `heavy` does not run because `unused` is never selected.

### Lazy list elements

```nix
let
  xs = [ (builtins.trace "first" 1) (builtins.trace "second" 2) ];
in builtins.head xs
```

Only `"first"` is traced; indexing does not force the second element.

### Short-circuit conditionals

```nix
if false then builtins.throw "unreachable" else "ok"
# => "ok"

false && builtins.throw "unreachable"
# => false (right side not evaluated)
```

### Strict `//` on WHNF sets

Both sides must be attribute sets in WHNF before merge; inner values remain lazy until accessed:

```nix
{ a = 1; } // { b = builtins.trace "forced" 2; }
# merge succeeds; "forced" appears only when `.b` is selected
```

## See also

- [Evaluation model](evaluation-model.md) — WHNF, reduction, and how laziness fits the full evaluator
- [Lists and attrsets](../syntax/lists-and-attrsets.md) — syntax for lazy collections
- [Conditionals and asserts](../syntax/conditionals-and-asserts.md) — `if`, `assert`, and branch forcing
- [let-in and with](../syntax/let-in-and-with.md) — local bindings and memoization
- [Functional package management](../../01-philosophy/functional-package-management.md) — why lazy, pure evaluation supports reproducible builds

## References

- [Nix language evaluation](https://nix.dev/manual/nix/stable/language/evaluation.html) — call-by-need, memoization, and WHNF
- [Nix language introduction](https://nix.dev/manual/nix/stable/language/) — states that the language is lazy
- [Nix language operators](https://nix.dev/manual/nix/stable/language/operators.html) — short-circuit `&&` / `||` / `->`, strictness of `//`
