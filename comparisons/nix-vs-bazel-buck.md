---
status: complete
---

# Nix vs Bazel / Buck

## Overview

**Bazel** and **Buck** are monorepo-oriented build systems. They model a repository as a graph of **targets** and **actions** (compile, link, test, …), run those actions in a **hermetic-ish** sandbox with declared inputs, and reuse work through local and **remote** caches (and, with remote execution, run actions on workers). Rules are **language-oriented** (`BUILD` / `BUCK` files, Starlark or similar); outputs land under the build output tree (for example `bazel-out/`, `bazel-bin/`). See [Bazel concepts](https://bazel.build/basics).

**Nix** packages software and systems as immutable [store paths](../02-concepts/store-path.md) under `/nix/store`. The unit is a [derivation](../02-concepts/derivation.md) and its [closure](../02-concepts/closure.md)—the transitive set of store paths needed to build or run—not a repo target label. Builds aim for [hermeticity](../01-philosophy/hermetic-builds.md) via the sandbox and declared inputs; fetches use [fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs) with pinned hashes. Nix is **language-agnostic** at the core and also covers dev shells, CI closures, and (with NixOS) OS configuration.

Both pursue reproducible, isolated builds, but at different layers: Bazel/Buck optimize **in-repo** build graphs and incremental rebuilds; Nix optimizes **content-addressed** artifacts and sharing across projects and machines. They can complement each other (for example nixpkgs packaging Bazel, or wrapping a prebuilt artifact in a FOD)—not drop-in substitutes.

**Buck note:** Meta’s **Buck2** (Rust rewrite, current direction) and legacy **Buck1** share the monorepo target model but differ in implementation and CLI; treat “Buck” as a family unless a doc pins a version.

## Details

**Unit of packaging.**

| | Bazel / Buck | Nix |
|---|---|---|
| Artifact | Target outputs (binaries, libraries, test logs) under the build output tree | Store paths; a [closure](../02-concepts/closure.md) is the transitive set to run or deploy |
| Identity | Target label (`//pkg:rule`) plus action/cache keys; remote cache entries by content hash | Store path digest under `/nix/store/<hash>-name` |
| Graph | Action graph scoped to the monorepo and its external deps | Derivation graph; closures can span nixpkgs, flakes, and custom repos |
| Sharing | Disk cache and optional remote cache/execution across CI and developers | Identical store paths in profiles, shells, and substituters ([binary caches](../04-store-and-build/binary-caches.md)) |
| Hermeticity | Declared deps, sandboxed actions, toolchain pins (exact behavior depends on rules and setup) | Build sandbox + referential integrity; network only on FODs with declared `outputHash` |
| Sweet spot | Large single-repo builds/tests with incremental and distributed cache | Reproducible packages, dev envs, cross-project deps, OS config |

**Build model.** Bazel/Buck evaluate `BUILD`/`BUCK` rules into an action graph: changing an input invalidates downstream actions, and cache hits skip re-execution. Nix evaluates Nix expressions into derivations; changing an input changes store paths upstream. Bazel’s remote cache is action-oriented; Nix’s substituters are store-path-oriented. Neither replaces the other’s cache protocol.

**Complementary use (don’t overclaim).** Common patterns:

- **Tooling in nixpkgs:** install or pin Bazel/Buck via Nix so CI and laptops share the same compiler toolchain wrapper—not the same as compiling the monorepo with Nix.
- **FOD for fixed upstream artifacts:** a tarball or binary built elsewhere (including Bazel CI) can enter the Nix store via a FOD if the content hash is pinned; Nix then treats it like any other store input.
- **Bazel inside a derivation:** possible for niche packaging (run Bazel as the builder script with sandbox paths), but not the default integration path and easy to fight the sandbox unless inputs are declared carefully.

Nix does not parse `BUILD` files; Bazel does not manage `/nix/store` or NixOS generations.

**What each is not.** Bazel/Buck are not general-purpose OS or distro package managers: they do not give you side-by-side store versions, `nix copy` of closures, or declarative host config. Nix is not a monorepo build orchestrator: it has no first-class target graph, action keys, or Bazel-style remote execution for arbitrary repo rules out of the box.

## Examples

**Same logical “hello binary,” different artifacts:**

```bash
# Bazel: build a target; artifact lives in the output tree (path depends on config/platform)
bazel build //examples/hello:hello
# e.g. bazel-bin/examples/hello/hello

# Nix: build a package; artifact is a store path (here via nixpkgs)
nix-build '<nixpkgs>' -A hello --no-out-link
# e.g. /nix/store/…-hello-2.12/bin/hello
```

Inspect what each system considers the deliverable:

```bash
# Bazel: list outputs for a built target
bazel cquery //examples/hello:hello --output=files

# Nix: transitive runtime closure of the hello store path
nix-store --query --requisites $(nix-build '<nixpkgs>' -A hello --no-out-link)
```

The Bazel row is a **labeled target output** in a workspace cache tree; the Nix row is a **content-addressed path** shared wherever that hash appears.

## References

- [Bazel docs — Bazel basics](https://bazel.build/basics) — workspaces, targets, actions, hermetic builds, caching
- [Nix manual — Store path](https://nix.dev/manual/nix/stable/store/store-path.html) — `/nix/store/<digest>-name` identity
- [Hermetic builds](../01-philosophy/hermetic-builds.md) — Nix sandbox and declared inputs
- [Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md) — evaluation vs build purity in Nix

## See also

- [Nix vs Docker](nix-vs-docker.md) — runtime images vs store closures (another “artifact unit” comparison)
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) — pinning external/build-artifact bytes into the store
- [CI with Nix](../11-development/ci-with-nix.md) — substituters and reproducible CI closures
- [Closure](../02-concepts/closure.md) — transitive store-path unit Nix deploys
