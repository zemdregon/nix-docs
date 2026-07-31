---
status: complete
---

# Nix Store Layout

## Overview

The **Nix store layout** is how realized store objects appear on disk when the store is backed by a filesystem. By default everything lives under `/nix/store`: one entry per object, named `<hash>-<name>`. The hash is an opaque digest; the name is human-readable. Together they form a [store path](../02-concepts/store-path.md)—the filesystem’s view of a single immutable object.

This page describes **where** objects sit on disk and how that relates to Nix’s referential model. **Input-addressed identity**—how an output path is computed from a [derivation](../02-concepts/derivation.md) and its inputs—is covered in [Hashing and inputs](hashing-and-inputs.md).

## Details

**Store root.** The configurable store directory (commonly `/nix/store`) is a flat namespace of object paths. There is no hierarchy by package name or version—only sibling entries, each one store path.

**Path anatomy.** Each entry is `/nix/store/<hash>-<name>`:

- **Hash (digest)** — 20 bytes, rendered as 32 ASCII characters in the Nix base-32 alphabet. It identifies the object in this store.
- **Name** — A readable label (often `pname-version`, or a derivation basename ending in `.drv`). It does not determine uniqueness; the full path does.

Example: `/nix/store/pg2zfrrbm58ynbjshhzkgg4q466spinf-hello-2.12.3`.

**Identity from inputs.** For a normal (input-addressed) derivation, the output path’s digest is derived from the build recipe and the store paths of its inputs—not from scanning the finished tree after the build. Same inputs → same path; change an input → a new path. Digests are treated as opaque for most operations; see [Hashing and inputs](hashing-and-inputs.md) for the fingerprint rules.

**What lives under `/nix/store`.** Once [realized](../02-concepts/store-path.md), the tree at a path is never modified in place. Common object kinds:

- **Derivation files (`.drv`)** — Serialized build recipes. They are ordinary store paths whose name ends in `.drv` (for example `…-which-2.25.drv`). Evaluation can write them; realization builds their outputs.
- **Output trees** — Whatever the builder produced: `bin/`, `lib/`, `share/`, and so on. Internal layout is package-defined, not fixed by Nix.
- **Sources and other artifacts** — Fetched tarballs, patches, and similar: same rule—one store path, one immutable tree (or file).

Nix does not mandate a single internal layout for all outputs; it mandates that each object occupies exactly one path under the store root.

**Filesystem as interface.** When the store exposes a filesystem representation, store paths are how you inspect, execute, and link to objects (`/nix/store/…-foo/bin/foo`). The path string is the stable handle; the digest prefix makes collisions impossible across distinct objects.

**Related state under `/nix/var/nix` (not the store dir).** Other Nix state usually lives under `/nix/var/nix/` and **references** store paths without being store objects itself:

| Path | Role |
|------|------|
| `/nix/var/nix/db/` | SQLite database of valid paths and references |
| `/nix/var/nix/gcroots/` | Symlinks that are [GC roots](garbage-collection.md)—paths (and their [closures](../02-concepts/closure.md)) kept alive |
| `/nix/var/nix/profiles/` | Profile and generation symlink farms |

Profiles and roots keep paths alive during garbage collection; `/nix/store` holds the actual content.

**One store dir per machine (usually).** Store paths embed the store directory prefix. References between objects assume a **single** store root: a path string from store A is not valid in store B. You cannot copy a store object into a store with a different store directory and expect referential integrity—rebuild (or substitute) into the target store instead. Do not merge unrelated `/nix/store` trees and expect `.drv` references to resolve.

**Layout vs addressing.** Input addressing answers “what path will this build get?” On-disk layout answers “what file or directory is that path?” Both use `<hash>-<name>` naming; identity is a graph concept, layout is where realized nodes land in the filesystem.

## Examples

**Anatomy of a realized output** (verified on a local store):

```text
/nix/store/pg2zfrrbm58ynbjshhzkgg4q466spinf-hello-2.12.3/
  bin/hello
  share/info/hello.info
  share/locale/…
```

The digest is 32 characters (`pg2zfrrbm58ynbjshhzkgg4q466spinf`); the name after the hyphen is for humans. `bin/` and `share/` come from the package build, not from Nix’s store schema.

**A derivation path vs its output:**

```text
/nix/store/000p8d2aqs6mbb5axv0q2vdpiyp713dm-which-2.25.drv   # recipe
/nix/store/hp02kp2b3j9qr31vd72sd2sndx9bwshn-which-2.25/      # realized output
  bin/which
```

**List the flat store root:**

```bash
ls /nix/store | head
```

You see only `<hash>-<name>` entries—no `pkgs/` or version hierarchy. Names ending in `.drv` are derivations; the rest are outputs, sources, or other objects.

**Inspect GC roots (outside the store dir):**

```bash
ls -la /nix/var/nix/gcroots
nix-store --gc --print-roots | head
```

Roots under `/nix/var/nix/gcroots` (and profile generations) pin store paths; they are not themselves entries in `/nix/store`.

**Query references (graph, not directory names):**

```bash
nix-store --query --tree /nix/store/pg2zfrrbm58ynbjshhzkgg4q466spinf-hello-2.12.3
```

Shows reference structure among paths; it does not change how directories are named on disk.

## References

- [Nix reference manual — store](https://nix.dev/manual/nix/stable/store/) — store model and filesystem representation
- [Nix reference manual — store path format](https://nix.dev/manual/nix/stable/store/store-path.html) — digest, name, and path syntax
- [Nix reference manual — garbage collector roots](https://nix.dev/manual/nix/stable/package-management/garbage-collector-roots.html) — `/nix/var/nix/gcroots` symlinks

## See also

- [Store path](../02-concepts/store-path.md) — identity, realization, and caching of a single path
- [Derivation](../02-concepts/derivation.md) — build recipe whose outputs become store paths
- [Closure](../02-concepts/closure.md) — dependency set referenced from a path
- [Hashing and inputs](hashing-and-inputs.md) — how output digests are computed
- [Garbage collection](garbage-collection.md) — reclaiming unreferenced paths under the store root
