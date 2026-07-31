---
status: complete
---

# Content-Addressed Store

## Overview

In the classic Nix model, [store paths](store-path.md) are **input-addressed**: the path hash reflects the [derivation](derivation.md) and its inputs, not a direct digest of the built files alone. **Content-addressed** storage is the alternative: a path’s identity follows a **content hash** of the store object (its file data and related metadata), so the same bits map to the same path regardless of how they were produced.

Nix already uses fixed content-addressing for [fixed-output derivations](fixed-output-derivation.md) (FODs), where the hash is declared up front. **Floating content-addressed derivations**—where the output hash is computed after the build—are **experimental** and require enabling the `ca-derivations` feature. For implementation detail and flags, see [ca-derivations](../08-experimental-features/ca-derivations.md).

## Details

**Input-addressed vs content-addressed.** An input-addressed path changes when any declared input changes, even if the builder happens to produce identical file contents. A content-addressed path is keyed to the output’s digest (per `outputHashMode` and `outputHashAlgo` in the manual), so identity tracks content rather than the full build recipe.

**Fixed vs floating.** **Fixed-output** content-addressing (FODs) predeclares the expected hash; the builder may use the network, and Nix verifies the result. **Floating** content-addressed derivations set `__contentAddressed = true` with `outputHashAlgo` and `outputHashMode` but **without** `outputHash`; Nix assigns the store path from the built output’s content address. By default floating CA builds are sandboxed like ordinary derivations (path assignment is the experimental split, not automatic network access); they may still declare impure builders when needed, unlike FODs which always get network for the fetch.

**Experimental status.** Floating content-addressed outputs require the [`ca-derivations` experimental feature](https://nix.dev/manual/nix/stable/language/advanced-attributes.html#adv-attr-__contentAddressed). Typical configuration:

```ini
extra-experimental-features = ca-derivations
```

Derivations that produce floating CA outputs also require the `ca-derivations` system feature on builders, so remote machines without the feature will not schedule those builds. Treat APIs, attributes, and behavior in this area as subject to change until stabilization; see [ca-derivations](../08-experimental-features/ca-derivations.md).

**Relation to FODs and fetches.** FODs are the stabilized, production-facing part of content-addressing today—especially for fetches where the hash must be fixed before network access. Floating CA is aimed at broader cases (for example, deduplicating builds that produce the same output from different input graphs), but remains experimental.

**Substitution and caching.** Content-addressed paths still participate in the same store lifecycle as input-addressed ones: realization, substitution from binary caches, and garbage collection keyed by store path. The difference is how that path name is computed.

## Examples

**Already in wide use: FOD output.** A `fetchurl` result lives at a path determined by its declared `outputHash`, not by the fetch URL or builder string. That is fixed content-addressing in practice.

**Experimental: floating CA derivation.** With `ca-derivations` enabled, a derivation may set `__contentAddressed = true` along with `outputHashAlgo` and `outputHashMode`. After a successful sandboxed build, Nix content-addresses the output; two builds that produce identical output data can yield the same store path even when their non-CA input-addressed recipes would differ.

**Contrast with a normal package.** `stdenv.mkDerivation` without CA attributes produces input-addressed outputs: bump a dependency hash and you get new store paths for dependents, even if the rebuilt artifact bytes were unchanged.

## References

- [Nix reference manual — content-addressing derivation outputs](https://nix.dev/manual/nix/stable/store/derivation/outputs/content-address) — fixed and floating CA outputs
- [Nix reference manual — advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) — `__contentAddressed`, `outputHash*`, derivation kinds
- [Nix reference manual](https://nix.dev/manual/nix/) — store and experimental features

## See also

- [Store path](store-path.md) — default input-addressed paths
- [Derivation](derivation.md) — build recipes and output types
- [Fixed-output derivation](fixed-output-derivation.md) — stabilized fixed content-addressing
- [ca-derivations](../08-experimental-features/ca-derivations.md) — experimental feature deep dive
- [Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md) — input-addressed identity vs bit-for-bit output
