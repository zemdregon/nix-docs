---
status: complete
last-checked: 2026-07
---

# ca-derivations

## Overview

The **`ca-derivations`** experimental feature enables **floating content-addressed derivations**: store paths keyed to built output content rather than to the full input-addressed recipe. When a derivation’s declared inputs change but the builder still produces identical bytes, the output can map to the **same** store path—avoiding unnecessary rebuilds and cache churn downstream.

This is the experimental counterpart to the stabilized fixed content-addressing already used by [fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs). For the store-level model and fixed-vs-floating distinction, see [Content-Addressed Store](../02-concepts/content-addressed-store.md).

**Version stamp:** As of the Nix **2.34.x** stable reference manual (`nix.dev/manual/nix/stable/` → 2.34), `ca-derivations` remains experimental and must be enabled explicitly. Experimental feature *flags* have existed since **Nix 2.4**. Stabilisation is tracked on the [ca-derivations tracking issue](https://github.com/NixOS/nix/milestone/35).

## Details

**What the flag unlocks.** With `ca-derivations` enabled, a derivation may set `__contentAddressed = true` together with `outputHashAlgo` and `outputHashMode`, and **without** `outputHash`. Nix builds in the sandbox like an ordinary derivation, then assigns the output path from the content address of the built files. Identical output data can share a path even when non-CA parts of the derivation description would differ—the manual’s motivation is avoiding mass rebuilds when, for example, a fetch URL changes but the downloaded content does not.

**Input-addressed default.** Ordinary [derivations](../02-concepts/derivation.md) are input-addressed: output paths reflect the derivation attributes and input store paths. Any declared input change yields new paths for that output and its dependents, even if the rebuilt artifact bytes were unchanged. [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md) summarizes how input addressing differs from content addressing in the store.

**Fixed vs floating.** **Fixed-output** content addressing (FODs) predeclares `outputHash` and may grant the builder network access with verification. **Floating** content addressing (`__contentAddressed = true`, no `outputHash`) computes the path after a successful sandboxed build. Floating CA does not by itself grant impure capabilities; the experimental split is path assignment policy, not a blanket network exception. (The content-addressing chapter notes provisional interaction with [impure-derivations](impure-derivations.md) for impure *builders*; a derivation marked `__impure = true` still cannot also be content-addressed.)

**Attribute combinations (manual).** The three derivation kinds are chosen only from these combinations; all others are invalid:

| Kind | Attributes |
|------|------------|
| Input-addressed | Default (`builtins.derivation`); optional `__contentAddressed = false` still triggers the experimental-feature check |
| Fixed-output | `outputHash`, `outputHashAlgo`, and `outputHashMode` |
| Floating CA | `__contentAddressed = true`, `outputHashAlgo`, `outputHashMode`, and **not** `outputHash` |

**`outputHashMode` values** (for CA outputs): `"flat"` (default), `"recursive"` or `"nar"` (same method; **`"nar"` requires Nix ≥ 2.21**), `"text"` ([dynamic-derivations](dynamic-derivations.md)), `"git"` ([git-hashing](fetch-tree-and-git.md)).

**Enabling the feature.** Add the flag in [nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) or pass it per invocation—same mechanisms as other experimental features ([Feature Flags Overview](feature-flags-overview.md)):

```ini
extra-experimental-features = ca-derivations
```

On multi-user installs the **daemon** must also have the flag (and typically a restart after changing `/etc/nix/nix.conf`), because floating CA affects store/database behaviour—not only client evaluation.

**Builder scheduling.** Any derivation producing a floating CA output implicitly requires the `ca-derivations` **system feature** on builders (`system-features` / `requiredSystemFeatures`). Remote builders without that feature will not schedule those builds—useful even after stabilisation for older or alternate Nix implementations.

**Not stabilized.** Attribute names, scheduling rules, and interaction with substitution may change. Do not rely on floating CA semantics in production tooling without pinning Nix versions and following upstream tracking.

## Examples

**Enable in configuration** (Nix 2.34.x; still experimental):

```ini
extra-experimental-features = ca-derivations
```

**Floating CA attributes** (shape from the advanced-attributes / content-addressing chapters; instantiate-checked on Nix 2.34 with `ca-derivations`—outputs show `method = "nar"` and no fixed hash):

```nix
derivation {
  name = "example-ca";
  system = builtins.currentSystem;
  builder = /bin/sh;
  args = [ "-c" "echo hello-ca > $out" ];
  __contentAddressed = true;
  outputHashMode = "nar"; # alias of "recursive"; "nar" since Nix 2.21
  outputHashAlgo = "sha256";
  # no outputHash — path is assigned from built content
}
```

**Contrast.** A normal `stdenv.mkDerivation` without CA attributes produces input-addressed outputs: bump a dependency’s store path and dependents get new paths even when their rebuilt bytes match the previous generation.

## References

- [Nix manual — Experimental features: ca-derivations](https://nix.dev/manual/nix/stable/development/experimental-features.html#xp-feature-ca-derivations) — flag purpose; stable manual as of Nix 2.34.x
- [Nix manual — Advanced attributes: `__contentAddressed`](https://nix.dev/manual/nix/stable/language/advanced-attributes.html#adv-attr-__contentAddressed) — derivation kinds and attribute combinations
- [Nix manual — Content-addressing derivation outputs](https://nix.dev/manual/nix/stable/store/derivation/outputs/content-address.html) — fixed vs floating CA, purity, system features
- [ca-derivations tracking issue](https://github.com/NixOS/nix/milestone/35) — stabilisation milestone

## See also

- [Feature Flags Overview](feature-flags-overview.md) — enabling experimental features
- [Tracking Stabilization](tracking-stabilization.md) — stabilization status in this wiki
- [impure-derivations](impure-derivations.md) — `__impure` incompatible with content-addressed derivations
- [Content-Addressed Store](../02-concepts/content-addressed-store.md) — store-level CA model
- [Derivation](../02-concepts/derivation.md) — build recipes and output types
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) — stabilized fixed content-addressing
- [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md) — input-addressed vs content-addressed paths
- [Reproducible builds audit](../14-security-and-trust/reproducible-builds-audit.md) — verifying bit-identical outputs vs input-addressed identity
