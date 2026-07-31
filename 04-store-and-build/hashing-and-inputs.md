---
status: complete
---

# Hashing and Inputs

## Overview

Nix assigns each [store path](../02-concepts/store-path.md) a hash that reflects **how** the object was produced—or, for some derivation kinds, **what** it contains. For ordinary [derivations](../02-concepts/derivation.md), output paths are **input-addressed**: the hash is computed from the derivation description and the store paths of declared inputs. [Fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs) instead fix the output hash up front, so path identity follows a declared content digest. **Floating** [content-addressed](../02-concepts/content-addressed-store.md) outputs (experimental) assign paths from built content after the fact.

Understanding which inputs enter the hash—and which impurities are bounded or excluded—is central to reproducible builds and predictable cache keys. Binary caches verify transferred bytes via **NAR** digests recorded in `.narinfo`; see [substitutes and NAR info](substitutes-and-narinfo.md).

## Details

### Input-addressed outputs (default)

When Nix registers a normal derivation, it computes each output path from the derivation’s attributes: builder, arguments, environment variables, output names, and the **store paths** of build-time dependencies. Same recipe and same input closure → same output paths on any machine. Change any declared input—source tree, dependency path, builder script, or env entry—and the hash changes and downstream paths change with it. The manual specifies the exact serialization and digest steps; at a high level, Nix hashes a canonical representation of the derivation together with its input store paths, then maps the digest into the path’s hash component.

### Path hash encoding

Store path hashes use **Nix base-32** (Nix32) encoding of a **20-byte** digest (160 bits). The human-readable name suffix (`hello-2.12`, etc.) is not part of the uniqueness guarantee; the encoded digest is. See the Nix manual [store path](https://nix.dev/manual/nix/stable/store/store-path.html) chapter for the path shape and digest mapping.

### What counts as an input

Only **declared** build inputs participate in input-addressed hashing. The builder runs in a [sandbox](builders-and-sandboxes.md) with a controlled view of the filesystem: paths listed as `src`, `buildInputs`, `nativeBuildInputs`, and similar attributes are visible; arbitrary host files outside that closure are not. Build-time environment variables are likewise limited to what the derivation records. Undeclared reads from the host therefore do not silently alter store path identity—though they can still break reproducibility if they affect the built bytes without changing declared inputs. That is why [hermetic builds](../01-philosophy/hermetic-builds.md) and declared inputs matter together.

### NAR hash (content of a store object)

A **Nix Archive (NAR)** is Nix’s canonical serialization of a filesystem object tree (files, directories, symlinks)—designed so the same tree always serializes the same way (no free-form timestamps or non-canonical directory order). The digest of that serialization is the **NAR hash** (`NarHash` in `.narinfo` / `narHash` in store object info). Binary caches use it to integrity-check substituted payloads; see [substitutes and NAR info](substitutes-and-narinfo.md) and the manual on [content-addressing file system objects](https://nix.dev/manual/nix/stable/store/file-system-object/content-address.html#serial-nix-archive).

NAR hashing is about **what the store object contains**. Input-addressing is about **how the path was named** before (or without) looking at those bytes. For FODs the two meet: the declared `outputHash` is a content digest of the output (often over a NAR).

### Fixed-output derivations

FODs declare `outputHash`, `outputHashAlgo`, and `outputHashMode`. Path computation for the output **ignores most derivation attributes** and keys off the declared hash (and name). The builder may fetch over the network; Nix verifies the output digest matches `outputHash` before accepting the path. Bit-identical content from different URLs yields the same store path; changed bytes require updating the declared hash.

`outputHashMode` selects how the output filesystem object is digested ([advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html)):

| Mode | Meaning |
|------|---------|
| `flat` | Hash raw file contents (single non-directory file); default for many simple fetches |
| `recursive` / `nar` | Hash the NAR serialization of the tree (`nar` is clearer; accepted since Nix **2.21**; `recursive` is the historic name) |
| `text`, `git` | Experimental digests (`dynamic-derivations` / `git-hashing`); not for ordinary packaging |

### Content-addressed outputs (sketch)

Nix already uses fixed content-addressing in production via FODs. **Floating** content-addressed derivations—where the output hash is computed from built content rather than predeclared—require the experimental `ca-derivations` feature. They remain sandboxed like ordinary builds; the difference is path assignment after a successful build. APIs and behavior in this area are not stabilized; see [content-addressed store](../02-concepts/content-addressed-store.md) and [ca-derivations](../08-experimental-features/ca-derivations.md).

### Derivation vs output paths

The `.drv` file itself lives at an input-addressed path derived from the derivation’s own hash. Output paths use related but distinct rules depending on output type (input-addressed, fixed-output, or experimental CA). Query tools such as `nix derivation show` and `nix-store --query --deriver` connect realized outputs back to their `.drv` and input graph.

## Examples

**Dependency bump, new path.** Package `B` depends on library `A`. Rebuilding `A` with a changed source produces a new store path for `A`; rebuilding `B` against that path yields a new path for `B` even if `B`’s own expression did not change—because `A`’s store path is an input to `B`’s hash.

**Same inputs, same path.** Two machines evaluate the same nixpkgs commit and build the same derivation with identical input closures. Both get the same output path; one may substitute from a binary cache while the other builds locally. Cache hits hinge on that shared identity plus matching NAR content when substituting.

**FOD: URL vs content.** A `fetchurl` FOD switches mirror URL but downloads the same tarball bytes. The output store path is unchanged because `outputHash` still matches. If upstream replaces the tarball, the FOD fails until `outputHash` is updated.

**Inspect NAR hash (local store).** On a machine with Nix and a realized path (`nix path-info` needs the `nix-command` experimental feature):

```bash
# Requires a local store path; prints narHash among other fields.
nix path-info --json /nix/store/…-hello-…
```

`narHash` is the digest of the NAR serialization used for substitution checks ([substitutes and NAR info](substitutes-and-narinfo.md)). Offline documentation cannot invent a specific digest; run the command against a path you have.

**Undeclared host state.** A builder reads `/etc/localtime` without declaring it as an input. That read does not change the input-addressed path hash; two builds with different host timezones could still share a path if declared inputs match—illustrating why sandboxing and declared inputs matter for reproducibility beyond path identity alone.

## References

- [Nix reference manual — derivations](https://nix.dev/manual/nix/stable/language/derivations.html) — derivation attributes and output path assignment
- [Nix reference manual — store paths](https://nix.dev/manual/nix/stable/store/store-path.html) — path shape and hash encoding
- [Nix reference manual — advanced attributes](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) — `outputHash*` / `outputHashMode`
- [Nix reference manual — content-addressing FSOs (NAR)](https://nix.dev/manual/nix/stable/store/file-system-object/content-address.html#serial-nix-archive)
- [Nix reference manual — store](https://nix.dev/manual/nix/stable/store/) — realization, substitution, and the store model

## See also

- [Substitutes and NAR info](substitutes-and-narinfo.md)
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md)
- [Builders and sandboxes](builders-and-sandboxes.md)
- [Hermetic builds](../01-philosophy/hermetic-builds.md)
- [Content-addressed store](../02-concepts/content-addressed-store.md)
- [ca-derivations](../08-experimental-features/ca-derivations.md)
