---
status: complete
---

# Operators

## Overview

Nix expressions combine values with prefix, infix, and postfix operators. Precedence and associativity follow the [Nix language manual](https://nix.dev/manual/nix/stable/language/operators.html); several operators are overloaded (notably `+`) or short-circuit (`&&`, `||`, `->`). Function [application](functions.md) binds tighter than most infix operators, so parentheses matter inside [lists](lists-and-attrsets.md).

## Details

### Precedence (high to low)

| Level | Operators | Notes |
|-------|-----------|-------|
| Selection | `.` | Attribute/path selection; see [lists and attrsets](lists-and-attrsets.md) |
| Application | juxtaposition | Function call; see [functions](functions.md) |
| Unary | `-` | Negation |
| Has attribute | `?` | `set ? name` |
| Concat lists | `++` | List concatenation |
| Multiplicative | `*`, `/` | Integer and float arithmetic |
| Additive | `+`, `-` | Arithmetic; `+` also concatenates strings and paths (below) |
| Logical NOT | `!` | Boolean negation |
| Update | `//` | Attribute-set merge; right-hand side wins on duplicate keys |
| Comparison | `<`, `>`, `<=`, `>=` | Ordered types only |
| Equality | `==`, `!=` | Partially strict on composites |
| Logical AND | `&&` | Short-circuit |
| Logical OR | `\|\|` | Short-circuit |
| Implication | `->` | Short-circuit: `false -> e` does not evaluate `e` |
| Pipe (experimental) | `\|>` / `<\|` | Needs `pipe-operators`; see [pipe operators](../../08-experimental-features/pipe-operators-and-lang.md) |

Within a level, most operators group left-to-right; the manual marks `++` and `//` as right-associative, and `->` as right-associative. Use parentheses when mixing operators at similar precedence.

### `+` overloads

`+` and `-` behave as arithmetic on integers and floats. `+` additionally concatenates:

| Left | Right | Result |
|------|-------|--------|
| string | string | string concatenation |
| path | path | path |
| path | string | path |
| string | path | string (path copied into the store) |

See [strings and interpolation](strings-and-interpolation.md) and [antiquotation and paths](antiquotation-and-paths.md).

### Update (`//`)

`left // right` merges two attribute sets. Keys present in **both** sets take their value from the **right** operand. Both operands are evaluated to **WHNF** (weak head normal form) before merge; the merge itself does not force deep evaluation of nested values.

### Short-circuit operators

- **`&&`**, **`||`**: Standard boolean short-circuit. The right operand is skipped when the result is already determined.
- **`->`**: `a -> b` is equivalent to `!a || b`. When `a` evaluates to `false`, `b` is not evaluated.

### Comparisons and equality

Comparison operators require **compatible ordered types**:

- **Numbers** (int or float): usual arithmetic ordering.
- **Strings** and **paths**: lexicographic ordering.
- **Lists**: compared **itemwise** in order; shorter list is less than a longer list with a matching prefix.

`==` and `!=` compare values of the same type. On composite values (lists, attribute sets), comparison is **partially strict**: structure and already-evaluated parts are compared; unevaluated thunks may remain unevaluated if a difference is found earlier.

### Lists vs application

Inside `[ ... ]`, elements are separated by **whitespace**, not commas. Function application binds tighter than list construction, so a call inside a list needs parentheses:

```nix
[ f x ]       # two elements: f and x
[ (f x) ]     # one element: result of f x
```

See [lists and attrsets](lists-and-attrsets.md).

## Examples

Precedence and parentheses:

```nix
1 + 2 * 3     # => 7
{ a = 1; } // { a = 2; b = 3; }   # => { a = 2; b = 3; }
```

String and path concatenation:

```nix
"hello " + "world"    # => "hello world"
./foo + "/bar"        # => ./foo/bar (path)
"prefix-" + ./file    # => "prefix-/nix/store/…-file" (string)
```

Short-circuit implication:

```nix
false -> builtins.throw "skipped"   # => true (right side not evaluated)
true  -> 42                         # => 42
```

List comparison:

```nix
[ 1 2 ] < [ 1 3 ]   # => true
[ 1 ]   < [ 1 2 ]   # => true
```

## See also

- [Lists and attrsets](lists-and-attrsets.md) — selection, `?`, `++`, list syntax
- [Functions](functions.md) — application and precedence
- [Strings and interpolation](strings-and-interpolation.md) — string `+`
- [Antiquotation and paths](antiquotation-and-paths.md) — path `+`
- [Pipe operators (experimental)](../../08-experimental-features/pipe-operators-and-lang.md) — `|>` and `<|`

## References

- [Nix manual — Operators](https://nix.dev/manual/nix/stable/language/operators.html)
