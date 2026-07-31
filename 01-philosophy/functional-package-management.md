---
status: complete
---

# Functional Package Management

## Overview

Nix treats packages as **values** in a purely functional language: a build is a function from declared inputs to an output in the [Nix store](../02-concepts/store-path.md). Installed software is not mutated in place; new builds produce new store paths, and switching versions means selecting different values—not overwriting shared directories like `/usr`.

This model is the package-management side of [purity and reproducibility](purity-and-reproducibility.md). Build-time enforcement of “only declared inputs” is [hermetic builds](hermetic-builds.md). For motivation and problem framing, see [Why Nix](why-nix.md). The original formulation is Eelco Dolstra’s *The Purely Functional Software Deployment Model*.

## Details

### Builds as functions (inputs → outputs)

A [derivation](../02-concepts/derivation.md) describes how to compute an output from fixed inputs (source, dependencies, build script, environment). Given the same inputs, the function yields the same result; the store path name encodes a cryptographic hash of those inputs so distinct recipes never collide. Changing a dependency changes the path—see [hashing and inputs](../04-store-and-build/hashing-and-inputs.md).

### Variants, not in-place upgrades

Installing a package with different flags, versions, or dependency sets is calling the same builder with different arguments. Each variant gets its own hashed store path; old variants remain available until garbage-collected. Profiles and NixOS [generations](../02-concepts/generation.md) *select* which value is active; they do not overwrite another package’s files. That selection model underpins [immutability and rollback](immutability-and-rollback.md).

### Composing package sets

Nixpkgs is a large attribute set of packages. `callPackage` wires a builder to the arguments it expects from that set; [overlays](../02-concepts/overlay.md) extend or override entries without editing the base tree in place—functional composition over immutable data. The composed set is still a value: applying an overlay yields a new package set, not a mutated global registry.

### Closures as values

A runnable artifact is not a single path but its [closure](../02-concepts/closure.md): the root output plus every runtime dependency, transitively. That graph is computed from declared references and stored as a value, not assembled by mutating a global prefix. Substitution from a binary cache replaces “build this function” with “fetch this already-computed result” when the store path matches—same identity either way.

### Contrast with traditional layouts

Classic Unix installs share a mutable tree (`/usr`, `/usr/local`): files are overwritten, dependencies are implicit, and “upgrading” destroys the previous install. Nix’s functional model keeps every variant addressable and side by side, which is why [hermetic builds](hermetic-builds.md) matter: undeclared host state would break the inputs→outputs contract.

## Examples

**Same package, two variants.** Building `hello` (or any package) with and without a feature flag / overlay override yields two store paths—both coexist; profile or environment selection picks which value is active. No shared `/usr/lib` is overwritten.

**Overlay without forking.** An overlay that sets `python3 = prev.python312` adds a variant to the composed package set; underlying definitions stay unchanged until the overlay is applied:

```nix
# Illustrative overlay shape (nixpkgs overlay API).
self: prev: {
  python3 = prev.python312;
}
```

**Closure inspection.** On a machine with Nix and a realized path:

```bash
# Replace PATH with a store path you already have (e.g. from `nix-build -A hello`).
nix-store --query --requisites /nix/store/…-hello-…
```

That lists the closure—the dependency graph as a set of paths, not a scan of `/usr/lib`. Requires a local Nix store; the command itself is from the Nix reference manual’s store query interface.

## References

- [Nix reference manual](https://nix.dev/manual/nix/) — store, derivations, and the evaluation model
- [Nix manual — derivations](https://nix.dev/manual/nix/stable/language/derivations.html)
- [nix.dev](https://nix.dev/) — ecosystem overview and learning material
- E. Dolstra, *The Purely Functional Software Deployment Model* ([PhD thesis](https://edolstra.github.io/pubs/phd-thesis.pdf)) — original formulation; background, not a normative spec for current Nix

## See also

- [Why Nix](why-nix.md)
- [Purity and reproducibility](purity-and-reproducibility.md)
- [Hermetic builds](hermetic-builds.md)
- [Immutability and rollback](immutability-and-rollback.md)
- [Derivation](../02-concepts/derivation.md)
- [Closure](../02-concepts/closure.md)
