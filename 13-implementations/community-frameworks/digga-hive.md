---
status: complete
---

# Digga / Hive

## Overview

**Digga** and **Hive** (divnix) are **flake layout / collector** tools for organizing hosts and module-system apps in a repo. They are **not** a network mesh, not Clan’s mesh VPN, and not Colmena’s deploy “hive.” See [Name collisions](#name-collisions) below.

**Digga** ([divnix/digga](https://github.com/divnix/digga)) was a flake utility library for shell, Home Manager, and NixOS hosts in one repository (DevOS lineage; built on [flake-utils-plus](https://github.com/gytis-ivaskevicius/flake-utils-plus)). As of mid-2023 maintainers marked it **deprecated and unmaintained**. Verified 2026-07: the GitHub repo is **not archived** (`archived: false`), but the README forbids new use.

**Hive** ([divnix/hive](https://github.com/divnix/hive)) is a separate divnix project for “module system applications” (NixOS, nix-darwin, Home Manager, …). It is not a Digga rewrite. It sits on [std / Paisano](std-paisano.md) (cells, block types) and collects configs for upstream tools rather than Digga’s monolithic `mkFlake` API. Docs are intentionally thin.

For greenfield flakes, prefer [flake-parts](../module-ecosystems/flake-parts.md), [Snowfall](snowfall.md), or [Blueprint and others](blueprint-and-others.md)—not Digga.

## Details

### Name collisions

| Name | What it is | Wiki |
|------|------------|------|
| Digga / **Hive** (this page) | Flake organization / std collectors for hosts and modules | Here |
| Colmena **hive** | Attrset of deployable NixOS nodes for hub → hosts SSH deploy | [Colmena](../../12-deployment-and-infra/colmena.md) |
| Clan **mesh** | Overlay/VPN and peer networking among inventory machines | [Clan and mesh](../../12-deployment-and-infra/clan-and-mesh.md) |
| **Machine mesh** (concept) | Interconnected Nix devices + inter-trust axes—not a flake layout name | [Machine mesh](../../02-concepts/machine-mesh.md) |

Hive collectors may *feed* a Colmena hive; that wiring does not make Digga/Hive a mesh or Colmena’s hive the same project.

### Digga (legacy)

Public surface centered on `lib.mkFlake`: channels/overlays, NixOS hosts, Home Manager users, and [devshell](https://github.com/numtide/devshell) setups. Layout vocabulary:

- **Modules** — reusable options/implementation without fixing system state
- **Profiles** — concrete settings in a domain
- **Suites** — aggregations of profiles

Maintainers later called that surface hard to keep correct; see [Ending digga (#503)](https://github.com/divnix/digga/issues/503) (2023). Suggested exits: **flake-parts**, **std**, raw `nixosSystem` / deploy tooling—no single successor.

| Fact | Digga (as of 2026-07) |
|------|------------------------|
| Org / repo | `divnix/digga` |
| GitHub archived? | **No** |
| Maintainer stance | Deprecated; “not recommended for any sort of use case” (README) |
| Last push (API) | 2024-05-17 |
| Handoff | Offered in #503; no active steward assumed |

### Hive (related, different model)

Same *problem space* (hosts / module-based systems), different shape: Paisano/std cells, [haumea](https://github.com/nix-community/haumea) loading, collectors such as `hive.collect` that can feed [Colmena](../../12-deployment-and-infra/colmena.md). Modules / profiles / suites appear as **block types**, not Digga’s exporter.

Verified 2026-07: `divnix/hive` is also **not** GitHub-archived; commits appear occasionally. README points at source and Matrix (`#hive-std-nix:matrix.org`), not a full manual. Niche std-adjacent kit—not “the Digga rewrite.”

## Examples

Historical Digga flake inspection only—do not start new configs from Digga templates:

```text
# Historical only — Digga is deprecated (repo not archived)
nix flake show github:divnix/digga
# Template / examples lived under examples/devos in that repo
```

Typical Digga exit path (sketch; not Digga-specific):

```nix
# flake-parts + explicit nixosConfigurations
outputs = inputs@{ flake-parts, nixpkgs, ... }:
  flake-parts.lib.mkFlake { inherit inputs; } {
    systems = [ "x86_64-linux" ];
    flake.nixosConfigurations.example = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [ ./hosts/example ];
    };
  };
```

For Hive, read community flakes that wire `divnix/hive` with std (e.g. configs linked from Digga #503), not a Digga-style guide.

## See also

- [Machine mesh](../../02-concepts/machine-mesh.md) — interconnect / trust concept; not this Hive
- [Clan and mesh](../../12-deployment-and-infra/clan-and-mesh.md) — Clan mesh VPN vs hive naming
- [Colmena](../../12-deployment-and-infra/colmena.md) — deploy hive attrset; different “Hive”
- [std / Paisano](std-paisano.md)
- [flake-parts](../module-ecosystems/flake-parts.md)
- [Snowfall](snowfall.md)
- [Blueprint and others](blueprint-and-others.md)

## References

- [divnix/digga](https://github.com/divnix/digga) — source; README deprecation; **not** GitHub-archived (verified 2026-07)
- [Ending digga (#503)](https://github.com/divnix/digga/issues/503) — deprecation rationale and alternatives
- Digga site (historical): [digga.divnix.com](https://digga.divnix.com)
- [divnix/hive](https://github.com/divnix/hive) — Hive source; not Digga; not archived (verified 2026-07)
- Related stack: [divnix/std](https://github.com/divnix/std), [paisano-nix/core](https://github.com/paisano-nix/core)
