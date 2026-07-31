---
status: complete
---

# Antiquotation and Paths

## Overview

In Nix documentation, **antiquotation** usually means embedding expressions in a literal with `${…}`—the same mechanism as [string interpolation](strings-and-interpolation.md), but applied to **path** literals. A path antiquotation such as `./foo-${name}.nix` keeps the result a path value while substituting `name` into the path text.

Path literals are a distinct type from strings. They resolve against the filesystem, can include lookup paths like `<nixpkgs>`, and behave differently when coerced to strings. General interpolation rules live in [strings and interpolation](strings-and-interpolation.md); this page focuses on path syntax, resolution, and store copying.

## Details

**Path vs division.** A path literal must contain at least one `/`. When `${…}` appears, at least one slash must come **before** the first interpolation or the parser treats `.` as numeric division. `./a.${foo}/b` is a path; `a.${foo}/b` is division.

**Relative and absolute paths.** Relative literals (`./`, `../`, or segments without a leading `/`) resolve against the **directory of the file being evaluated**, not the working directory. Absolute paths (`/etc/…`) are valid but make expressions less portable; prefer relative paths for sources beside the `.nix` file, or a string literal when you only need a fixed filesystem location in config output. See [literals](literals.md).

**Canonical form.** Path values are normalized like `realpath` **without** following symlinks: no trailing slashes, no duplicate slashes, and no `.` or `..` components remain in the value. The path does not need to exist on disk to be a valid path value.

**Home paths.** A leading `~` expands to the user's home directory (`~/src` → `/home/user/src`). These are **forbidden in pure evaluation**; see [purity boundaries](../semantics/purity-boundaries.md) and [pure eval and impure](../../07-flakes/pure-eval-and-impure.md).

**Lookup paths.** Tokens such as `<nixpkgs>` or `<nixpkgs/lib>` are lookup path literals. They resolve to path values via `NIX_PATH` (or flake equivalents in locked workflows). Prefer pinning inputs in flakes over implicit lookup paths when reproducibility matters.

**Path antiquotation.** Inside a path literal, `${expr}` may appear after the required slash. The expression must evaluate to a string or path (or an attribute set with `__toString` / `outPath` as for string interpolation). Each segment is concatenated into the path text before resolution rules apply.

**Coercion and the store.** Converting a path to a string—via `"${./src}"`, concatenating a string with a path (`"prefix-" + ./file`), or similar—requires the path to refer to a **readable file or directory**. Nix copies that content into the [store](../../02-concepts/store-path.md) and uses the resulting store path string. This is how `./source.nix` and `${./src}` end up as fixed, content-addressed inputs in derivations. Path values used without string coercion (e.g. passed to `import`) do not automatically copy to the store.

## Examples

**Path antiquotation vs division.**

```nix
let name = "default";
in {
  config = ./foo-${name}.nix;   # path
  # broken = foo-${name}.nix;   # parsed as division, not a path
}
```

**Relative resolution.** In `/projects/pkg/default.nix`, `./src` means `/projects/pkg/src`.

**Lookup path.**

```nix
import <nixpkgs> { }
# resolves <nixpkgs> via NIX_PATH, then imports that path
```

**Store copy on coercion.**

```nix
"${./data.json}"
# copies data.json next to this file into /nix/store/…-data.json
```

**Home path (impure eval only).**

```nix
~/projects/my-app   # expands under $HOME; error in pure evaluation
```

## References

- [Nix language syntax — Path](https://nix.dev/manual/nix/stable/language/syntax.html) — path literals, slashes, interpolation, lookup paths
- [String interpolation](https://nix.dev/manual/nix/stable/language/string-interpolation.html) — `${…}` in paths and strings
- [Nix language types — Path](https://nix.dev/manual/nix/stable/language/types.html) — canonical paths and store copying

## See also

- [Literals](literals.md)
- [Strings and interpolation](strings-and-interpolation.md)
- [Purity boundaries](../semantics/purity-boundaries.md)
- [Store path](../../02-concepts/store-path.md)
- [Pure eval and impure](../../07-flakes/pure-eval-and-impure.md)
