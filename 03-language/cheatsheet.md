---
status: complete
---

# Language Cheatsheet

Dense quick reference for the Nix expression language. Deeper treatment lives in sibling pages under [syntax](syntax/README.md), [semantics](semantics/README.md), [builtins](builtins/README.md), and [idioms](idioms/README.md).

## See also

- [Cheatsheets: Language](../cheatsheets/language.md) — root cheatsheet hub
- [Laziness](semantics/laziness.md) — call-by-need, memoization, what forces what
- [Anti-patterns](idioms/anti-patterns.md) — `with`, `rec`, and other footguns

## Syntax quick ref

Full syntax: [literals](syntax/literals.md) · [strings](syntax/strings-and-interpolation.md) · [lists/attrs](syntax/lists-and-attrsets.md) · [functions](syntax/functions.md) · [let/with](syntax/let-in-and-with.md) · [operators](syntax/operators.md) · [if/assert](syntax/conditionals-and-asserts.md) · [paths](syntax/antiquotation-and-paths.md)

**Laziness:** values evaluate only when demanded; unused `let` bindings and attr fields are free. `if`, `&&`, `||`, `->` short-circuit. See [laziness](semantics/laziness.md).

### Literals

| Form | Examples |
|------|----------|
| Integer | `0`, `42`, `-7` |
| Float | `3.14`, `.27e13` |
| Boolean | `true`, `false` |
| Null | `null` |
| Path | `./src`, `/etc/nixos`, `<nixpkgs>` — must contain `/`; distinct from strings |
| URI token | `https://example.com` — parsed as **string**, not path |

### Strings

| Form | Notes |
|------|-------|
| `"…"` | Escapes: `\"`, `\\`, `\n`, `\${` for literal `${` |
| `''…''` | Indented; dedents common leading spaces; `''${` for literal `${` |
| `${expr}` | In strings, paths, and attr names; expr → string, path, or `{ __toString \| outPath }` |

### Lists and attribute sets

| Syntax | Meaning |
|--------|---------|
| `[ a b (f x) ]` | Whitespace-separated elements; parenthesize calls |
| `{ a = 1; b = 2; }` | Unordered attrs; `;` after each binding |
| `set.attr` | Select; `set.attr or default` if missing |
| `set ? attr` | Has attribute |
| `rec { … }` | Attr names in scope for each other |
| `inherit x;` | `x = x;` |
| `inherit (src) a b;` | `a = src.a; b = src.b;` |
| `{ a.b = 1; }` | Nested path sugar |

### Functions

| Pattern | Meaning |
|---------|---------|
| `x: body` | Single arg |
| `x: y: body` | Curried; `f a b` = `(f a) b` |
| `{ a, b }: body` | Set pattern — exact attrs required |
| `{ a, b, ... }: body` | Allow extra attrs |
| `{ a ? 1 }: body` | Default if `a` omitted |
| `args @ { a, ... }: body` | `args` = argument **as passed** (defaults not merged in) |

### `let`, `with`, control

| Form | Notes |
|------|-------|
| `let x = 1; y = 2; in body` | Local bindings; mutual refs OK in same block |
| `with set; body` | Bring set attrs into scope; **does not** shadow `let`/params |
| `if c then a else b` | Only chosen branch evaluated |
| `assert c; body` | Abort with backtrace if `c` is false |

### Path vs string

- Path literals resolve relative to the **file** being evaluated; coercion to string copies into the [store](../02-concepts/store-path.md).
- `./foo-${name}.nix` — path antiquotation; needs `/` before first `${` or parser sees division.

### Common operators

| Op | Role |
|----|------|
| `.` | Select (tightest) |
| juxtaposition | Function application |
| `++` | List concat |
| `+` | Add numbers; concat strings/paths (mixed rules — see [operators](syntax/operators.md)) |
| `//` | Shallow attrset merge; **right wins** on duplicate keys |
| `==` `!=` `<` `>` | Comparison / equality |
| `&&` `\|\|` `!` `->` | Boolean; short-circuit |
| `?` | `set ? name` |

Precedence table: [operators](syntax/operators.md).

## Common builtins

Catalog: [attrset/list/string](builtins/attrset-list-string.md) · [import/fetch](builtins/import-and-fetch.md) · [derivation](builtins/derivation-builtins.md) · [debugging](builtins/debugging-trace.md)

Many names exist both as globals (`map`) and as `builtins.map`; prefer `builtins.…` in libraries.

| Builtin | One-liner |
|---------|-----------|
| `map f list` | Map over list |
| `filter pred list` | Keep elements where `pred` is true |
| `attrNames set` | Sorted list of attribute names |
| `getAttr s set` | Dynamic `.` — abort if missing |
| `toString e` | Coerce to string (paths, ints, lists, derivations via `outPath`, …) |
| `toJSON e` | Serialize value to JSON string |
| `import path` | Evaluate `.nix` at path (dirs → `default.nix`); memoized |
| `fetchurl arg` | Download URL → store path |
| `fetchTarball arg` | Download and unpack tarball → store path |
| `derivation attrs` | Low-level `.drv` primitive (`name`, `system`, `builder` required) |
| `trace e1 e2` | Print `e1` on stderr; return `e2` |
| `abort s` | Hard abort (not skipped by some query tools) |
| `throw s` | Evaluation error (some query tools skip derivations that throw) |
| `typeOf e` | Type name string (`"int"`, `"set"`, `"list"`, …) — guard before typed ops |

## Idiom snippets

Details: [callPackage](idioms/callPackage.md) · [overlays](idioms/overlays-pattern.md) · [rec vs fix](idioms/rec-and-fixed-points.md)

**callPackage-shaped recipe** (nixpkgs helper, not a builtin):

```nix
# pkg.nix
{ stdenv, lib, dep ? null }:
stdenv.mkDerivation {
  pname = "my-pkg";
  version = "1.0";
  src = ./.;
  buildInputs = lib.optional (dep != null) dep;
}

# usage
pkgs.callPackage ./pkg.nix { }
pkgs.callPackage ./pkg.nix { dep = pkgs.zlib; }
```

**Overlay layer** — `final` = composed set; `prev` = before this layer:

```nix
final: prev: {
  myPkg = prev.callPackage ./my-pkg.nix {
    inherit (final) someDep;
  };
  someDep = prev.someDep.overrideAttrs (old: { /* … */ });
}
```

**`rec` vs `let`** — prefer `let` when attrs don't need mutual self-reference; avoid `rec { a = a; }` shadowing outer names (infinite recursion):

```nix
# clear local binding
let a = 1; in { a = a; b = a + 1; }   # { a = 1; b = 2; }

# explicit self when needed
let self = { x = 1; y = self.x + 1; }; in self

# rec only for small, self-contained mutual refs
rec { foo = "a"; bar = foo + "b"; }
```

## References

- [Nix language](https://nix.dev/manual/nix/stable/language/)
- [Nix language syntax](https://nix.dev/manual/nix/stable/language/syntax.html)
- [Nix language builtins](https://nix.dev/manual/nix/stable/language/builtins.html)
