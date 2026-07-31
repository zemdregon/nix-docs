---
status: complete
---

# nix store

## Overview

The **`nix store`** command group is the modern CLI surface for direct manipulation of the [Nix store](../../02-concepts/store-path.md): adding paths, querying metadata, deleting objects, running garbage collection, copying closures between stores, verifying integrity, and related low-level operations. It lives under the unified `nix` binary and requires the experimental [`nix-command`](../../08-experimental-features/nix-command.md) feature—the same gate as `nix build` and `nix flake`.

Several store workflows that classic tools folded into `nix-store` are split across sibling commands in the new CLI. **`nix path-info`** answers “what is this path, how big is its closure, is it on a substituter?” **`nix copy`** moves closures between local, SSH, and binary-cache stores. This page covers `nix store` subcommands at overview depth and points to those related commands where the modern split differs from [classic `nix-store`](../classic-cli/nix-store.md).

Like other Nix 3 commands, `nix store` is marked **experimental**—subcommands and flags can change between releases. For the authoritative list and per-command options, use the [manual entry for `nix store`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-store.html) and the [new CLI index](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html).

## Details

### Experimental feature and store model

Enable `nix-command` in `nix.conf` or pass `--extra-experimental-features nix-command` per invocation. Without it, store operations use the classic [`nix-store`](../classic-cli/nix-store.md) tool instead.

Operations apply to the **local store** by default (`/nix/store`, or whatever `store` is set to in `nix.conf`). Many subcommands accept `--store` to target another store URI (SSH host, binary cache, chroot store). Store URIs and protocol behavior are covered in [Store protocols](../../04-store-and-build/store-protocols.md) and [Binary caches](../../04-store-and-build/binary-caches.md).

### `nix store` subcommands (overview)

The manual lists every subcommand; the table below summarizes the ones most often encountered. Deprecated aliases (`add-file`, `add-path`) are omitted here—prefer `nix store add`.

| Subcommand | Role |
|------------|------|
| `add` | Add a file or directory to the store (replaces classic `--add` / fixed-output adds). |
| `cat` | Print a file inside a store path to stdout (classic log/cat-style reads). |
| `copy-log` | Copy build logs between stores. |
| `copy-sigs` | Copy signatures for store paths from substituters. |
| `delete` | Remove paths from a store (classic `--delete`). |
| `diff-closures` | Show packages/versions added or removed between two closures. |
| `dump-path` | Serialize a store path to stdout in NAR format (classic `--export` of a single path). |
| `gc` | Run garbage collection on a store (classic `--gc`; see [Garbage collection](../../04-store-and-build/garbage-collection.md)). |
| `info` | Test whether a store URI is reachable (useful before remote copy or SSH builds). |
| `ls` | Show information about a path in the store (overlaps with query-style inspection). |
| `make-content-addressed` | Rewrite a path or closure to content-addressed form. |
| `optimise` | Deduplicate identical files via hard links (classic `--optimise`). |
| `path-from-hash-part` | Resolve a store path from its hash component. |
| `prefetch-file` | Download a file into the store. |
| `repair` | Repair corrupted or missing store paths where possible. |
| `sign` | Sign store paths with a local key. |
| `verify` | Check integrity of store paths (classic `--verify`). |
| `roots-daemon` | Daemon that returns GC roots on request (internal/daemon integration). |

For full syntax, flags, and any subcommands added after your Nix version, see the [manual](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-store.html)—do not treat wiki tables as exhaustive.

### Related commands outside `nix store`

**`nix path-info`** — Query [store paths](../../02-concepts/store-path.md): print paths for installables, closure sizes, NAR sizes, signatures, JSON metadata, and check existence on another store (including a binary cache). It does **not** build or substitute; paths must already exist unless you run `nix build` first. Largely replaces `nix-store --query` / `--references` / size introspection workflows with installable-aware UX.

**`nix copy`** — Copy closures **between stores** (`--from` / `--to` URIs). Typical uses: seed a remote machine via SSH, push to a local `file://` binary cache, or pull from `https://cache.nixos.org`. This is the modern replacement for classic `nix-store --export` / `--import` bulk transfer patterns, with store URIs instead of raw NAR pipes. See [Binary caches](../../04-store-and-build/binary-caches.md) for cache layout and signing expectations.

**Global `--repair`** — On several `nix` commands (including evaluation/build paths), `--repair` can rewrite missing or corrupted store files during evaluation or rebuild missing outputs. That overlaps conceptually with `nix store repair` but applies at different stages; check the manual for the command you are running.

### Contrast with classic `nix-store`

Classic [`nix-store`](../classic-cli/nix-store.md) is a single binary with long-style flags (`--query`, `--delete`, `--gc`, `--verify`, `--repair`, `--export`, `--import`, `--add`, etc.). The modern CLI **splits** responsibilities:

- **Mutation and store-local ops** → `nix store …` subcommands.
- **Closure metadata and installables** → `nix path-info`.
- **Cross-store transfer** → `nix copy`.

Classic commands remain available on typical installs; scripts and older docs still reference them. [Garbage collection](../../04-store-and-build/garbage-collection.md) is documented in terms of live/dead paths and roots—`nix store gc` and `nix-store --gc` share the same underlying collector; profile-generation cleanup may still go through `nix-collect-garbage` or `nix store gc` depending on flags and version.

Physical layout under `/nix/store`, GC root directories, and profiles are store-domain topics—see [Nix store layout](../../04-store-and-build/nix-store-layout.md) rather than repeating them here.

## Examples

Check that an SSH store is reachable before copying a closure:

```bash
nix store info --store ssh://user@build-host
```

Run garbage collection on the local store (same family as `nix-store --gc`):

```bash
nix store gc
```

Delete specific paths from the local store:

```bash
nix store delete /nix/store/…-obsolete-package
```

Inspect closure size for an installable (requires `nix-command`; often paired with flakes for `nixpkgs#…` refs):

```bash
nix path-info --recursive --closure-size --human-readable nixpkgs#hello
```

Copy a system closure to another host, allowing the destination to substitute missing paths:

```bash
nix copy --substitute-on-destination --to ssh://server /run/current-system
```

Verify and repair store integrity (when corruption is suspected):

```bash
nix store verify --all
nix store repair /nix/store/…-broken-path
```

## References

- [Nix reference manual — `nix store`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-store.html)
- [Nix reference manual — `nix path-info`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-path-info.html)
- [Nix reference manual — `nix copy`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-copy.html)
- [Nix reference manual — new CLI (`nix`)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html)
- [Nix reference manual — store](https://nix.dev/manual/nix/stable/store/)

## See also

- [nix-store](../classic-cli/nix-store.md) — classic store binary and flag-oriented workflows
- [Store path](../../02-concepts/store-path.md) — what store objects are and how paths are named
- [Nix store layout](../../04-store-and-build/nix-store-layout.md) — on-disk layout and `/nix/var/nix` state
- [Garbage collection](../../04-store-and-build/garbage-collection.md) — live/dead paths, roots, and GC configuration
- [Binary caches](../../04-store-and-build/binary-caches.md) — substituters and pushing/pulling closures
- [nix-command](../../08-experimental-features/nix-command.md) — experimental feature that enables `nix store`
