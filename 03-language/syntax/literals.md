---
status: complete
---

# Literals

## Overview

Nix expressions are built from values. **Literals** are the syntax for writing primitive values directly in source code: integers, floats, booleans, `null`, and paths. Lists, attribute sets, and functions use their own forms and are covered elsewhere.

Strings have a richer literal surface (quotes, indentation, interpolation, antiquotation); see [strings and interpolation](strings-and-interpolation.md). Paths are a distinct type from strings and interact with the filesystem and [store paths](../../02-concepts/store-path.md) when coerced or copied into the store.

## Details

**Integers** are signed 64-bit two's complement values (range \(-2^{63}\) through \(2^{63}-1\)). Non-negative integers appear as digit sequences (`0`, `42`). Negative values are unary `-` applied to a positive literal (`-1`), not a dedicated negative token. The minimum value cannot be written as a literal: `-9223372036854775808` parses as negation of `9223372036854775808`, which is one past the maximum and overflows.

**Floats** are 64-bit IEEE 754 numbers. Examples include `123.43` and scientific notation such as `.27e13`. A leading `-` is again unary negation.

**Booleans** are the keywords `true` and `false`. The same values exist as `builtins.true` and `builtins.false`.

**Null** is the single value written `null`, also available as `builtins.null`.

**Paths** denote filesystem locations and are not strings. A path literal must contain at least one `/`: `./src`, `/etc/nixos`, or `~/projects`. Without a slash, a dotted name is attribute selection—`builder.sh` selects `sh` from `builder`, not a path. Relative path literals resolve against the directory of the file being evaluated. Absolute paths start with `/`. The `~/` home shorthand is rejected in [pure evaluation](../semantics/purity-boundaries.md). [Lookup paths](antiquotation-and-paths.md) such as `<nixpkgs>` also produce path values when resolved. Path literals may include interpolation, but at least one `/` must appear before any `${…}` so the token is recognized as a path.

Unquoted tokens that match the URI grammar (`http://example.com`) are parsed as **string** literals, not paths—a convenience for URLs without quotes. See [strings and interpolation](strings-and-interpolation.md).

Compound values—[lists and attribute sets](lists-and-attrsets.md)—use bracket and brace syntax rather than single-token literals. For how literals relate to the type system and coercion, see [types and coercion](../semantics/types-and-coercion.md).

## Examples

```nix
# integers and floats
42
-7
3.14
.27e13

# booleans and null
true
false
null

# paths (must contain /)
./default.nix
../modules
/etc/hosts
~/src          # rejected under pure evaluation

# not a path: attribute selection
# builder.sh

# URI-like token → string, not path
https://nixos.org

# lookup path (resolves to a path when evaluated)
<nixpkgs>
```

Verified with `nix-instantiate --eval`: `builtins.typeOf https://nixos.org` → `"string"`; `builtins.isPath ./.` → `true`; `~/x` under `--pure-eval` fails with a pure-mode path error.

## References

- [Nix language syntax](https://nix.dev/manual/nix/stable/language/syntax.html) — number and path literals, `~/` and pure eval
- [Nix language types](https://nix.dev/manual/nix/stable/language/types.html) — integer, float, boolean, null, path vs string
- [String literals](https://nix.dev/manual/nix/stable/language/string-literals.html) — URI form as an unquoted string literal

## See also

- [Strings and interpolation](strings-and-interpolation.md)
- [Antiquotation and paths](antiquotation-and-paths.md)
- [Lists and attribute sets](lists-and-attrsets.md)
- [Types and coercion](../semantics/types-and-coercion.md)
- [Purity boundaries](../semantics/purity-boundaries.md)
- [Store path](../../02-concepts/store-path.md)
