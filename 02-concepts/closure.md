---
status: complete
---

# Closure

## Overview

A **closure** is a [store path](store-path.md) plus every path it needs at runtime, transitively. It is the unit Nix copies, substitutes, or deploys when something must run elsewhere—not a single binary, but the full dependency graph rooted at that path.

## Details

**How it is computed.** Each store object records its **references**: other store paths it depends on. Nix walks those edges transitively—starting from declared refs in [derivations](derivation.md) and build outputs, plus any paths discovered when scanning for embedded `/nix/store` references—to produce the closure as a set of paths.

**What it is for.** When you build remotely, push to a cache, or activate a profile, Nix works on closures, not lone paths. Substitution fetches every member of the closure that is missing locally; deployment copies the same set so the root path can execute with no undeclared host dependencies.

**Disk and GC.** Every profile, generation, and build result holds its closure alive by reference. That is why `/nix/store` grows with side-by-side versions and why [garbage collection](../04-store-and-build/garbage-collection.md) only removes paths unreachable from any root—understanding closures explains both footprint and what you must keep pinned.

## Examples

**Inspect a closure.** `nix-store --query --requisites /nix/store/…-hello-2.12` lists every store path required to run that output—dependencies of dependencies included.

**Deploy to another host.** With the `nix-command` experimental feature, `nix copy --to ssh://server /nix/store/…-myapp` transfers the closure for `myapp`; the server needs no matching `/usr` layout, only those paths.

**Why two variants coexist.** Building the same package with different inputs yields two root paths and two closures. Both remain on disk until nothing references either graph—typical when multiple projects pin different dependency sets.

## References

- [Nix manual — Nix store](https://nix.dev/manual/nix/stable/store/) — store objects and references
- [Nix manual — `nix-store`](https://nix.dev/manual/nix/stable/command-ref/nix-store.html) — `--query --requisites` and related closure queries
- [Nix manual — `nix copy`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-copy.html) — copying closures between stores (requires `nix-command`)

## See also

- [Store path](store-path.md)
- [Derivation](derivation.md)
- [Functional package management](../01-philosophy/functional-package-management.md)
- [Garbage collection](../04-store-and-build/garbage-collection.md)
