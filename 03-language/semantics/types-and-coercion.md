---
status: complete
---

# Types and Coercion

## Overview

The Nix language is **dynamically typed**: values carry a runtime type, but expressions are not annotated or checked statically. A type mismatch surfaces only when an expression is **evaluated**—for example when an operator expects a boolean, or when `${…}` tries to coerce a value to a string. Every value is exactly one of the types below; there is no implicit conversion between unrelated types except where the language defines explicit coercion rules (chiefly toward strings).

## Details

### The type universe

| Type | Role | Predicate |
|------|------|-----------|
| **int** | Signed 64-bit integer | `builtins.isInt` |
| **float** | IEEE 754 double | `builtins.isFloat` |
| **bool** | `true` or `false` | `builtins.isBool` |
| **string** | Immutable byte sequence plus string context | `builtins.isString` |
| **path** | Canonical POSIX-style filesystem path (bytes starting with `/`) | `builtins.isPath` |
| **null** | Single null value (`builtins.null`) | `builtins.isNull` (same as `e == null`) |
| **attrs** | Attribute set | `builtins.isAttrs` |
| **list** | Ordered list | `builtins.isList` |
| **function** | Lambda or built-in function | `builtins.isFunction` |
| **external** | Opaque value from a Nix plugin | (plugin-specific) |

An attribute set with a callable `__functor` attribute is still type **attrs** (`isFunction` is `false`), but it is **callable** via function application — see [functions](../syntax/functions.md) and [operators](../syntax/operators.md).

Literals and syntax for each type are covered in [literals](../syntax/literals.md). Compound values are built with [lists and attribute sets](../syntax/lists-and-attrsets.md).

### Path is not string

Path and string values are **distinct types**, even when they contain the same byte sequence. A path `./foo` is not interchangeable with `"./foo"` for operators that require one type or the other. Path literals resolve relative to their base directory and are normalized (no `.`, `..`, or duplicate slashes); strings are opaque bytes. When a path must become a string in a **store-aware** context, Nix may copy the referenced file or directory into the [store](../../02-concepts/store-path.md)—see coercion below.

### Coercion to string

Several contexts require a string: `${expr}` in [strings and interpolation](../syntax/strings-and-interpolation.md), `"text" + path`, and `builtins.toString`. Rules differ slightly by mechanism.

**Interpolation (`${expr}`).** The expression must evaluate to:

- a **string** — used as-is;
- a **path** — copied into the store; the result is the store path string;
- an **attribute set** with `__toString` (function `self → string`) or `outPath` (string). If both exist, **`__toString` wins**. [Derivations](../../02-concepts/derivation.md) interpolate via `outPath` to the first output’s store path.

Any other type (plain list, function, or attribute set without those hooks) aborts evaluation with a coercion error.

**`builtins.toString`.** Explicit conversion accepts strings (unchanged), paths (string form of the path), integers, booleans (`true` → `"1"`, `false` → `""`), `null` (empty string), lists (elements stringified and joined with spaces), and attribute sets with `__toString` or `outPath`. Functions and arbitrary attribute sets without hooks cannot be converted.

**String–path concatenation.** `"prefix" + ./file` yields a string and **copies** `./file` into the store, embedding the resulting store path. This is the same store-copy behavior as path interpolation, not plain `toString` on a path literal.

There is no general coercion from string back to path except deprecated `builtins.toPath`; prefer path literals or `./. + "/segment"`.

### Numeric types and operators

Integers and floats are separate types but **type-compatible** for arithmetic, comparison, and equality (see [operators](../syntax/operators.md)):

- **Pure integer** operands (`+`, `-`, `*`, `/` with ints only) produce an **integer**.
- **Mixed** or all-float operands promote to **float**.
- **Division by zero** and **integer overflow** (result outside signed 64-bit range) are evaluation errors.

Comparison operators treat numbers with arithmetic ordering; strings and paths use lexicographic ordering; lists compare item-wise.

### When types are checked

Type requirements appear at **use sites**: boolean conditions in `if` and `assert`, operands of overloaded `+`, comparison operands, function callability, and interpolation. Because evaluation is [lazy](laziness.md), a type error in an unused branch may never appear. For how expressions reduce to values, see [evaluation model](evaluation-model.md).

## Examples

**Runtime type predicates.**

```nix
builtins.isInt 42        # => true
builtins.isPath ./src    # => true
builtins.isString ./src  # => false
```

**Path versus string.**

```nix
./foo == "./foo"   # => false (different types)
1 + "x"            # type error: no implicit int→string coercion
"./" + ./foo       # => string with store path after copy (if ./foo exists)
```

**Attribute-set coercion hooks.**

```nix
let
  withHook = { __toString = self: "v${toString self.n}"; n = 1; };
  withOutPath = { outPath = "/nix/store/…-example"; };
in {
  a = "${withHook}";    # => "v1"
  b = "${withOutPath}"; # => "/nix/store/…-example"
}
```

**Numeric promotion.**

```nix
1 + 2       # => 3 (int)
1 + 2.0     # => 3.0 (float)
1 / 2       # => 0 (int division)
1 / 2.0     # => 0.5 (float)
```

**Lists via `toString`, not interpolation.**

```nix
builtins.toString [ 1 2 3 ]   # => "1 2 3"
# "${[1 2 3]}"                # error: cannot coerce list to string
```

## References

- [Nix manual — Data types](https://nix.dev/manual/nix/stable/language/types.html)
- [Nix manual — String interpolation](https://nix.dev/manual/nix/stable/language/string-interpolation.html)
- [Nix manual — Operators](https://nix.dev/manual/nix/stable/language/operators.html) — arithmetic, equality, string/path `+`

## See also

- [Literals](../syntax/literals.md)
- [Strings and interpolation](../syntax/strings-and-interpolation.md)
- [Operators](../syntax/operators.md)
- [Evaluation model](evaluation-model.md)
- [Store path](../../02-concepts/store-path.md)
