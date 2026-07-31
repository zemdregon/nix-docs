---
status: complete
---

# Blueprint and Others

## Overview

[Blueprint](https://github.com/numtide/blueprint) (Numtide) is an opinionated flake library that maps a **standard folder layout** onto flake outputs. Drop files under `packages/`, `hosts/`, `modules/`, `devshells/`, and similar directories; Blueprint wires them to `packages.*`, `nixosConfigurations.*` / `darwinConfigurations.*`, `nixosModules.*`, `devShells.*`, and related attrs. The design goal is to cut glue code so `flake.nix` stays thin—closer to Rails-style convention than to a free-form outputs function.

Blueprint is one of several **community scaffolds** (upstream marks it **experimental** as of 2026-07). They share a problem (noisy flakes, ad-hoc repo layout) but differ in mechanism. [flake-parts](../module-ecosystems/flake-parts.md) evaluates outputs through the Nix module system. Blueprint and peers such as [Snowfall](snowfall.md), [Digga / Hive](digga-hive.md), and [std / Paisano](std-paisano.md) prefer fixed directory or cell conventions. Numtide positions Blueprint as a spiritual successor to [flake-utils](https://github.com/numtide/flake-utils): keep mapping predictable (KISS, 1:1 paths → attrs), avoid deep module recursion, and break out when the project outgrows the scaffold.

## Details

### Blueprint mechanism

Add Blueprint as an input and hand `outputs` to it:

```nix
outputs = inputs: inputs.blueprint { inherit inputs; };
```

Optional `prefix` (often `"nix/"`) nests the scanned tree under a subdirectory so Nix folders stay separate from application sources. Root special files such as `devshell.nix`, `package.nix`, and `formatter.nix` cover defaults; named entries live under the conventional directories (`packages/foo/default.nix` → `packages.<system>.foo`, and so on). Supported surfaces include NixOS, nix-darwin, Home Manager, system-manager, nix-unit, RFC 166 formatting via `nix fmt`, overridable systems via [nix-systems](https://github.com/nix-systems), and automatic flake checks derived from packages, devshells, and NixOS configurations.

Upstream is explicit that Blueprint is **not** aimed at highly complex flakes: once conventions fight the problem, leave the scaffold and compose outputs yourself (or switch to a module-based approach).

### Map: community frameworks vs flake-parts

| Approach | How structure is expressed | Typical fit |
|----------|----------------------------|-------------|
| **Blueprint** | Fixed folders/files → flake attrs | Small–medium repos; want almost no `outputs` boilerplate |
| **[flake-parts](../module-ecosystems/flake-parts.md)** | NixOS-style modules (`imports`, `perSystem`, options) | Growing flakes; shareable `flakeModules`; flexible schema |
| **[Snowfall](snowfall.md)** | Opinionated lib + directory conventions (Snowfall Org) | Homogeneous multi-host / multi-package trees in that ecosystem |
| **[Digga / Hive](digga-hive.md)** | Digga (deprecated) / divnix Hive collectors | Digga→Hive handoff; **not** Colmena hive or Clan mesh |
| **[std / Paisano](std-paisano.md)** | Cells/blocks (divnix Standard / Paisano) | Structured monorepos with std’s cell model |
| **clan-core** (related) | Broader deployment/product stack | Machines/deploy (+ Clan mesh VPN)—not a thin folder mapper |

Rule of thumb: choose **folder/convention scaffolds** (Blueprint, Snowfall, std, …) when the team wants one obvious layout and low ceremony; choose **flake-parts** when you need mergeable options, reusable flake modules, and a closer fit to the raw flake schema without a mandatory directory tree.

## Examples

Scaffold a new project:

```bash
mkdir my-project && cd my-project
nix flake init -t github:numtide/blueprint
```

Minimal `flake.nix` after init (inputs aside, outputs stay one call):

```nix
{
  description = "Simple flake with a devshell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-unstable";
    blueprint.url = "github:numtide/blueprint";
    blueprint.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs: inputs.blueprint { inherit inputs; };
}
```

With a `nix/` prefix and a package folder `nix/packages/hello/default.nix`, build with `nix build .#hello`. Default developer env lives in root `devshell.nix` (or under `devshells/` for multiple shells)—`nix develop` without stuffing a `devShells` attr into `flake.nix` by hand.

## See also

- [Snowfall](snowfall.md)
- [Digga / Hive](digga-hive.md)
- [std / Paisano](std-paisano.md)
- [flake-parts](../module-ecosystems/flake-parts.md)
- [Community frameworks](README.md)

## References

- Source / README: [numtide/blueprint](https://github.com/numtide/blueprint) — folder→output map, experimental badge (verified 2026-07)
- Documentation: [numtide.github.io/blueprint](https://numtide.github.io/blueprint/main/)
- Install / template walkthrough: [Installing Blueprint](https://numtide.github.io/blueprint/main/getting-started/install/)
- Related (Numtide lineage): [numtide/flake-utils](https://github.com/numtide/flake-utils)
- Related (deployment stack mentioned upstream): [clan-core](https://git.clan.lol/clan/clan-core)
