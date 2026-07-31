---
status: index
---

# Core Concepts

Vocabulary and mental models used throughout the stack. Leaf articles in this domain are draft; pair with [01-philosophy](../01-philosophy/README.md) for Week 1 mental-model reading.

## Contents

- [Derivation](derivation.md) — Build recipe and store object
- [Store Path](store-path.md) — Hashed paths under the Nix store
- [Closure](closure.md) — Runtime dependency closure
- [Profile](profile.md) — User or system profile generations
- [Generation](generation.md) — Bootable or profile generation
- [Channel](channel.md) — Classic nixpkgs distribution mechanism
- [Flake (concept)](flake.md) — Pinned inputs and pure evaluation — deep dive in 07
- [Overlay](overlay.md) — Composable package-set modification
- [Overlay vs Override](overlay-vs-override.md) — When to use which
- [Fixed-Output Derivation](fixed-output-derivation.md) — FODs and output hashing
- [Import From Derivation](import-from-derivation.md) — Realise-during-eval (IFD)
- [Content-Addressed Store](content-addressed-store.md) — CA store model
- [Machine mesh](machine-mesh.md) — Multi-machine interconnect and inter-trust (concept)
