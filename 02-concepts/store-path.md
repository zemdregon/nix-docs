---
status: complete
---

# Store Path

## Overview

A **store path** is the on-disk location of a single object in the Nix store. Every built package, fetched source, and derivation file lives at a path of the form `/nix/store/<hash>-<name>`. The hash identifies the object's **build identity**—traditionally from the derivation and its inputs (input-addressed)—so distinct inputs never share a path. Once realized, a store path is **immutable**; upgrades and rollbacks add or select different paths rather than modifying existing ones.

Store paths are the unit Nix uses for **caching**, **garbage collection**, and **substitution**: if a path already exists locally or on a binary cache, Nix can skip building it. How digests are computed from inputs (or content) is covered in [hashing and inputs](../04-store-and-build/hashing-and-inputs.md).

## Details

**Path shape.** The store root is `/nix/store` (configurable per store). Each entry is `<hash>-<human-readable-name>`, for example `/nix/store/…-hello-2.12`. The hash portion is a 32-character Nix base-32 encoding of a 20-byte digest. The name aids debugging; the digest is what makes the path unique. Treat the digest as opaque for most operations—exact fingerprint rules differ by store-object kind.

**Input-addressed identity.** For a normal [derivation](derivation.md), the hash is computed from the derivation and the store paths of its dependencies. Same recipe and same input closure → same output path on any machine that can build or substitute it. Change any input and you get a new path; old paths remain until [garbage collection](../04-store-and-build/garbage-collection.md) removes unreferenced ones. [Fixed-output derivations](fixed-output-derivation.md) instead key the path off a declared output hash. See [Immutability and rollback](../01-philosophy/immutability-and-rollback.md).

**Realization and validity.** A path becomes **valid** when Nix **realizes** it—builds it, copies it from a substitute, or imports it—and every path in its [closure](closure.md) is likewise valid. Until then, only the derivation (`.drv` file) may exist. After realization, the tree at that path is not modified in place.

**Caching and substitution.** Before building, Nix checks whether the output path is already in the local store. If not, it can **substitute** a bit-identical copy from a configured binary cache. The store path is the key for both local reuse and remote fetch.

**GC and references.** Each store object records **references** to other store paths. Garbage collection deletes paths nothing references anymore. Profiles, generations, and other [GC roots](../04-store-and-build/garbage-collection.md) keep paths alive. The closure of a path is the full set reachable via those references.

**Layout on disk.** Store objects share a common directory layout (metadata, `bin/`, `lib/`, etc. depending on type). Physical organization under `/nix/store` is described in [Nix store layout](../04-store-and-build/nix-store-layout.md).

## Examples

- **Inspect a path:** `nix-store --query --references /nix/store/…-hello-2.12` lists direct dependencies; `--requisites` lists the full closure.
- **Path from a build:** With `nix-command` (and usually `flakes`) enabled, `nix build nixpkgs#hello` prints or symlinks to the realized output under `/nix/store/…`. Classic equivalent: `nix-build '<nixpkgs>' -A hello`.
- **Same inputs, same path:** Rebuilding the same derivation with unchanged dependencies yields the identical store path; bumping a dependency hash produces a new one alongside the old.

## References

- [Nix manual — Nix store](https://nix.dev/manual/nix/stable/store/) — store objects, paths, and realization
- [Nix manual — Store path](https://nix.dev/manual/nix/stable/store/store-path.html) — path shape and digest encoding
- [Nix manual — Derivations](https://nix.dev/manual/nix/stable/language/derivations.html) — how output paths are assigned
- [Nix manual — `nix-store`](https://nix.dev/manual/nix/stable/command-ref/nix-store.html) — `--query --references` / `--requisites`

## See also

- [Derivation](derivation.md) — build recipe whose output is a store path
- [Closure](closure.md) — runtime dependency set rooted at a path
- [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md) — what enters the path digest
- [Fixed-output derivation](fixed-output-derivation.md) — content-keyed paths for fetches
- [Immutability and rollback](../01-philosophy/immutability-and-rollback.md) — why paths are never patched in place
- [Nix store layout](../04-store-and-build/nix-store-layout.md) — filesystem layout under `/nix/store`
