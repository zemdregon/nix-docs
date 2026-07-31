---
status: complete
---

# Evaluation Model

## Overview

**Evaluation** is the process of turning Nix expressions into **values** by applying language rules — literals, operators, built-ins, and user-defined functions — as needed by whatever is consuming the expression (CLI command, REPL, or another subexpression).

A **value** is an irreducible expression: `1 + 2` is still an expression, `3` is a value. Evaluation proceeds on the **head** of an expression; after the applicable rules run, the result is in **weak head normal form (WHNF)**: the outermost constructor is fully determined, but inner parts may still be unevaluated **thunks**. “Weak” means the head may still be a function — a function in WHNF is already a value even if its body is untouched.

Nix uses **call-by-need** (lazy) evaluation: thunks delay work until a value is demanded, and memoize once forced. **Strictness** rules say which subexpressions must reach WHNF before a construct can produce a result. Beyond data dependencies, **evaluation order is mostly unspecified**.

## Details

### Values and WHNF

Evaluation stops at WHNF, not necessarily at a fully expanded tree:

- An integer literal is a value and WHNF.
- `x: x + 1` is WHNF (a function); `x + 1` inside the body is not evaluated until the function is applied and `x` is needed.
- `{ a = 1; b = f 2; }` can be WHNF while `b` remains a thunk if nothing has read `b` yet.

The consumer decides how much to evaluate. `nix-instantiate --eval -E '1 + 2'` must reduce `1 + 2` to `3`; importing a module may leave large parts of the file as thunks until an option or attribute is accessed.

### Call-by-need and memoization

A **thunk** pairs a delayed expression with its **lexical closure** (the bindings in scope where it was created). When a thunk is **forced**, the expression runs once and the result replaces the thunk.

Memoization applies in these places:

- **Attribute values** in a set — forcing `.attr` evaluates and caches that attribute.
- **`let` bindings** — each name is evaluated at most once when first used.
- **Function parameters** — each formal is evaluated at most once per call when first used in the body.

The **result of a function call** is not automatically memoized. Unless you bind it (`let r = f x; in …` or an attribute), calling `f x` again may repeat work.

See [laziness](laziness.md) for lazy control flow (`&&`, `||`, `->`, `if`) and common pitfalls.

### Strictness

**Strictness** is which arguments or parts of an expression must be WHNF before a form can proceed.

| Construct | Typical strictness |
|-----------|-------------------|
| Set pattern `{ a, b }: …` | Strict in the **argument set** reaching WHNF: must be a set with required names present (defaults and `@`-patterns follow [function](../syntax/functions.md) rules). Individual attribute **values** inside the set are not forced until referenced. |
| Arithmetic, comparison | Operands forced to WHNF when the operator runs |
| Attribute selection `set.attr` | `set` forced to WHNF; then `attr` is forced if selected |
| List / attrset literals | Elements stored as thunks until accessed |

Example: `wrap = x: { wrapped = x; }` is **not** strict in `x`. The function is WHNF immediately; `x` is only forced when something reads `.wrapped`.

Built-ins and operators declare their own strictness; the [Nix language manual](https://nix.dev/manual/nix/stable/language/evaluation.html) is authoritative for edge cases.

### Evaluation order

Order is **mostly unspecified** except where data dependencies require it: a subexpression must be evaluated before its value is used. Do not rely on side-effect ordering — for example, the relative order of multiple `builtins.trace` calls is not defined.

For [types and coercion](types-and-coercion.md), coercions happen when an operator or built-in demands a particular type, not eagerly at binding time.

### Scoping during evaluation

When a thunk or function body runs, free variables resolve in the **lexical environment** where the expression was written, not at the call site. Closures captured in thunks therefore see the bindings from their definition point. See [scoping and shadowing](scoping-and-shadowing.md).

### Failure modes

Two common evaluation failures are easy to confuse:

| Symptom | Typical cause |
|---------|----------------|
| **Infinite recursion** / “infinite recursion encountered” | A **value cycle** — e.g. `let x = x; in x` or mutually recursive attrsets without a base case. The evaluator detects the cycle when forcing a thunk already on the stack. |
| **Stack overflow** / “exceeded max-call-depth” | **Deep or unbounded call chains** — e.g. `builtins.foldl' (x: y: x + y) 0 (range 0 100000)` — not necessarily a cycle, just too many nested calls. |

Both are evaluation limits, but one is cyclic dependency on values, the other is call depth.

## Examples

Values vs expressions:

```nix
1 + 2    # expression (not a value)
3        # value
```

WHNF with an unevaluated inner thunk:

```nix
let f = x: x + 1; in { a = f 2; }
# WHNF as a set; attribute a is a thunk until .a is accessed
```

Non-strict function parameter:

```nix
wrap = x: { wrapped = x; };
# wrap 42 is WHNF immediately; x is not forced until .wrapped is read
```

Memoization in `let` vs repeated calls:

```nix
let
  expensive = builtins.trace "eval" (1 + 1);
in [ expensive expensive ]   # trace once
# vs
let f = x: builtins.trace "call" (x + 1); in [ (f 1) (f 1) ]   # trace twice
```

Strictness of set patterns (from the manual):

```nix
{ x, y, z } @ args: args
# args is the value as passed; matching checks required names exist
```

Evaluation is demand-driven when building [derivations](../../02-concepts/derivation.md): `stdenv.mkDerivation { … }` may construct a attrset whose `.drvPath` and dependencies are resolved only when the Nix command needs the store path, not when the Nix file is first parsed.

## See also

- [Laziness](laziness.md) — thunks, short-circuit operators, when work runs
- [Types and coercion](types-and-coercion.md) — when values are coerced
- [Scoping and shadowing](scoping-and-shadowing.md) — lexical closures in thunks
- [Functions](../syntax/functions.md) — patterns, defaults, set strictness
- [Derivation](../../02-concepts/derivation.md) — how evaluation connects to the store

## References

- [Nix manual — Evaluation](https://nix.dev/manual/nix/stable/language/evaluation.html)
- [Nix manual — Language](https://nix.dev/manual/nix/stable/language/)
