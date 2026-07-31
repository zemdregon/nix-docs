---
status: complete
---

# Strings and Interpolation

## Overview

Nix **strings** are immutable byte sequences plus optional string context. The language does not distinguish character encodings at the type level.

Three literal forms build strings: double-quoted `"…"`, indented `''…''`, and unquoted **URI syntax** (RFC 2396 appendix B). **Interpolation** embeds expressions with `${…}` inside strings, path literals, and attribute names. Paths are a separate type; `${…}` inside a path keeps a path value (antiquotation), while interpolating a path *into a string* copies it to the store. See [literals](literals.md) and [antiquotation and paths](antiquotation-and-paths.md).

## Details

**Double-quoted strings.** Usual form for short text; may span lines. Escape with `\`: `\"`, `\\`, `\${` (literal `${`), plus `\n`, `\r`, `\t`. Write `$${` when you need a literal `${` without starting interpolation (`"$${` → `$` then `${`).

**Indented strings.** Delimited by `''`, suited to multi-line config and shell snippets. Nix strips a **common prefix of spaces** from every line (tabs are not stripped). After the opening `''`, leading whitespace and a newline on the first line are ignored if that line has no other text.

Indented-string escapes differ from double-quoted ones:

| Want | Write |
|------|--------|
| `$` | `''$` |
| `${` | `''${` |
| `''` | `'''` |
| newline / CR / tab | `''\n`, `''\r`, `''\t` |

`''\` escapes any other character. A lone `'` needs no escape. `$${` may be written literally, as in double-quoted strings.

**URI syntax.** Unquoted tokens matching the URI grammar can stand alone where a string is expected—e.g. `https://example.org/foo.tar.bz2` without quotes.

**What may be interpolated.** An expression inside `${…}` must be a string, a path, or an attribute set that supplies either:

- `__toString` — a function `self → string`, or
- `outPath` — a string store path.

If both are present, **`__toString` wins**. A [derivation](../../02-concepts/derivation.md) interpolates to the store path of its **first** output. A **path** interpolated into a string is copied into the store and the resulting [store path](../../02-concepts/store-path.md) string is used. Other types are not valid unless coerced first; see [types and coercion](../semantics/types-and-coercion.md).

**Where interpolation works.** `${…}` appears in double-quoted and indented strings, in path expressions, and in attribute names (dynamic keys in [lists and attribute sets](lists-and-attrsets.md)). Path antiquotation (`./${name}.nix` stays a path) versus string coercion of paths is covered in [antiquotation and paths](antiquotation-and-paths.md).

## Examples

**Double-quoted interpolation and escapes** (verified with `nix-instantiate --eval`):

```nix
let version = "1.0";
in "hello-${version}\nline two"
# ⇒ "hello-1.0\nline two"

"\${"   # ⇒ "${"
"$${"   # ⇒ "$" then "${"
```

**Indented string.** Common prefix spaces are stripped. Use `''${` for a literal `${`; bare `${name}` expands:

```nix
let name = "app";
in ''
  echo ''${name}
  echo ${name}
''
# ⇒ "echo ${name}\necho app\n"
```

Indented escapes for `$` and `''`:

```nix
''
  ''$
''
# ⇒ "$\n"

''
  '''
''
# ⇒ "''\n"
```

**Derivation and path.** `${someDrv}` becomes the first output’s store path; `"${./src}"` copies `./src` into the store and interpolates that path string. Contrast with `./${name}.nix`, which remains a path value (see [antiquotation and paths](antiquotation-and-paths.md)).

**Dynamic attribute name:**

```nix
{ ${"enabled"} = true; }
# ⇒ { enabled = true; }
```

**`__toString` over `outPath`:**

```nix
let a = { __toString = _: "yes"; outPath = throw "no"; };
in "${a}"
# ⇒ "yes"
```

## References

- [String literals](https://nix.dev/manual/nix/stable/language/string-literals.html) — double-quoted, indented, and URI forms
- [String interpolation](https://nix.dev/manual/nix/stable/language/string-interpolation.html) — `${…}` rules and coercions
- [Nix language types](https://nix.dev/manual/nix/stable/language/types.html) — string type and context

## See also

- [Literals](literals.md)
- [Antiquotation and paths](antiquotation-and-paths.md)
- [Lists and attribute sets](lists-and-attrsets.md)
- [Types and coercion](../semantics/types-and-coercion.md)
- [Derivation](../../02-concepts/derivation.md)
- [Store path](../../02-concepts/store-path.md)
