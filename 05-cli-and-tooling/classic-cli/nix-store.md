---
status: complete
---

# nix-store

## Overview

`nix-store` is the classic CLI for **primitive operations on the Nix store**: building or fetching [store paths](../../02-concepts/store-path.md), querying reference graphs, garbage collection, export/import, integrity checks, and disk optimisation. Each invocation takes exactly one operation flag (`--realise`, `--query`, `--gc`, and so on).

Higher-level commands (`nix-build`, `nix-env`, `nix-collect-garbage`) wrap subsets of this behaviour. You rarely need `nix-store` day to day, but it remains the direct interface to store mechanics documented in the [Store and Build](../../04-store-and-build/README.md) domain.

The experimental [`nix store`](../modern-cli/nix-store-ops.md) command group replaces many of these operations with subcommands (`nix store gc`, `nix store delete`, `nix store verify`, …) and adds store-URL support for remote stores. Classic `nix-store` always targets the local store (via the Nix daemon in multi-user setups).

## Details

**Invocation model.** `nix-store` _operation_ [_options…_] [_paths…_]. Only one operation per run. Per-operation help: `nix-store --help --realise` or `man nix-store-realise`.

### Realisation (`--realise` / `-r`)

Build or fetch the store objects for each argument path:

- **Derivation (`.drv`)** — Substitute or build each output in the derivation's [closure](../../02-concepts/closure.md); run the builder when substitutes are unavailable.
- **Non-derivation path** — If not already valid, try to substitute its closure from [substituters](../../04-store-and-build/binary-caches.md).

Realised output paths are printed on stdout. This is essentially what [`nix-build`](nix-build.md) does after evaluation. Useful flags include `--dry-run` (plan only), `--check` (rebuild and compare for determinism), and `--add-root` _path_ (register a [GC root](../../04-store-and-build/garbage-collection.md) symlink).

### Query (`--query` / `-q`)

Inspect metadata about paths already in the store. One query mode per invocation (default: `--outputs`). Common queries:

| Query | Prints |
|-------|--------|
| `--references` | Immediate dependencies of each path |
| `--requisites` / `-R` | Full closure (all transitive dependencies) |
| `--referrers` | Paths in the store that reference the argument |
| `--tree` | Nested ASCII reference tree |
| `--graph` | Graphviz `dot` format for the reference graph |
| `--deriver` / `-d` | Derivation that built the path (or `unknown-deriver`) |
| `--roots` | GC roots pointing at the path |
| `--hash` / `--size` | Content hash or serialised size from the Nix database |

Arguments may be symlinks outside `/nix/store`; the query follows the target. `--use-output` / `-u` applies the query to a derivation's output path; `--force-realise` / `-f` builds first.

### Garbage collection (`--gc`)

Delete store paths not reachable from [GC roots](../../04-store-and-build/garbage-collection.md). Without subflags, all **dead** paths are removed and freed bytes are reported.

| Subflag | Effect |
|---------|--------|
| `--print-roots` | List roots used for the scan |
| `--print-live` | List reachable paths (no deletion) |
| `--print-dead` | List deletable paths (no deletion) |
| `--max-freed` _bytes_ | Stop after freeing at least _bytes_ (`K`/`M`/`G`/`T` suffixes) |

Behaviour is also influenced by `keep-derivations` and `keep-outputs` in `nix.conf`. [`nix-collect-garbage`](nix-collect-garbage.md) is mostly an alias with extra profile-generation deletion flags.

### Delete (`--delete`)

Remove specific paths, but only when safe—the same liveness rules as `--gc`. A targeted alternative to full collection: delete one dead path without scanning the entire store. With `--ignore-liveness`, root reachability is ignored, but paths still cannot be deleted if other store paths refer to them.

### Optimise (`--optimise`)

Reduce on-disk store size by hard-linking identical regular files and symlinks across paths. Files match when their [NAR](https://nix.dev/manual/nix/stable/glossary.html#gloss-nar) serialisations are identical (content and executable bit for files; target for symlinks). Typical savings are on the order of 25–35%. Does not change logical store contents or references.

### Export and import (`--export` / `--import`)

Serialise store objects to stdout (`--export`) or read them from stdin (`--import`) in Nix's import/export format for copying into another store.

**Important:** `--export` does **not** automatically include a path's closure. Export every requisite explicitly—usually via `nix-store --query --requisites`. Import fails if referenced paths are missing in the target store. For SSH closure transfer, `nix-copy-closure` is the usual tool; see [Store protocols](../../04-store-and-build/store-protocols.md).

### Verify (`--verify`)

Check consistency between the Nix SQLite database and the filesystem under [store layout](../../04-store-and-build/nix-store-layout.md). Repairs inconsistencies automatically (often caused by manual edits under `/nix/store` or non-Nix tools).

| Flag | Effect |
|------|--------|
| `--check-contents` | Hash every valid path and compare to database records (slow on large stores) |
| `--repair` | Re-download or rebuild missing or corrupted valid paths |

Related per-path operations: `--verify-path`, `--repair-path`.

### Classic vs modern CLI

| Classic | Modern (experimental) |
|---------|----------------------|
| `nix-store --realise` | `nix build`, `nix copy` |
| `nix-store --query --requisites` | `nix path-info --closure` |
| `nix-store --gc` | `nix store gc` |
| `nix-store --delete` | `nix store delete` |
| `nix-store --optimise` | `nix store optimise` |
| `nix-store --export` / `--import` | `nix copy`, `nix store dump-path` |
| `nix-store --verify` | `nix store verify`, `nix store repair` |

Modern commands accept `--store` URLs (`auto`, `ssh://…`, `https://…`) for remote operations; classic `nix-store` does not.

## Examples

**Realise a derivation** (same core step as `nix-build`):

```bash
nix-store --realise $(nix-instantiate ./package.nix)
```

**Show runtime closure and dependency tree:**

```bash
nix-store --query --requisites /nix/store/…-hello-2.12
nix-store --query --tree /nix/store/…-hello-2.12
```

**Run GC and inspect without deleting:**

```bash
nix-store --gc
nix-store --gc --print-dead
```

**Export a closure for offline import** (export all requisites, not just the top path; `$path` must already be a valid store path—realize it first if needed):

```bash
# path=/nix/store/…-hello-…   # already-realized output
nix-store --export $(nix-store --query --requisites "$path") > closure.nar
nix-store --import < closure.nar
```

**Verify store integrity** (optionally with content checks):

```bash
nix-store --verify
nix-store --verify --check-contents --repair
```

**Reclaim disk via deduplication:**

```bash
nix-store --optimise
```

## References

- [Nix reference manual — `nix-store`](https://nix.dev/manual/nix/stable/command-ref/nix-store.html)
- [Nix reference manual — `nix-store --realise`](https://nix.dev/manual/nix/stable/command-ref/nix-store/realise.html)
- [Nix reference manual — `nix-store --query`](https://nix.dev/manual/nix/stable/command-ref/nix-store/query.html)
- [Nix reference manual — `nix-store --gc`](https://nix.dev/manual/nix/stable/command-ref/nix-store/gc.html)

## See also

- [Store and Build](../../04-store-and-build/README.md) — store model, builders, caches, GC
- [Nix store layout](../../04-store-and-build/nix-store-layout.md) — on-disk layout under `/nix/store`
- [Garbage collection](../../04-store-and-build/garbage-collection.md) — live/dead paths, roots, `nix.conf` settings
- [Store path](../../02-concepts/store-path.md) — path identity and realisation
- [Closure](../../02-concepts/closure.md) — transitive dependency sets queried with `--requisites`
- [nix-collect-garbage](nix-collect-garbage.md) — GC alias with profile generation cleanup
- [nix store](../modern-cli/nix-store-ops.md) — modern store subcommands
