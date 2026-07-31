---
status: complete
---

# Closure

## Overview

A **closure** is a [store path](store-path.md) plus every path reachable from it via recorded **references**—transitively. It is the unit Nix copies, substitutes, or deploys when something must run or build elsewhere: not a single binary, but the full dependency graph rooted at that path.

Which root you choose matters. The closure of a [derivation](derivation.md) (`.drv`) is the **build-time** dependency set; the closure of an **output** path is the **runtime** set. Deploying or caching software almost always means transferring an output closure.

## Details

**How it is computed.** Each store object records its references: other store paths it depends on. Nix walks those edges transitively—starting from declared refs in derivations and build outputs, plus any paths discovered when scanning for embedded `/nix/store` strings—to produce the closure as a set of paths. The glossary term for a member of that set is a **requisite**.

**Build-time vs runtime.** Instantiating a package yields a `.drv` whose closure includes compilers, fetchers, and other build-only inputs. Realizing the default output yields a path whose closure is what the program needs to *run*—typically smaller. Multiple outputs (e.g. `out` vs `dev`) have different closures so documentation or headers need not travel with every runtime deploy.

**What it is for.** Remote builds, binary-cache substitution, `nix copy`, and profile activation all operate on closures. Substitution fetches every missing member; deployment copies the same set so the root can execute with no undeclared host dependencies. A path is **valid** only when its whole closure is readable in the store.

**Disk and GC.** Every profile, generation, and build result holds its closure alive by reference. That is why `/nix/store` grows with side-by-side versions and why [garbage collection](../04-store-and-build/garbage-collection.md) only removes paths unreachable from any root—understanding closures explains both footprint and what you must keep pinned. Path identity and why dependency bumps enlarge closures are covered in [hashing and inputs](../04-store-and-build/hashing-and-inputs.md).

## Examples

**Inspect a runtime closure.** `nix-store --query --requisites /nix/store/…-hello-2.12` lists every store path required to run that output—dependencies of dependencies included. Direct edges only: `--references`.

**Deploy to another host.** With the `nix-command` experimental feature, `nix copy --to ssh://server /nix/store/…-myapp` transfers the closure for `myapp`; the server needs no matching `/usr` layout, only those paths.

**Why two variants coexist.** Building the same package with different inputs yields two root paths and two closures. Both remain on disk until nothing references either graph—typical when multiple projects pin different dependency sets.

## References

- [Nix manual — Glossary (closure)](https://nix.dev/manual/nix/stable/glossary.html) — closure, requisite, reachable, validity
- [Nix manual — Nix store](https://nix.dev/manual/nix/stable/store/) — store objects and references
- [Nix manual — `nix-store`](https://nix.dev/manual/nix/stable/command-ref/nix-store.html) — `--query --requisites` and related closure queries
- [Nix manual — `nix copy`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-copy.html) — copying closures between stores (requires `nix-command`)

## See also

- [Store path](store-path.md)
- [Derivation](derivation.md)
- [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md)
- [Garbage collection](../04-store-and-build/garbage-collection.md)
- [Profile](profile.md)
- [Functional package management](../01-philosophy/functional-package-management.md)
