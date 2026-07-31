---
status: complete
---

# Language Cheatsheet

Dense Nix expression-language quick reference. Deeper treatment: [03-language](../03-language/README.md) · domain [cheatsheet](../03-language/cheatsheet.md).

## Quick reference

Syntax: [literals](../03-language/syntax/literals.md) · [strings](../03-language/syntax/strings-and-interpolation.md) · [lists/attrs](../03-language/syntax/lists-and-attrsets.md) · [functions](../03-language/syntax/functions.md) · [let/with](../03-language/syntax/let-in-and-with.md) · [operators](../03-language/syntax/operators.md) · [if/assert](../03-language/syntax/conditionals-and-asserts.md) · [paths](../03-language/syntax/antiquotation-and-paths.md)

Semantics: [laziness](../03-language/semantics/laziness.md) · [types/coercion](../03-language/semantics/types-and-coercion.md) · [scoping](../03-language/semantics/scoping-and-shadowing.md) · [purity](../03-language/semantics/purity-boundaries.md)

**Laziness:** unused `let` bindings and attr fields are free. `if`, `&&`, `||`, `->` short-circuit.

### Literals

| Form | Examples |
|------|----------|
| Integer | `0`, `42`, `-7` (signed 64-bit) |
| Float | `3.14`, `.27e13` |
| Boolean | `true`, `false` |
| Null | `null` |
| Path | `./src`, `/etc/nixos`, `<nixpkgs>` — must contain `/`; **not** a string |
| URI token | `https://example.com` — parsed as **string** |

### Strings

| Form | Notes |
|------|-------|
| `"…"` | Escapes: `\"`, `\\`, `\n`, `\${` or `$${` for literal `${` |
| `''…''` | Indented; strips common leading spaces; `''${` for literal `${` |
| `${expr}` | In strings, paths, attr names; expr → string, path, or `{ __toString \| outPath }` |

### Lists and attribute sets

| Syntax | Meaning |
|--------|---------|
| `[ a b (f x) ]` | Whitespace-separated; parenthesize calls |
| `{ a = 1; b = 2; }` | Unordered attrs; `;` after each binding |
| `set.attr` / `set.attr or d` | Select / default if missing |
| `set ? attr` | Has attribute |
| `rec { … }` | Attr names in scope for each other |
| `inherit x;` / `inherit (src) a b;` | `x = x;` / `a = src.a; b = src.b;` |
| `{ a.b = 1; }` | Nested path sugar |

### Functions

| Pattern | Meaning |
|---------|---------|
| `x: body` | Single arg |
| `x: y: body` | Curried; `f a b` = `(f a) b` |
| `{ a, b }: body` | Exact attrs required |
| `{ a, b, ... }: body` | Extra attrs allowed |
| `{ a ? 1 }: body` | Default if omitted |
| `args @ { a, ... }: body` | `args` = argument **as passed** (defaults not merged in) |

### `let`, `with`, control

| Form | Notes |
|------|-------|
| `let x = 1; y = 2; in body` | Local bindings; mutual refs OK |
| `with set; body` | Bring attrs into scope; **does not** shadow `let`/params |
| `if c then a else b` | Only chosen branch evaluated |
| `assert c; body` | Abort if `c` is false |

### Path vs string

- Path literals resolve relative to the **file** being evaluated; coercing a path to string copies into the [store](../02-concepts/store-path.md).
- `./foo-${name}.nix` — path antiquotation; need `/` before first `${` or the parser sees division.

### Operators (high → low)

| Op | Role |
|----|------|
| `.` | Select (tightest) |
| juxtaposition | Function application |
| `-` (unary) | Negation |
| `?` | `set ? name` |
| `++` | List concat (right-assoc) |
| `*` `/` | Multiply / divide |
| `+` `-` | Arithmetic; `+` also concats strings/paths |
| `!` | Boolean NOT |
| `//` | Attrset merge; **right wins** |
| `<` `>` `<=` `>=` | Ordered comparison |
| `==` `!=` | Equality |
| `&&` | AND (short-circuit) |
| `\|\|` | OR (short-circuit) |
| `->` | Implication (short-circuit) |
| `\|>` `<\|` | Pipe — experimental `pipe-operators`; see [pipe operators](../08-experimental-features/pipe-operators-and-lang.md) |

`+` overloads: string+string → string; path+path / path+string → path; string+path → string (path copied to store). Full table: [operators](../03-language/syntax/operators.md).

### Common builtins

Catalog: [attrset/list/string](../03-language/builtins/attrset-list-string.md) · [import/fetch](../03-language/builtins/import-and-fetch.md) · [path I/O](../03-language/builtins/path-and-filesystem.md) · [derivation](../03-language/builtins/derivation-builtins.md) · [debug](../03-language/builtins/debugging-trace.md)

Prefer `builtins.…` in libraries (avoids `with` shadowing).

| Builtin | One-liner |
|---------|-----------|
| `map` / `filter` | Map / keep where pred true |
| `foldl' op nul list` | Left fold; forces each step |
| `attrNames` / `getAttr` | Sorted names / dynamic `.` |
| `toString` / `toJSON` | Coerce / serialize |
| `typeOf e` | `"int"`, `"set"`, `"list"`, … |
| `import path` | Eval `.nix` (dir → `default.nix`); memoized |
| `fetchurl` / `fetchTarball` | URL → store path |
| `derivation attrs` | Low-level `.drv` (`name`, `system`, `builder`) |
| `trace e1 e2` | Print `e1`; return `e2` |
| `abort` / `throw` | Hard abort / soft eval error |

### Idiom snippets

Details: [callPackage](../03-language/idioms/callPackage.md) · [overlays](../03-language/idioms/overlays-pattern.md) · [rec vs fix](../03-language/idioms/rec-and-fixed-points.md) · [anti-patterns](../03-language/idioms/anti-patterns.md)

```nix
# callPackage-shaped recipe
{ stdenv, lib, dep ? null }:
stdenv.mkDerivation {
  pname = "my-pkg"; version = "1.0"; src = ./.;
  buildInputs = lib.optional (dep != null) dep;
}
# pkgs.callPackage ./pkg.nix { }  or  { dep = pkgs.zlib; }

# overlay: final = composed; prev = before this layer
final: prev: {
  myPkg = prev.callPackage ./my-pkg.nix { inherit (final) someDep; };
}

# prefer let over rec when no mutual self-ref
let a = 1; in { a = a; b = a + 1; }   # { a = 1; b = 2; }
rec { foo = "a"; bar = foo + "b"; }   # small mutual refs only
```

## Common commands

Evaluate language expressions (not package builds). `nix repl` / `nix eval` need experimental [`nix-command`](../08-experimental-features/nix-command.md) (Nix **2.34.x** stable manual — still experimental). Classic `nix-instantiate` does not.

| Command | Use |
|---------|-----|
| `nix repl` | Interactive evaluator (`nix-command`) |
| `nix eval --expr '1 + 1'` | Eval expression (`nix-command`) |
| `nix-instantiate --eval -E '1 + 1'` | Classic eval |
| `nix-instantiate --eval --strict -E '…'` | Force deep evaluation |
| `nix-instantiate --parse -E '…'` | Parse only (AST check) |

In `nix repl`: `:l <nixpkgs>`, `:p expr` (print deeply), `:t expr` (type), `:q` quit.

## See also

- [03-language](../03-language/README.md) — full language domain
- [03-language cheatsheet](../03-language/cheatsheet.md) — same material colocated with teaching pages
- [Syntax](../03-language/syntax/README.md) · [Semantics](../03-language/semantics/README.md) · [Builtins](../03-language/builtins/README.md) · [Idioms](../03-language/idioms/README.md)
- [lib helpers](../03-language/idioms/lib-helpers.md) — nixpkgs `lib` (not language builtins)
- [CLI cheatsheet](cli.md) — `nix eval` / `nix repl` flags
- [Comments and formatting](../03-language/syntax/comments-and-formatting.md)

## References

- [Nix stable manual](https://nix.dev/manual/nix/stable/)
- [Nix language](https://nix.dev/manual/nix/stable/language/)
- [Nix language syntax](https://nix.dev/manual/nix/stable/language/syntax.html)
- [Nix language operators](https://nix.dev/manual/nix/stable/language/operators.html)
- [Nix language types](https://nix.dev/manual/nix/stable/language/types.html)
- [Nix language builtins](https://nix.dev/manual/nix/stable/language/builtins.html)
- [Nix language string literals](https://nix.dev/manual/nix/stable/language/string-literals.html)
- [Nix language evaluation](https://nix.dev/manual/nix/stable/language/evaluation.html)
