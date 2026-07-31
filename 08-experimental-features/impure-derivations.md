---
status: complete
---

# impure-derivations

## Overview

The **`impure-derivations`** experimental feature lets a [derivation](../02-concepts/derivation.md) produce **non-fixed outputs**: each build may write different bytes to its store paths. Set `__impure = true` on the derivation to mark it impure. That is an explicit, build-time alternative to impure evaluation helpers such as `builtins.currentTime`.

**Version stamp:** As of the Nix **2.34.x** stable reference manual (`nix.dev/manual/nix/stable/` → 2.34; title 2.34.9), `impure-derivations` remains experimental (verified on Nix **2.34.8**). Impure derivations relax the usual sandbox contract—builders get **network access**, and outputs are not pinned by a predeclared hash. Only [fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs) or other impure derivations may depend on an impure derivation’s outputs. An impure derivation **cannot** also be content-addressed. Enable explicitly and track progress via [Tracking Stabilization](tracking-stabilization.md) and the [impure-derivations tracking issue](https://github.com/NixOS/nix/milestone/42).

## Details

**What the flag unlocks.** With `impure-derivations` enabled, a derivation may set `__impure = true`. Nix treats the derivation as producing **variable output**—the built files may differ each time the derivation runs. This is the opposite of an FOD, where `outputHash` fixes the expected content before the build runs.

**Network and sandbox.** Impure derivations have **network access** during the build. Ordinary input-addressed derivations stay sandboxed and cannot fetch arbitrary remote data at build time unless they use an FOD or depend on an impure derivation that performed the impure step.

**Who may depend on impure outputs.** Downstream derivations that consume an impure output must themselves be either a **fixed-output derivation** (verifying content against `outputHash`) or another **impure derivation**. Normal derivations cannot rely on impure outputs—this keeps the bulk of the dependency graph reproducible while allowing controlled escape hatches.

**Incompatible with content-addressed derivations.** A derivation marked `__impure = true` cannot also be content-addressed (`__contentAddressed = true`). See [ca-derivations](ca-derivations.md) for the floating content-addressed model and this mutual exclusion.

**Relation to evaluation purity.** Impure derivations affect **build-time** behavior in the store, not Nix language evaluation rules alone. For where evaluation may touch the filesystem, environment, or time, see [Purity boundaries](../03-language/semantics/purity-boundaries.md). For how builders run inside sandboxes by default, see [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md).

**Enabling the feature.** Add the flag in [nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) or pass it per invocation—same mechanisms as other experimental features ([Feature Flags Overview](feature-flags-overview.md)):

```ini
extra-experimental-features = impure-derivations
```

On multi-user installs the **daemon** must also have the flag (and typically a restart after changing `/etc/nix/nix.conf`) for realisation: client-only `--extra-experimental-features` is enough for some eval checks, but `nix-instantiate` / builds that talk to the daemon will still report the feature disabled if the daemon lacks it (observed on Nix 2.34.8).

**Not stabilized.** Attribute semantics, scheduling, and interaction with substitution may change. Do not rely on impure derivation behavior in production tooling without pinning Nix versions and following upstream tracking.

## Examples

**Enable in configuration** (Nix 2.34.x; still experimental):

```ini
extra-experimental-features = impure-derivations
```

**Manual example — random bytes to `$out`:** each build can produce different output (from the Nix 2.34 experimental-features manual):

```nix
derivation {
  name = "impure";
  builder = /bin/sh;
  __impure = true; # mark this derivation as impure
  args = [ "-c" "read -n 10 random < /dev/random; echo $random > $out" ];
  system = builtins.currentSystem;
}
```

With the flag enabled for evaluation (`nix-instantiate --option experimental-features impure-derivations --eval -E '…'`), Nix 2.34.8 accepts `__impure = true` and returns a derivation attrset. Each time this derivation is **built**, the builder reads from `/dev/random` and writes ten random bytes to `$out`, so the output content varies between builds.

**Without the flag** (Nix 2.34.8):

```text
error: experimental Nix feature 'impure-derivations' is disabled; add '--extra-experimental-features impure-derivations' to enable it
```

**Contrast with `builtins.currentTime`.** Using `builtins.currentTime` during evaluation embeds the current time into the evaluated expression (and thus into input-addressed paths derived from it). An impure derivation instead performs the non-deterministic work **inside the builder** under an explicitly marked derivation—making the impurity visible in the `.drv` graph rather than hiding it in pure-looking Nix code.

## References

- [Nix manual — Experimental features: impure-derivations (2.34)](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-impure-derivations) — flag purpose, random-output example, dependency rules
- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — how experimental flags work and the full flag list
- [impure-derivations tracking issue](https://github.com/NixOS/nix/milestone/42) — stabilisation milestone

## See also

- [Feature Flags Overview](feature-flags-overview.md) — enabling experimental features
- [Tracking Stabilization](tracking-stabilization.md) — stabilization status in this wiki
- [ca-derivations](ca-derivations.md) — content-addressed derivations; incompatible with `__impure`
- [Derivation](../02-concepts/derivation.md) — build recipes and output types
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md) — hash-pinned outputs and network fetches
- [Purity boundaries](../03-language/semantics/purity-boundaries.md) — evaluation-time purity vs impure builtins
- [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md) — default sandbox behavior for ordinary builds
