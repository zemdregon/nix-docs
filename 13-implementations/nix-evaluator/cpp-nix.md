---
status: complete
last-checked: 2026-07
---

# CppNix

## Overview

**CppNix** is the common name for the official [NixOS/nix](https://github.com/NixOS/nix) implementation: the C++ Nix package manager that evaluates the Nix language, drives the store, and ships the CLI. It is the production default on NixOS and the reference point for “stock Nix” elsewhere—what most docs mean when they say simply “Nix.”

It owns the familiar surfaces: classic commands (`nix-build`, `nix-shell`, …), the newer `nix` CLI (including flakes when enabled), and the [experimental feature flags](../../08-experimental-features/feature-flags-overview.md) that gate unfinished or still-iterating behavior. Alternatives ([Lix](lix.md), [Tvix](tvix.md), [Snix](snix.md)) exist as forks or reimplementations; none replace CppNix as the NixOS-shipped baseline unless you deliberately switch.

**Maturity (last checked 2026-07-31):** production default / reference implementation. NixOS and most tutorials assume this tree; treat other evaluators as deliberate choices.

## Details

### What it is

| Aspect | CppNix |
|--------|--------|
| Upstream | [NixOS/nix](https://github.com/NixOS/nix) |
| Language | C++ |
| Role | Reference evaluator + store + CLI |
| NixOS | Default / shipped with the OS |
| Docs | [Nix reference manual](https://nix.dev/manual/nix/) |

“CppNix” is community shorthand to distinguish this tree from Lix, Tvix, and Snix. Upstream branding is still **Nix**. Glossary: [CppNix](../../glossary.md#cppnix).

### Experimental features and flakes

Since Nix 2.4, unstable capabilities are guarded by named **experimental feature** flags. Flakes and the modern `nix` command family are the most visible examples: they live behind flags until (or unless) stabilized for a given release. How flags work and how they relate to RFCs: [Feature flags overview](../../08-experimental-features/feature-flags-overview.md). Exact flag names and defaults change between releases—check the manual for the version you run. Stabilization tracks **Nix** releases, not NixOS `YY.MM` labels—see [tracking stabilization](../../08-experimental-features/tracking-stabilization.md) and [release cadence](../../15-history-and-governance/release-cadence.md).

### Vs other evaluators

| | Maturity / niche (high level; last checked 2026-07-31) |
|--|-------------------------------|
| **CppNix** | Production default; NixOS and most tutorials assume this |
| **[Lix](lix.md)** | Compatible fork of the C++ lineage; alternative daemon/CLI |
| **[Tvix](tvix.md)** | Independent Rust reimplementation (TVL); experimental / research |
| **[Snix](snix.md)** | Modular Rust continuation of the Tvix stack; early / research |

Governance and fork history: [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md). Treat maturity labels as a snapshot—verify before pinning production tooling to a non-default implementation.

### Versioning with NixOS / Nixpkgs

NixOS and Nixpkgs ship a pinned CppNix for each channel/release (stable vs rolling differ). The [Nix reference manual](https://nix.dev/manual/nix/) publishes versioned builds; match the manual to the Nix on your `PATH` when debugging flags or CLI behavior. The packaged Nix version is independent of the NixOS `YY.MM` channel name—see [release cadence](../../15-history-and-governance/release-cadence.md).

## Examples

Confirm which Nix binary you are running (CppNix vs a fork on `PATH`):

```bash
nix --version
which nix
```

Typical flake / new-CLI opt-in in `nix.conf` (flag names can change between releases—confirm in the manual for your version):

```ini
experimental-features = nix-command flakes
```

One-shot without editing config:

```bash
nix --extra-experimental-features 'nix-command flakes' flake show .
```

On NixOS, prefer declarative settings:

```nix
nix.settings.experimental-features = [ "nix-command" "flakes" ];
```

## See also

- [Lix](lix.md) — C++-lineage fork
- [Tvix](tvix.md) — independent Rust reimplementation (TVL)
- [Snix](snix.md) — modular Rust continuation of Tvix
- [Nix Evaluators](README.md) — evaluator index
- [Glossary](../../glossary.md#cppnix) — CppNix / Lix / Tvix / Snix term index
- [Feature flags overview](../../08-experimental-features/feature-flags-overview.md) — experimental feature gating
- [Tracking stabilization](../../08-experimental-features/tracking-stabilization.md) — how Nix flags land across Nix releases
- [Release cadence](../../15-history-and-governance/release-cadence.md) — NixOS YY.MM vs Nix versioning
- [Forks and governance splits](../../15-history-and-governance/forks-and-governance-splits.md) — history of splits

## References

- [NixOS/nix](https://github.com/NixOS/nix) — official C++ Nix source
- [Nix reference manual](https://nix.dev/manual/nix/) — CLI, config, experimental features (versioned)
- [Download Nix / NixOS](https://nixos.org/download/) — current packaged Nix and NixOS stable labels
