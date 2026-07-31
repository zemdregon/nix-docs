---
status: complete
---

# Conditionals and Asserts

## Overview

Nix provides two boolean-driven control forms: **conditionals** (`if … then … else …`) for choosing between expressions, and **assertions** (`assert …; …`) for failing evaluation when a requirement is not met. Both require a boolean condition. Conditionals rely on [laziness](../semantics/laziness.md) so only the taken branch is evaluated; assertions are commonly paired with the [implication operator](operators.md) (`->`) in package functions to enforce dependency constraints without pulling optional deps when a feature is off.

## Details

### Conditionals

Syntax:

```nix
if e1 then e2 else e3
```

`e1` must evaluate to a boolean (`true` or `false`). If it is `true`, the result is `e2`; otherwise `e3`. Both branches appear in the syntax, but Nix evaluates **only the chosen branch**—the other is never forced. That matters when a branch would error, recurse infinitely, or touch the [Nix store](../../01-philosophy/purity-and-reproducibility.md) unnecessarily.

Use conditionals anywhere an expression is expected: attribute values, function bodies, list elements, and nested inside other forms.

### Assertions

Syntax:

```nix
assert e1; e2
```

`e1` must evaluate to `true`. If it does, evaluation continues and the result is `e2`. If it is `false`, evaluation **aborts** and Nix prints a backtrace pointing at the failed assertion. Assertions do not produce a value on their own; they guard the expression that follows.

Typical uses:

- **Package call contracts** — when a caller enables a feature flag, required dependencies must be non-`null` (see Examples).
- **Internal invariants** — sanity checks inside large attribute sets or modules before building a derivation.

Assertions are checked when evaluation reaches them; they are not a separate static analysis pass.

### Implication in package patterns

In [Nixpkgs](../../06-nixpkgs/architecture/mkDerivation.md) call wrappers, assertions often use `->` (logical implication): `assert feature -> dep != null;` means “if `feature` is enabled, `dep` must be provided.” When `feature` is `false`, the right-hand side is not required to hold and is not evaluated—same short-circuit behavior as `if`.

**Assertions vs conditionals for optional deps:** an assertion ensures the caller passed consistent arguments; an `if` on the derivation attribute set **nulls out** unused inputs so the store path does not change when an unused dependency updates (avoiding spurious rebuilds).

## Examples

Minimal conditional:

```nix
if enableDebug then "-g" else ""
```

Assertion with implication (classic optional-feature pattern):

```nix
{ sslSupport ? false, openssl ? null, stdenv, ... }:

assert sslSupport -> openssl != null;

stdenv.mkDerivation {
  # ...
  openssl = if sslSupport then openssl else null;
}
```

When `sslSupport` is `false`, the assertion passes even if `openssl` is `null`; the `if` keeps OpenSSL out of the derivation’s inputs so disabling SSL does not rebuild the package when OpenSSL changes elsewhere.

Multiple guards chain as separate `assert` forms before the body:

```nix
assert localServer -> db4 != null;
assert httpServer -> httpd != null;
# ...
stdenv.mkDerivation { /* ... */ }
```

## See also

- [Operators](operators.md) — `->`, `&&`, `||`, and comparison operators
- [Laziness](../semantics/laziness.md) — why only one branch of `if` runs
- [Purity and reproducibility](../../01-philosophy/purity-and-reproducibility.md) — evaluation aborts and deterministic builds
- [mkDerivation](../../06-nixpkgs/architecture/mkDerivation.md) — where package-level `assert` / `if` patterns appear

## References

- [Nix manual — Conditionals](https://nix.dev/manual/nix/stable/language/syntax.html#conditionals)
- [Nix manual — Assertions](https://nix.dev/manual/nix/stable/language/syntax.html#assertions)
- [Nix manual — `->` operator](https://nix.dev/manual/nix/stable/language/operators.html)
