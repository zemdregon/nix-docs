---
status: complete
---

# Attrset, List, String

## Overview

The Nix evaluator exposes collection and string primitives under the global `builtins` attribute set. A subset is also available as bare names in the top-level scope (`map`, `toString`, `removeAttrs`, `true`, `false`, `null`, …). Prefer `builtins.…` when writing library-style code so names stay unambiguous if `with` or imports shadow globals.

These functions operate on values of the language types — lists, attribute sets, and strings — and do not touch the filesystem or network. For path I/O and fetches, see [path and filesystem](path-and-filesystem.md) and [import and fetch](import-and-fetch.md). Type predicates (`isAttrs`, `isList`, `isString`, …) and `typeOf` are the usual guards before calling a typed builtin.

## Details

### Attribute sets

| Builtin | Role |
|---------|------|
| `attrNames set` | Alphabetically sorted list of attribute names |
| `attrValues set` | Values in the same order as `attrNames` |
| `getAttr s set` | Dynamic `.` — abort if `s` is missing |
| `hasAttr s set` | Dynamic `?` |
| `catAttrs attr list` | Collect attr `attr` from each set in `list` (skip missing) |
| `intersectAttrs e1 e2` | Attributes of `e2` whose names also appear in `e1` |
| `mapAttrs f set` | `f name value` for each attribute |
| `removeAttrs set list` | Drop names in `list` (missing names ignored) |
| `listToAttrs list` | Build a set from `{ name; value; }` elements; first duplicate wins |
| `zipAttrsWith f list` | Union of names across sets; `f name values` for each |
| `functionArgs f` | Formal args of a set-pattern function → `{ argName = hasDefault; … }` |

`attrNames` / `attrValues` force attribute names to be sorted, so iteration order is stable. Use `getAttr` / `hasAttr` when the name is computed; use `.` / `?` when it is a literal identifier.

### Lists

| Builtin | Role |
|---------|------|
| `map f list` | Map (also global) |
| `filter f list` | Keep elements where `f` is true |
| `foldl' op nul list` | Left fold; each `op` result is forced immediately |
| `concatLists lists` | Flatten one level of nested lists |
| `concatMap f list` | `concatLists (map f list)`, more efficient |
| `elem x xs` / `elemAt xs n` | Membership / zero-based index (OOB is fatal) |
| `head` / `tail` / `length` | First element, rest, length |
| `genList f n` | `[ f 0 … f (n-1) ]` |
| `sort comparator list` | Stable sort; comparator must be a strict weak order |
| `partition pred list` | `{ right = …; wrong = …; }` |
| `all` / `any` | Predicates over every / some element |
| `groupBy f list` | Map of group key → list of elements |
| `genericClosure { startSet; operator; }` | Transitive closure over `key`-bearing attrsets |

Avoid repeated `tail` for recursion: each call is O(n), so walking a list that way is O(n²). Prefer `foldl'`, `map`, or indexing patterns instead.

### Strings and conversion

| Builtin | Role |
|---------|------|
| `stringLength s` | Byte length |
| `substring start len s` | Bytes `[start, start+len)`; `len = -1` means “to end” |
| `concatStringsSep sep list` | Join strings with separator |
| `replaceStrings from to s` | Parallel multi-string replace; `to` is lazy per match |
| `match regex s` | Full-string POSIX ERE match → capture list or `null` |
| `split regex s` | Interleave non-matches with capture groups |
| `compareVersions` / `splitVersion` / `parseDrvName` | Version and drv-name helpers |
| `toString e` | Coerce to string (paths, ints, bools, lists, `{ outPath }`, …) |
| `fromJSON` / `toJSON` / `fromTOML` / `toXML` | Structured interchange |
| `hashString type s` | Hash of a string (`md5` / `sha1` / `sha256` / `sha512`) |
| `convertHash { hash; … }` | Reformat hashes between base16 / nix32 / base64 / SRI |

`toString` on a boolean yields `""` for `false` and `"1"` for `true`; on a list it joins elements with spaces. Derivations coerce via `outPath`. See [types and coercion](../semantics/types-and-coercion.md).

### Numbers and bits

`add`, `sub`, `mul`, `div`, `lessThan`, `ceil`, `floor`, `bitAnd`, `bitOr`, and `bitXor` cover arithmetic and integer bitwise ops. `lessThan` requires both sides to be numbers, strings, or paths of matching kind.

## Examples

```nix
builtins.attrNames { y = 1; x = "foo"; }
# => [ "x" "y" ]

builtins.mapAttrs (n: v: v * 10) { a = 1; b = 2; }
# => { a = 10; b = 20; }

builtins.concatStringsSep "/" [ "usr" "local" "bin" ]
# => "usr/local/bin"

builtins.match "a(b)(c)" "abc"
# => [ "b" "c" ]

builtins.partition (x: x > 10) [ 1 23 9 3 42 ]
# => { right = [ 23 42 ]; wrong = [ 1 9 3 ]; }

builtins.listToAttrs [
  { name = "foo"; value = 123; }
  { name = "bar"; value = 456; }
]
# => { foo = 123; bar = 456; }

builtins.foldl' (acc: x: acc + x) 0 [ 1 2 3 ]
# => 6
```

## References

- [Nix language — Built-ins](https://nix.dev/manual/nix/stable/language/builtins.html) — full primitive catalog
- [Nix language — Types](https://nix.dev/manual/nix/stable/language/types.html) — value kinds and coercion

## See also

- [Lists and attribute sets](../syntax/lists-and-attrsets.md)
- [Strings and interpolation](../syntax/strings-and-interpolation.md)
- [Functions](../syntax/functions.md)
- [Types and coercion](../semantics/types-and-coercion.md)
- [lib helpers](../idioms/lib-helpers.md)
