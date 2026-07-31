---
status: complete
---

# dynamic-derivations

## Overview

The **`dynamic-derivations`** experimental feature unlocks a narrow slice of **dynamic derivations** support in Nix: derivation outputs whose identity is not fully fixed at evaluation time, and dependencies on outputs that are themselves produced as derivation outputs. The manual describes the surface as limited—mainly **text-hashing** outputs for building `.drv` files, and dependencies on derivation outputs that are themselves derivation outputs.

**Version stamp:** As of the Nix **2.34.x** stable reference manual (`nix.dev/manual/nix/stable/` → 2.34; title 2.34.9), `dynamic-derivations` remains experimental and must be enabled explicitly (verified on Nix **2.34.8**: `builtins.outputOf` is present only with the flag). This is an advanced, research-oriented area—not a stable packaging API for most workflows. Enable it like other flags ([Feature Flags Overview](feature-flags-overview.md)); track stabilisation via [Tracking Stabilization](tracking-stabilization.md) and the [dynamic-derivations tracking issue](https://github.com/NixOS/nix/milestone/39).

## Details

**What the flag enables.** With `dynamic-derivations` on, Nix allows:

- **Text-hashing derivation outputs** — outputs whose store path is computed via text hashing, so a build can produce `.drv` files as outputs rather than only pre-known fixed paths. Related: `outputHashMode = "text"` in the floating CA / advanced-attributes model ([ca-derivations](ca-derivations.md)).
- **Dependencies on dynamic outputs** — a derivation may depend on the output of another derivation when that output is itself a derivation output (not only a statically known store path at eval time).
- **`builtins.outputOf`** — language access to deriving-path style output references. Given a derivation reference and an output name, it returns a concrete output path when statically known, or an **input placeholder** when the derivation is content-addressed or itself produced by another derivation. The primop can be nested (output-of-output). It corresponds to the `^` sigil in deriving-path / installable syntax.

The experimental-features page does not promise a full “derivations created at build time” product behind this single flag; treat the above as the documented scope for Nix 2.34.x. Deeper store-model notes live under [Store derivation / deriving path](https://nix.dev/manual/nix/2.34/store/derivation/) in the 2.34 manual.

**Experimental and evolving.** Like all [experimental features](feature-flags-overview.md), `dynamic-derivations` may change or be removed. Behavior, builtins, and CLI affordances can shift between releases—check [release notes](https://nix.dev/manual/nix/stable/release-notes/) when upgrading. For a related but distinct capability (builders invoking Nix during a build), see [recursive-nix](recursive-nix.md).

**Background concepts.** Static derivation structure, `.drv` files, and input addressing are covered in [Derivation](../02-concepts/derivation.md). How hashes and inputs feed store paths is in [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md).

## Examples

**Enable in `nix.conf`** (persistent opt-in; Nix 2.34.x):

```ini
extra-experimental-features = dynamic-derivations
```

**Append alongside other flags** without replacing an existing list:

```ini
experimental-features = nix-command flakes
extra-experimental-features = dynamic-derivations
```

**One-shot on the command line:**

```bash
nix --extra-experimental-features dynamic-derivations build .
```

**`builtins.outputOf` availability** (verified Nix 2.34.8):

```bash
# With the flag: primop is visible
nix-instantiate --extra-experimental-features dynamic-derivations --eval -E 'builtins.outputOf'
# => <PRIMOP>

# Without the flag:
# error: attribute 'outputOf' missing
```

Chaining shape from the builtins manual (needs real derivation references in a larger expression):

```nix
builtins.outputOf
  (builtins.outputOf myDrv "out")
  "out"
```

The experimental-features page itself does not ship a minimal end-to-end dynamic-derivation recipe; real use typically pairs this flag with upstream tracking and in-tree experiments rather than copy-paste packaging snippets.

## References

- [Nix manual — Experimental features (`dynamic-derivations`, 2.34)](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-dynamic-derivations) — version-stamped flag description
- [Nix manual — Built-ins (`outputOf`)](https://nix.dev/manual/nix/2.34/language/builtins.html#builtins-outputOf) — placeholder / deriving-path behaviour
- [Nix manual — Store derivation](https://nix.dev/manual/nix/2.34/store/derivation/) — deriving paths and dynamic-derivation model notes
- [Nix manual — nix.conf](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `experimental-features` and `extra-experimental-features`
- [dynamic-derivations tracking issue](https://github.com/NixOS/nix/milestone/39) — stabilisation milestone

## See also

- [Feature Flags Overview](feature-flags-overview.md) — how experimental features are enabled and lifecycle
- [Tracking Stabilization](tracking-stabilization.md) — which flags have stabilized or remain experimental
- [recursive-nix](recursive-nix.md) — builders calling Nix during a build (separate flag)
- [ca-derivations](ca-derivations.md) — floating CA; `outputHashMode = "text"` overlap
- [Derivation](../02-concepts/derivation.md) — static derivation model and `.drv` files
- [Hashing and inputs](../04-store-and-build/hashing-and-inputs.md) — how inputs determine store paths
