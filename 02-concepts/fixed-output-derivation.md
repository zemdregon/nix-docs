---
status: complete
---

# Fixed-Output Derivation

## Overview

A **fixed-output derivation** (FOD) is a [derivation](derivation.md) whose output hash is declared in advance. The builder may use the network, but Nix checks the built output against that hash; a mismatch fails the build. The resulting [store path](store-path.md) is determined by the declared hash (and the derivation name), not by the full input graph of the fetch step.

FODs are how Nix brings upstream sources and other remote artifacts into the store while keeping the rest of the build [hermetic](../01-philosophy/hermetic-builds.md). Common examples are `fetchurl`, `fetchFromGitHub`, and similar fetch helpers in nixpkgs.

## Details

**Declared output hash.** A FOD sets `outputHash`, `outputHashAlgo`, and `outputHashMode`. Together they fix the expected content address of the output. After the builder runs, Nix digests the output and compares it to `outputHash`; if they differ, the derivation fails rather than silently changing downstream inputs.

**Network access.** Unlike ordinary input-addressed derivations, a FOD builder is allowed network access. That is the controlled impurity: the outside world may be consulted, but only through outputs whose hash was pinned ahead of time. See [purity and reproducibility](../01-philosophy/purity-and-reproducibility.md).

**Output path identity.** For a normal derivation, the hash in a store path comes from the derivation and its input closure. For a FOD, path computation ignores most derivation attributes and depends on `outputHash*` and `name`. Changing a fetch URL without changing the downloaded content therefore does not change the store path—only changing the fetched bytes (or the declared hash) does.

**Fixed content-addressing.** In the Nix manual, FODs are the stabilized form of **fixed-output content-addressing**: the content address is known before the build. [Floating content-addressed derivations](content-addressed-store.md) extend the same addressing model but are experimental and do not predeclare the hash.

**Impure environment variables.** Attributes such as `impureEnvVars` (for example proxy settings used by `fetchurl`) are only permitted on FODs, where the output hash bounds the effect of those impurities.

**Single output.** FODs produce a single output. Fetch helpers wrap `builtins.derivation` (or equivalent) with the required `outputHash*` attributes and a builder that downloads or copies the fixed content.

## Examples

**Pinned tarball fetch.** A `fetchurl` call declares `url`, `outputHash`, and related fields. Nix downloads the file, stores it under `/nix/store/<hash>-<name>`, and later build steps consume that path without further network access.

**Upstream changes the artifact.** If the upstream tarball changes but the expression still declares the old `outputHash`, the FOD fails. Updating the hash (after verifying the new content) is the intentional workflow for tracking upstream changes.

**URL change, same content.** Mirror or redirect changes that serve bit-identical content leave the FOD output path unchanged, because path identity follows the declared hash, not the URL string.

## References

- [Nix reference manual — advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) — `outputHash`, `outputHashAlgo`, `outputHashMode`, and derivation kinds
- [Nix reference manual — content-addressing derivation outputs](https://nix.dev/manual/nix/stable/store/derivation/outputs/content-address) — fixed-output content-addressing and fetch rationale
- [Nix reference manual](https://nix.dev/manual/nix/) — store model and derivations

## See also

- [Derivation](derivation.md) — input-addressed build recipes
- [Store path](store-path.md) — path shape and realization
- [Content-addressed store](content-addressed-store.md) — floating CA outputs (experimental)
- [Hermetic builds](../01-philosophy/hermetic-builds.md) — sandboxing and controlled fetches
- [Purity and reproducibility](../01-philosophy/purity-and-reproducibility.md) — why FODs exist
