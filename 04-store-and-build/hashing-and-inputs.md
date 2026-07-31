---
status: complete
---

# Hashing and Inputs

## Overview

Nix assigns each [store path](../02-concepts/store-path.md) a hash that reflects **how** the object was produced—or, for some derivation kinds, **what** it contains. For ordinary [derivations](../02-concepts/derivation.md), output paths are **input-addressed**: the hash is computed from the derivation description and the store paths of declared inputs. [Fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs) instead fix the output hash up front, so path identity follows a declared content digest. **Floating** [content-addressed](../02-concepts/content-addressed-store.md) outputs (experimental) assign paths from built content after the fact.

Understanding which inputs enter the hash—and which impurities are bounded or excluded—is central to reproducible builds and predictable cache keys.

## Details

**Input-addressed outputs (default).** When Nix registers a normal derivation, it computes each output path from the derivation’s attributes: builder, arguments, environment variables, output names, and the **store paths** of build-time dependencies. Same recipe and same input closure → same output paths on any machine. Change any declared input—source tree, dependency path, builder script, or env entry—and the hash changes and downstream paths change with it. The manual specifies the exact serialization and digest steps; at a high level, Nix hashes a canonical representation of the derivation together with its input store paths, then maps the digest into the path’s hash component.

**Path hash encoding.** Store path hashes use **Nix base-32** encoding of a **20-byte** digest (160 bits). The human-readable name suffix (`hello-2.12`, etc.) is not part of the uniqueness guarantee; the encoded digest is. See the Nix manual for the precise mapping from derivation data to digest.

**What counts as an input.** Only **declared** build inputs participate in input-addressed hashing. The builder runs in a [sandbox](builders-and-sandboxes.md) with a controlled view of the filesystem: paths listed as `src`, `buildInputs`, `nativeBuildInputs`, and similar attributes are visible; arbitrary host files outside that closure are not. Build-time environment variables are likewise limited to what the derivation records. Undeclared reads from the host therefore do not silently alter store path identity—though they can still break reproducibility if they affect the built bytes without changing declared inputs.

**Fixed-output derivations.** FODs declare `outputHash`, `outputHashAlgo`, and `outputHashMode`. Path computation for the output **ignores most derivation attributes** and keys off the declared hash (and name). The builder may fetch over the network; Nix verifies the output digest matches `outputHash` before accepting the path. Bit-identical content from different URLs yields the same store path; changed bytes require updating the declared hash.

**Content-addressed outputs (sketch).** Nix already uses fixed content-addressing in production via FODs. **Floating** content-addressed derivations—where the output hash is computed from built content rather than predeclared—require the experimental `ca-derivations` feature. They remain sandboxed like ordinary builds; the difference is path assignment after a successful build. APIs and behavior in this area are not stabilized; see [content-addressed store](../02-concepts/content-addressed-store.md) and [ca-derivations](../08-experimental-features/ca-derivations.md).

**Derivation vs output paths.** The `.drv` file itself lives at an input-addressed path derived from the derivation’s own hash. Output paths use related but distinct rules depending on output type (input-addressed, fixed-output, or experimental CA). Query tools such as `nix derivation show` and `nix-store --query --deriver` connect realized outputs back to their `.drv` and input graph.

## Examples

Conceptual scenarios (no store builds in this pass).

**Dependency bump, new path.** Package `B` depends on library `A`. Rebuilding `A` with a changed source produces a new store path for `A`; rebuilding `B` against that path yields a new path for `B` even if `B`’s own expression did not change—because `A`’s store path is an input to `B`’s hash.

**Same inputs, same path.** Two machines evaluate the same nixpkgs commit and build the same derivation with identical input closures. Both get the same output path; one may substitute from a binary cache while the other builds locally.

**FOD: URL vs content.** A `fetchurl` FOD switches mirror URL but downloads the same tarball bytes. The output store path is unchanged because `outputHash` still matches. If upstream replaces the tarball, the FOD fails until `outputHash` is updated.

**Undeclared host state.** A builder reads `/etc/localtime` without declaring it as an input. That read does not change the input-addressed path hash; two builds with different host timezones could still share a path if declared inputs match—illustrating why sandboxing and declared inputs matter for reproducibility beyond path identity alone.

## References

- [Nix reference manual — derivations](https://nix.dev/manual/nix/stable/language/derivations.html) — derivation attributes and output path assignment
- [Nix reference manual — store paths](https://nix.dev/manual/nix/stable/store/store-path.html) — path shape and hash encoding
- [Nix reference manual — store](https://nix.dev/manual/nix/stable/store/) — realization, substitution, and the store model

## See also

- [Derivation](../02-concepts/derivation.md) — build recipes and input-addressed outputs
- [Store path](../02-concepts/store-path.md) — path shape and realization
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) — declared hash and network fetches
- [Content-addressed store](../02-concepts/content-addressed-store.md) — fixed vs floating CA addressing
- [ca-derivations](../08-experimental-features/ca-derivations.md) — experimental floating CA feature
- [Builders and sandboxes](builders-and-sandboxes.md) — controlled build environment and declared inputs
