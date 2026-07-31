---
status: complete
---

# recursive-nix

## Overview

The **`recursive-nix`** experimental feature allows derivation builders to invoke Nix during a build, so a build script can recursively build other derivations. That breaks the usual separation between evaluation (which produces `.drv` files) and realisation (which runs builders), and is useful for advanced packaging patterns where the set of sub-builds depends on intermediate build results.

**Version stamp:** As of the Nix **2.34.x** stable reference manual (`nix.dev/manual/nix/stable/` → 2.34; title 2.34.9), `recursive-nix` remains experimental (manual example and substitution restriction unchanged relative to the flag entry; local Nix **2.34.8**). Behaviour and restrictions may change. Enable it explicitly ([Feature Flags Overview](feature-flags-overview.md)); track stabilisation in [Tracking Stabilization](tracking-stabilization.md) and the [recursive-nix tracking issue](https://github.com/NixOS/nix/milestone/47). For a related but distinct capability (derivation outputs whose identity is not fully fixed at eval time), see [dynamic-derivations](dynamic-derivations.md).

## Details

**What the flag enables.** With `recursive-nix` on, a builder may run `nix-build`, `nix build`, or similar inside the sandbox. The derivation should declare the need via `requiredSystemFeatures = [ "recursive-nix" ]` (optional but recommended—the 2.34 manual marks it as letting Nix know the build requires the feature / a builder that advertises it). The builder typically needs `nix` (and often `NIX_PATH` or flake inputs) in `buildInputs`.

**Substitution restrictions.** Recursive builders may not pull arbitrary store paths via substitution. For example, running `nix-store -r` on a path that is neither already in the derivation’s build inputs nor produced by an earlier recursive Nix call in the same build is **disallowed**. That prevents hidden dependencies and store-state-dependent builds that would break reproducibility. Paths already listed as inputs, or built earlier in the same recursive session, are permitted.

**Background concepts.** Static derivation structure and `.drv` files are in [Derivation](../02-concepts/derivation.md). How builders run inside sandboxes is in [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md). How substitution works—and why uncontrolled `-r` is risky—is in [Substitutes and narinfo](../04-store-and-build/substitutes-and-narinfo.md).

## Examples

**Enable in `nix.conf`** (Nix 2.34.x; still experimental):

```ini
extra-experimental-features = recursive-nix
```

On multi-user installs, the **daemon** (and any remote builders) must advertise / allow the feature for scheduled builds; client-only flags are not enough for realisation.

**Minimal recursive build** (from the Nix 2.34 experimental-features manual; requires `<nixpkgs>` on `NIX_PATH`):

```nix
with import <nixpkgs> {};

runCommand "foo"
  {
    # Optional: let Nix know "foo" requires the experimental feature
    requiredSystemFeatures = [ "recursive-nix" ];
    buildInputs = [ nix jq ];
    NIX_PATH = "nixpkgs=${<nixpkgs>}";
  }
  ''
    hello=$(nix-build -E '(import <nixpkgs> {}).hello.overrideDerivation (args: { name = "recursive-hello"; })')

    mkdir -p $out/bin
    ln -s $hello/bin/hello $out/bin/hello
  ''
```

The inner `nix-build` is allowed because it goes through Nix’s recursive-build machinery. Calling `nix-store -r /nix/store/…-hello-2.10` on a path not already in `buildInputs` or from a prior recursive call in this script would be rejected (manual’s concrete hash is illustrative).

## References

- [Nix manual — Experimental features (`recursive-nix`, 2.34)](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-recursive-nix) — version-stamped flag description, example, and substitution restriction
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `experimental-features` and `extra-experimental-features`
- [recursive-nix tracking issue](https://github.com/NixOS/nix/milestone/47) — stabilisation milestone

## See also

- [Feature Flags Overview](feature-flags-overview.md) — how experimental features are enabled and lifecycle
- [Tracking Stabilization](tracking-stabilization.md) — which flags have stabilized or remain experimental
- [dynamic-derivations](dynamic-derivations.md) — dynamic outputs and text-hashing (separate flag)
- [Derivation](../02-concepts/derivation.md) — static derivation model and `.drv` files
- [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md) — how builders execute
- [Substitutes and narinfo](../04-store-and-build/substitutes-and-narinfo.md) — substitution and why arbitrary `-r` is restricted
