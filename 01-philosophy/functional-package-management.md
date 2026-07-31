---
status: complete
---

# Functional Package Management

## Overview

Nix treats packages as **values** in a purely functional language: a build is a function from declared inputs to an output in the [Nix store](../02-concepts/store-path.md). Installed software is not mutated in place; new builds produce new store paths, and switching versions means selecting different values—not overwriting shared directories like `/usr`.

This model is the package-management side of [purity and reproducibility](purity-and-reproducibility.md). For motivation and problem framing, see [Why Nix](why-nix.md). The original formulation is Eelco Dolstra’s *The Purely Functional Software Deployment Model*.

## Details

**Builds as functions.** A [derivation](../02-concepts/derivation.md) describes how to compute an output from fixed inputs (source, dependencies, build script). Given the same inputs, the function yields the same result; the store path name encodes a content hash so distinct inputs never collide.

**Variants, not upgrades.** Installing a package with different flags, versions, or dependency sets is calling the same builder with different arguments. Each variant gets its own hashed store path; old variants remain available until garbage-collected.

**Composing package sets.** Nixpkgs is a large attribute set of packages. `callPackage` wires a builder to the arguments it expects from that set; [overlays](../02-concepts/overlay.md) extend or override entries without editing the base tree in place—functional composition over immutable data.

**Closures as values.** A runnable artifact is not a single path but its [closure](../02-concepts/closure.md): the root output plus every runtime dependency, transitively. That graph is computed and stored as a value, not assembled by mutating a global prefix.

**Contrast with traditional layouts.** Classic Unix installs share a mutable tree (`/usr`, `/usr/local`): files are overwritten, dependencies are implicit, and “upgrading” destroys the previous install. Nix’s functional model keeps every variant addressable and side by side.

## Examples

**Same package, two variants.** Building `hello` with and without a feature flag yields two store paths—both coexist; profile or environment selection picks which value is active.

**Overlay without forking.** An overlay that sets `python3 = prev.python312` adds a variant to the composed package set; underlying definitions stay unchanged until the overlay is applied.

**Closure inspection.** `nix-store --query --requisites` on a store path lists the closure—the dependency graph materialized as a set of paths, not a scan of `/usr/lib`.

## References

- [Nix reference manual](https://nix.dev/manual/nix/) — store, derivations, and the evaluation model
- [nix.dev](https://nix.dev/) — ecosystem overview and learning material
- E. Dolstra, *The Purely Functional Software Deployment Model* ([PhD thesis](https://edolstra.github.io/pubs/phd-thesis.pdf)) — original formulation of functional package management

## See also

- [Why Nix](why-nix.md)
- [Purity and Reproducibility](purity-and-reproducibility.md)
- [Derivation](../02-concepts/derivation.md)
- [Store path](../02-concepts/store-path.md)
- [Closure](../02-concepts/closure.md)
- [Overlay](../02-concepts/overlay.md)
