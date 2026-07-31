---
status: complete
---

# Content-Addressed Store

## Overview

In the classic Nix model, [store paths](store-path.md) are **input-addressed**: the path hash reflects the [derivation](derivation.md) and its inputs, not a direct digest of the built files alone. **Content-addressed** storage is the alternative: a path’s identity follows a **content hash** of the store object (its file data and related metadata, per `outputHashMode` and `outputHashAlgo`), so the same bits can map to the same path regardless of how they were produced.

Nix already uses **fixed** content-addressing for [fixed-output derivations](fixed-output-derivation.md) (FODs), where `outputHash*` is declared up front and verified after fetch. **Floating** content-addressed derivations—where the output hash is computed after the build—are **experimental** and require enabling the `ca-derivations` feature; treat APIs and semantics as unstable until stabilization. For flags, attribute combinations, and builder scheduling, see [ca-derivations](../08-experimental-features/ca-derivations.md). For how path hashes are computed across derivation kinds, see [hashing and inputs](../04-store-and-build/hashing-and-inputs.md).

## Details

**Input-addressed vs content-addressed.** An input-addressed path changes when any declared input changes, even if the builder happens to produce identical file contents. A content-addressed path is keyed to the output’s digest, so identity tracks content rather than the full build recipe. That distinction matters for cache reuse: two builds with different input graphs but identical output bytes can share a content-addressed path (fixed FODs today; floating CA when enabled), while input-addressed outputs always diverge when any input store path changes.

**Three addressing modes.** Nix distinguishes ordinary derivations, FODs, and floating CA outputs by which attributes are set. The manual treats these as mutually exclusive kinds:

| Mode | Path identity from | `outputHash` | Network | Status |
|------|-------------------|--------------|---------|--------|
| Input-addressed (default) | Derivation attributes + input store paths | — | Sandboxed (no network) | Stable |
| Fixed-output (FOD) | Predeclared `outputHash*` (+ name) | Required | Allowed; verified after build | Stable |
| Floating CA | Built output content (`outputHashMode` / `outputHashAlgo`) | Must **not** be set | Sandboxed by default (like ordinary derivations) | **Experimental** (`ca-derivations`) |

**Fixed content-addressing (FODs).** FODs stabilize content-addressing for cases where the hash must be known before the build—especially fetches. The builder may use the network; Nix digests the output and fails if it does not match the declared `outputHash`. Path computation ignores most derivation attributes (URL, builder string, etc.), so bit-identical content from different mirrors yields the same store path. See [fixed-output derivation](fixed-output-derivation.md) and the illustrative [fod-fetchurl.nix](../meta/examples/fod-fetchurl.nix) snippet.

**Floating content-addressing (experimental).** With `ca-derivations` enabled, a derivation may set `__contentAddressed = true` together with `outputHashAlgo` and `outputHashMode`, and **without** `outputHash`. Nix builds in the sandbox like an ordinary derivation, then assigns the store path from the content address of the built files. The experimental split is **path assignment policy**, not automatic network access—unlike FODs, floating CA does not by itself grant impure capabilities. Motivation: deduplicate outputs across different input-addressed recipes when the built bytes match (for example, avoiding mass rebuilds when a fetch URL changes but downloaded content does not).

**Enabling floating CA.** Add the experimental feature flag:

```ini
extra-experimental-features = ca-derivations
```

Derivations that produce floating CA outputs also require the `ca-derivations` **system feature** on builders (`requiredSystemFeatures` / `system-features`), so remote machines without the feature will not schedule those builds. On multi-user installs the daemon needs the flag as well. Do not rely on floating CA in production without pinning Nix versions; see [ca-derivations](../08-experimental-features/ca-derivations.md).

**Store lifecycle.** Content-addressed paths participate in the same store lifecycle as input-addressed ones: **realization** (build or substitute), **substitution** from binary caches (NAR integrity checks still apply), and **garbage collection** keyed by store path. The difference is only how the path name is computed before or after the build completes.

**Relation to the `.drv` file.** The derivation file itself remains input-addressed at its own `.drv` path. Output paths use related but distinct rules depending on output type; query tools such as `nix derivation show` and `nix-store --query --deriver` connect realized outputs back to their `.drv` and input graph.

## Examples

**Fixed CA in production: `fetchurl`.** A `fetchurl` result lives at a path determined by its declared `outputHash`, not by the fetch URL or builder string. That is fixed content-addressing—the stabilized form in wide use today. [fod-fetchurl.nix](../meta/examples/fod-fetchurl.nix) shows the attribute shape (placeholder hash; not evaluated in this vault).

**Experimental: floating CA attributes.** With `ca-derivations` enabled, a derivation may look like:

```nix
{
  __contentAddressed = true;
  outputHashMode = "nar";
  outputHashAlgo = "sha256";
  # no outputHash — path assigned from built content after the build
}
```

Combine those with the usual `name` / `system` / `builder` / `args` (or a wrapper such as `stdenv.mkDerivation`). After a successful sandboxed build, Nix content-addresses the output. Two builds that produce identical output data can yield the same store path even when their input-addressed recipes would differ.

**Contrast with a normal package.** `stdenv.mkDerivation` without CA attributes produces input-addressed outputs: bump a dependency’s store path and dependents get new paths, even if the rebuilt artifact bytes were unchanged.

## References

- [Nix reference manual — content-addressing derivation outputs](https://nix.dev/manual/nix/stable/store/derivation/outputs/content-address) — fixed and floating CA outputs, system features
- [Nix reference manual — advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) — `__contentAddressed`, `outputHash*`, derivation kinds
- [Nix reference manual — experimental feature: ca-derivations](https://nix.dev/manual/nix/stable/development/experimental-features.html#xp-feature-ca-derivations) — flag purpose and status

## See also

- [Store path](store-path.md) — default input-addressed paths
- [Derivation](derivation.md) — build recipes and output types
- [Fixed-output derivation](fixed-output-derivation.md) — stabilized fixed content-addressing
- [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md) — how path hashes are computed
- [ca-derivations](../08-experimental-features/ca-derivations.md) — experimental feature deep dive
- [Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md) — input-addressed identity vs bit-for-bit output
