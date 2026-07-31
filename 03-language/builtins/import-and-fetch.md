---
status: complete
---

# Import and Fetch

## Overview

**Import** loads another Nix expression from a path. **Fetch** builtins download or materialize external trees/files into the store so expressions can depend on pinned or remote inputs. Together they are how Nix splits code across files and how non-flake workflows pull nixpkgs or other sources.

Many fetchers are unavailable or stricter under restricted / pure evaluation; prefer hash-pinned or flake-locked inputs when reproducibility matters. See [purity boundaries](../semantics/purity-boundaries.md) and [flake](../../02-concepts/flake.md).

## Details

### `import` and `scopedImport`

`import path` parses and evaluates the expression at `path`. If `path` is a directory, `default.nix` inside it is used. The imported file must not rely on free variables from the call site — pass arguments instead:

```nix
y = import ./foo.nix x;   # foo.nix: x: x + 456
```

Unlike some languages, `import` is an ordinary function (also available as a global). Results are memoized per path.

`scopedImport scope path` is like `import` but injects attributes from `scope` as variables in the imported file (shadowing builtins with the same names). It does **not** memoize evaluation the way `import` does — side effects such as `trace` can differ across calls.

### Classic fetchers

| Builtin | Role |
|---------|------|
| `fetchurl arg` | Download a URL; return store path of the file. `arg` is a URL string or `{ url; name?; }` |
| `fetchTarball arg` | Download and unpack a `.tar` (gzip/bzip2/xz). URL string or `{ url; sha256; }`. Single top-level directory is stripped |
| `fetchGit arg` | Git tree → store. URL or attrset (`url`, `rev`, `ref`, `submodules`, `shallow`, `lfs`, …) |
| `fetchMercurial` | Mercurial analogue (global; less common) |

Without a content hash, tarball/git fetches consult caches and `tarball-ttl`; tip-of-branch fetches can change across runs. Hash-pinned `fetchTarball { url; sha256; }` is the usual reproducibility fix outside flakes.

`fetchurl` / `fetchTarball` are not available in restricted evaluation mode. `fetchGit` with a local worktree and no `ref`/`rev` uses current tracked file contents (`git ls-files`), including uncommitted changes to those files.

**Verified fetches** (`verifyCommit`, `publicKey` / `publicKeys`) require the `verified-fetches` experimental feature.

### Experimental / flake-oriented fetchers

| Builtin | Feature flag | Role |
|---------|--------------|------|
| `fetchTree input` | `fetch-tree` | Generic tree/file fetch by `type` (`file`, `git`, `tarball`, `github`, …); returns `{ outPath; narHash; … }` |
| `fetchClosure args` | `fetch-closure` | Pull a store path closure from a binary cache (`fromStore`, `fromPath`, optional CA rewrite) |
| `getFlake ref` | `flakes` | Evaluate a flake; unlocked refs need impure eval |
| `parseFlakeRef` / `flakeRefToString` | `flakes` | Flake ref ↔ attrset |

`fetchTree` downloads are cached under `$XDG_CACHE_HOME/nix` with similar TTL behavior when `narHash` is missing. Prefer supplying `narHash` so the result can be substituted and verified. URL-like flake refs as `fetchTree` arguments additionally need the `flakes` feature.

`fetchClosure` is preferred over `storePath` when you must refer to an existing store object: it names the cache and can rewrite to content-addressed paths so trust setup is simpler.

### `storePath`

`builtins.storePath /nix/store/…` registers a dependency on an **existing** store path without re-copying it under a new hash. Plain path literals pointing at store paths *do* copy again. Not available in pure evaluation mode — prefer `fetchClosure` or flake inputs.

## Examples

Offline (no network): `import` is a regular function; pass arguments into the imported expression:

```nix
# sibling.nix contains:  x: x + 1
import ./sibling.nix 41
# => 42
```

Fetcher shapes (from the builtins manual). These may download unless substituted/cached; pin hashes/`rev` for reproducibility. Not run in this wiki’s offline verify pass:

```nix
import (fetchTarball {
  url = "https://github.com/NixOS/nixpkgs/archive/nixos-26.05.tar.gz";
  sha256 = "…";  # real hash required
}) { }

builtins.fetchGit {
  url = "https://github.com/NixOS/nix.git";
  rev = "841fcbd04755c7a2865c51c1e2d3b045976b7452";
  ref = "1.11-maintenance";
}

# Experimental (fetch-tree); prefer narHash when possible
builtins.fetchTree {
  type = "github";
  owner = "NixOS";
  repo = "nixpkgs";
  rev = "ae2e6b3958682513d28f7d633734571fb18285dd";
}
```

## References

- [Nix language — Built-ins](https://nix.dev/manual/nix/stable/language/builtins.html) — `import`, `fetch*`, `getFlake`, …
- [Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — `fetch-tree`, `fetch-closure`, `flakes`, `verified-fetches`

## See also

- [Path and filesystem](path-and-filesystem.md)
- [Purity boundaries](../semantics/purity-boundaries.md)
- [Channel](../../02-concepts/channel.md)
- [Flake](../../02-concepts/flake.md)
- [Fixed-output derivation](../../02-concepts/fixed-output-derivation.md)
