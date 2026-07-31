---
status: complete
---

# Functions

## Overview

Nix functions are **anonymous** values written as `pattern: body`. The pattern describes what the argument must look like and binds names used in `body`. Functions have no built-in names; assign them with [let-in](let-in-and-with.md) or as attributes in a set.

Application uses **juxtaposition** — `f arg` with no operator — and is left-associative, so `f a b` means `(f a) b`. That makes **currying** natural: `x: y: x + y` is a function that returns another function. Callable values are not limited to user-defined functions; built-ins and attribute sets with a `__functor` attribute are also callable. See [operators](operators.md) for precedence relative to other forms.

## Details

### Identifier patterns

A single identifier matches any argument and binds it to that name:

```nix
x: !x          # negate a boolean
x: y: x + y    # curried addition
```

Each colon introduces another parameter. Partial application works because every function takes exactly one argument:

```nix
map (x: x + 1) [ 1 2 3 ]
# => [ 2 3 4 ]
```

### Set patterns

A pattern `{ x, y, z }: …` matches an [attribute set](lists-and-attrsets.md) that contains exactly those attribute names (no more, no less). Add `...` (ellipsis) to allow extra attributes:

```nix
{ x, y, z, ... }: z + y + x
```

**Default values** use `name ? expr`. Attributes with defaults may be omitted at call sites:

```nix
{ x, y ? "foo", z ? "bar" }: z + y + x
```

Only `x` is required here; missing `y` or `z` use the defaults.

**@-patterns** bind the whole argument as passed, before pattern matching proceeds:

```nix
args @ { x, y, z, ... }: z + y + x + args.a
# equivalent to:
{ x, y, z, ... } @ args: z + y + x + args.a
```

`args` is the argument **as passed**, not a merged view with defaults applied. For example, `args @ { a ? 23, ... }: [ a args ]` called as `f {}` yields `[ 23 {} ]` — `a` is 23 from the default, but `args` remains `{}`.

All names introduced by the pattern — including `@`-bindings — are in scope for the **entire** function expression, including default expressions. A parameter can refer to another, or an `@`-binding can appear in a default:

```nix
{ x, y ? [ x ] }: { inherit y; }
args @ { x ? args.a, ... }: x
```

### Strictness

Set-pattern functions are **strict in the attribute set argument** to weak head normal form: the value must be a set, required names must be present (or have defaults), and no disallowed extra names may appear when `...` is absent. Individual attribute **values** inside the set are not forced until referenced in the body. See [laziness](../semantics/laziness.md) and the [evaluation model](../semantics/evaluation-model.md).

### Other callable values

Beyond `pattern: body` expressions, Nix can apply:

- **Built-in functions** (`builtins.add`, `import`, etc.)
- **Attribute sets with `__functor`**, which receive the set itself as the first argument when called

The common nixpkgs idiom of functions taking `{ stdenv, lib, ... }:` is a set pattern; [callPackage](../idioms/callPackage.md) fills those arguments from a fixed-point set.

## Examples

```nix
# bind a named function in let
let
  concat = { x, y }: x + y;
in concat { x = "foo"; y = "bar"; }
# => "foobar"

# currying and partial application
let add = x: y: x + y;
in map (add 10) [ 1 2 3 ]
# => [ 11 12 13 ]

# defaults, ellipsis, and @-pattern
let
  greet = args @ { name, greeting ? "Hello", ... }:
    "${greeting}, ${name}";
in greet { name = "world"; extra = 1; }
# => "Hello, world"

# @-binding does not include defaulted fields
let
  f = args @ { a ? 23, ... }: [ a args ];
in f {}
# => [ 23 {} ]

# default referencing another parameter
let
  wrap = { x, y ? [ x ] }: { inherit y; };
in wrap { x = 3; }
# => { y = [ 3 ]; }

# @-binding used in a default
let
  f = args @ { x ? args.a, ... }: x;
in f { a = 1; }
# => 1

# __functor: set applied as a function
let
  add = { __functor = self: x: x + self.x; };
  inc = add // { x = 1; };
in inc 1
# => 2

# set patterns force the argument to WHNF, not attribute values
let f = { a, b }: a;
in f { a = 1; b = throw "unused"; }
# => 1
```

## References

- [Nix language syntax — Functions](https://nix.dev/manual/nix/stable/language/syntax.html) — patterns, defaults, ellipsis, and `@`-patterns
- [Nix language operators — Function application](https://nix.dev/manual/nix/stable/language/operators.html) — juxtaposition, callability, precedence

## See also

- [Operators](operators.md)
- [Lists and attribute sets](lists-and-attrsets.md)
- [let-in and with](let-in-and-with.md)
- [Laziness](../semantics/laziness.md)
- [Evaluation model](../semantics/evaluation-model.md)
- [callPackage](../idioms/callPackage.md)
