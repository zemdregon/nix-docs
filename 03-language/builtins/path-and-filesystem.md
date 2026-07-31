---
status: complete
---

# Path and Filesystem

## Overview

Path builtins read host files at **evaluation time**, copy trees into the store, or inspect path-shaped values. They are a major [purity boundary](../semantics/purity-boundaries.md): the same expression can yield different results when the filesystem changes unless paths are pinned (hashes, flakes locks, or already-valid store paths).

Related: string-ish path helpers `baseNameOf` and `dirOf` work on paths or strings; they do not open files. Importing expressions from paths is covered under [import and fetch](import-and-fetch.md).

## Details

### Path values vs store copies

A path literal such as `./src` is a path value. Using it where a derivation expects sources usually causes Nix to **copy** that tree into the store. Prefer explicit control with `builtins.path` when you need filtering, a chosen store name, a flat hash, or a known `sha256` under pure evaluation.

### Reading and probing

| Builtin | Role |
|---------|------|
| `readFile path` | File contents as a string |
| `readDir path` | Attrset of entry name → `"regular"` / `"directory"` / `"symlink"` / `"unknown"` |
| `readFileType path` | Type of one filesystem node |
| `pathExists path` | Whether the path exists at eval time |
| `hashFile type path` | Hash of file contents (`md5` / `sha1` / `sha256` / `sha512`) |

These observe the host. Restricted or pure evaluation modes limit what may be read; see purity boundaries.

### Filtering into the store

**`builtins.path { path; name?; filter?; recursive?; sha256?; }`** copies `path` into the store with optional controls:

- `name` — store basename (useful when the source name has illegal characters)
- `filter` — same predicate shape as `filterSource`: `(path: type: bool)`
- `recursive` — default `true` (NAR hash of a tree); `false` requires a regular file and uses a flat hash (fetchurl-like)
- `sha256` — expected content hash; required for many pure-eval uses of arbitrary paths

**`filterSource pred path`** is the older filter API. Prefer `builtins.path` with `name` when filtering trees that already live in the store: `filterSource` embeds the input directory name (including its hash) in the output name, so filtered-out changes can still force rebuilds.

Predicate types for both filters: `"regular"`, `"directory"`, `"symlink"`, `"unknown"`. Excluding a directory drops its whole subtree. Device nodes and FIFOs cannot be copied even if the predicate returns true.

### Path string helpers

| Builtin | Role |
|---------|------|
| `baseNameOf x` | Last path component of a path or string (string trailing `/` rules differ slightly from GNU `basename`) |
| `dirOf s` | Everything before the final `/` (dirname-like) |
| `toPath s` | **Deprecated** — use `/. + "/abs"` or `./. + "/rel"` instead |
| `isPath e` | Type predicate |

### Lookup paths

`<nixpkgs>` desugars to `builtins.findFile builtins.nixPath "nixpkgs"`. `nixPath` is the configured search-path list (`nix-path` / `NIX_PATH` / `-I`). Each entry is `{ prefix; path; }` where `path` may be a local directory, channel URL, HTTP(S) tarball, or (with flakes) a flake URL. Not available or not useful the same way under pure flake evaluation.

### Environment and store location

| Builtin | Notes |
|---------|------|
| `getEnv name` | Env var or `""`; under pure eval ambient vars evaluate to `""` |
| `storeDir` | Logical store directory from the active store URL |

## Examples

```nix
# Drop .git / .svn noise when copying a tree into the store
builtins.path {
  path = ./.;
  name = "mysrc";
  filter = path: type:
    !(type == "directory" && baseNameOf path == ".git");
}

# Legacy filterSource (prefer builtins.path for store inputs)
builtins.filterSource
  (path: type: type != "directory" || baseNameOf path != ".svn")
  ./source-dir

builtins.readDir ./A
# e.g. { B = "regular"; C = "directory"; }

builtins.pathExists ./missing.nix  # => false
```

## References

- [Nix language — Built-ins](https://nix.dev/manual/nix/stable/language/builtins.html) — `path`, `filterSource`, `readFile`, `findFile`, …
- [Nix language — Syntax](https://nix.dev/manual/nix/stable/language/syntax.html) — path literals and lookup-path syntax

## See also

- [Antiquotation and paths](../syntax/antiquotation-and-paths.md)
- [Purity boundaries](../semantics/purity-boundaries.md)
- [Import and fetch](import-and-fetch.md)
- [Store path](../../02-concepts/store-path.md)
