---
status: complete
---

# std / Paisano

## Overview

[Standard](https://github.com/divnix/std) (`divnix/std`) is a DivNix DevOps framework for organizing Nix flake projects around the software development lifecycle. Its folder importer and output typing come from **Paisano** (grow-family API; historically `divnix/paisano`, now maintained as [paisano-nix/core](https://github.com/paisano-nix/core)).

Where [flake-parts](../module-ecosystems/flake-parts.md) structures `outputs` with the module system, Standard/Paisano structures the *repository*: **cells** (domain folders), **cell blocks** (typed modules inside a cell), and **targets** (concrete packages, shells, images, …). A CLI/TUI and a JSON “registry” expose what you can *do* with those targets.

## Details

**Paisano vs Standard.** Paisano is the reusable importer: map `cellsFrom` into per-system flake fragments, attach **block types** (and optional **actions**), and emit a discoverable registry. Standard packages Paisano with a curated set of block types (installables, devshells, OCI/operables, nixago, …), dogfoods itself under `cells/`, and integrates vertical tools (numtide/devshell, treefmt, nix2container, and others).

**Cells and blocks.** Under `cellsFrom` (often `./nix`), each subdirectory is a **cell**. Inside a cell, only files (or directories with `default.nix`) whose names appear in `cellBlocks` are imported — e.g. `packages.nix` or `packages/default.nix`. Breadth is new blocks; depth across repos is composing flakes, not deeper nesting.

**Calling convention.** Every cell block is a function with a fixed interface:

```nix
{ inputs, cell }: {
  # targets for this block
}
```

`inputs` are de-systemized flake inputs (current `system` lifted) plus helpers such as `inputs.cells` and limited `self`/`sourceInfo` — not a free `self.packages…` graph. `cell` holds sibling blocks of the *current* cell so concerns stay local. That boundary is intentional: refactoring stays within typed paths instead of a spaghetti `self`.

**Grow and soil.** `std.growOn` / `paisano.growOn` grows the cell tree; the attrset after it is **soil** — compatibility with the Nix CLI or other frameworks. Typical helpers:

- `harvest` — lift a cell/block path into conventional flake attrs (`packages`, `devShells`, …)
- `winnow` / `pick` — filtered or non-system variants

Soil can also host [flake-parts](../module-ecosystems/flake-parts.md) or flake-utils patterns; Standard does not replace those APIs, it feeds them structured outputs.

**Typed layout.** Grown outputs follow roughly `${system}.${cell}.${block}.${target}`. Block types attach semantics and **actions** (build, push, …) surfaced under the registry (`__std` / Paisano registry schema; still versioned as unstable `v0` in Paisano docs). The `std` TUI (`nix run github:divnix/std` / project `std` entry) reads that registry so teammates can discover targets without memorizing fragments.

**NixOS configs.** Standard’s README steers Digga users toward [divnix/hive](https://github.com/divnix/hive) (cells/collectors on std/Paisano)—not Digga’s `mkFlake`. That Hive is a flake-layout tool; it is **not** Colmena’s deploy hive, Clan’s mesh VPN, or the [machine mesh](../../02-concepts/machine-mesh.md) concept. Digga itself is deprecated—see [Digga / Hive](digga-hive.md). For other layout frameworks, see [Snowfall](snowfall.md) and [Blueprint and others](blueprint-and-others.md).

## Examples

Minimal Standard sketch (from upstream getting-started shape):

```nix
# flake.nix
{
  description = "std / Paisano sketch";

  inputs = {
    std.url = "github:divnix/std";
    nixpkgs.follows = "std/nixpkgs";
  };

  outputs = { std, self, ... } @ inputs: std.growOn {
    inherit inputs;
    cellsFrom = ./nix;
    cellBlocks = with std.blockTypes; [
      (installables "packages" { ci.build = true; })
      (devshells "shells" { ci.build = true; })
    ];
  } {
    # Soil: Nix CLI–shaped outputs
    packages = std.harvest self [ "mycell" "packages" ];
    devShells = std.harvest self [ "mycell" "shells" ];
  };
}

# nix/mycell/packages.nix
{ inputs, cell }: {
  inherit (inputs.nixpkgs) hello;
  default = cell.packages.hello;
}
```

Explore a Standardized repo with the project TUI after `direnv allow` / `nix develop`, or `nix run github:divnix/std`. For Paisano alone (custom block types, no Standard block library), use `paisano.growOn` from `github:paisano-nix/core` (flake URL `github:divnix/paisano` still redirects there).

## See also

- [Digga / Hive](digga-hive.md)
- [Snowfall](snowfall.md)
- [Blueprint and others](blueprint-and-others.md)
- [flake-parts](../module-ecosystems/flake-parts.md)

## References

- Source / README: [divnix/std](https://github.com/divnix/std) — cells, `growOn`/`harvest`, Digga→Hive pointer (verified 2026-07)
- Documentation site: [std.divnix.com](https://std.divnix.com/) (canonical; may be intermittently unavailable — prefer GitHub when down)
- Paisano core: [paisano-nix/core](https://github.com/paisano-nix/core) (redirect from [divnix/paisano](https://github.com/divnix/paisano))
- Architecture notes: [ARCHITECTURE.md](https://github.com/divnix/std/blob/main/ARCHITECTURE.md)
- Related: [divnix/hive](https://github.com/divnix/hive) — host/module collectors on std (not Digga; not mesh)
- Community walkthrough (third-party book, linked from std README): [std-book](https://jmgilman.github.io/std-book/)
