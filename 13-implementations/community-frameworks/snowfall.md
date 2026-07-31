---
status: complete
---

# Snowfall

## Overview

[Snowfall Lib](https://snowfall.org/guides/lib/quickstart/) (`snowfallorg/lib`) is an opinionated flake library for structuring NixOS, nix-darwin, and Home Manager configs. You call `snowfall-lib.mkFlake` (or `mkLib` then `lib.mkFlake`); the library scans a fixed directory layout and generates flake outputs — packages, overlays, modules, systems, homes, shells, and more — instead of hand-building a large `outputs` attrset.

Compared with [flake-parts](../module-ecosystems/flake-parts.md), Snowfall leans on **convention over configuration**: put files in the expected places and wire them through `mkFlake` options. The broader Snowfall project also ships CLI and tooling products; this page covers **Lib** only.

## Details

**Entry points.** Add the library as a flake input named exactly `snowfall-lib` (that name is required). Typical wiring:

```nix
outputs = inputs:
  inputs.snowfall-lib.mkFlake {
    inherit inputs;
    src = ./.; # flake root
  };
```

`mkFlake` is a convenience for `mkLib { … }` followed by `lib.mkFlake { }`. Pass `inherit inputs` and `src` (flake root). Optionally set `snowfall.root` to look for Snowfall-managed directories elsewhere (e.g. `./nix`) instead of cluttering the repo root.

**Namespace.** `snowfall.namespace` names your packages, library helpers, and overlay attrs. If unset, it defaults to `internal`. Managed files receive a `namespace` argument; local packages/helpers are reached as `pkgs.${namespace}.…` / `lib.${namespace}.…`.

**Directory layout (under the Snowfall root).** Lib expects directories such as:

| Path | Role |
| --- | --- |
| `packages/<name>/default.nix` | Packages (`callPackage`-style); exported on `packages` and via overlay |
| `modules/{nixos,darwin,home}/<name>/default.nix` | Platform modules; also exported as flake modules |
| `overlays/<name>/default.nix` | Custom overlays |
| `systems/<arch>-<format>/<host>/default.nix` | Host configs (e.g. `x86_64-linux/my-host`) |
| `homes/<arch>-<format>/<user>/default.nix` | Home Manager configs |
| `lib/` | Merged into the Snowfall `lib` (namespaced) |
| `shells/` | Dev shells |

`mkFlake` builds the corresponding flake outputs from that tree. Systems land on `nixosConfigurations`, `darwinConfigurations`, or generator-backed `*Configurations` depending on format.

**Integrations via inputs.** Add flake inputs when you need them; no extra Lib flags beyond that for basic enablement:

- `home-manager` — homes and HM-as-module on systems
- `darwin` — macOS / nix-darwin hosts
- `nixos-generators` — image/ISO-style formats under `systems/`

**Common `mkFlake` knobs.** Attach input overlays/modules with `overlays`, `systems.modules.nixos` / `darwin`, `systems.hosts.<name>.modules`, `homes.modules`, and per-home module lists. Map defaults with `alias` (e.g. `alias.packages.default = "my-package"`). For deeper helpers, use `mkLib` and the merged `lib` (nixpkgs.lib plus input libs under their input names).

**Fit.** Snowfall suits monorepo-style NixOS/HM flakes that want a prescribed tree. Prefer [flake-parts](../module-ecosystems/flake-parts.md) when you want module-composed flake options closer to the raw [flake schema](../../07-flakes/anatomy/flake-nix-schema.md). Other opinionated layouts: [Digga / Hive](digga-hive.md) (Digga deprecated; Hive ≠ Colmena hive / Clan mesh), [std / Paisano](std-paisano.md), [Blueprint and others](blueprint-and-others.md).

## Examples

Minimal flake using only `mkFlake` (official quickstart shape; pin nixpkgs to your channel—upstream docs may still show an older release):

```nix
{
  inputs = {
    # Prefer current stable (nixos-26.05 as of 2026-07); Snowfall quickstart still showed 24.05.
    nixpkgs.url = "github:nixos/nixpkgs/nixos-26.05";
    snowfall-lib = {
      url = "github:snowfallorg/lib";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs:
    inputs.snowfall-lib.mkFlake {
      inherit inputs;
      src = ./.;
      snowfall = {
        namespace = "my-namespace";
        # root = ./nix; # optional: move packages/, systems/, … here
        meta = {
          name = "my-awesome-flake";
          title = "My Awesome Flake";
        };
      };
    };
}
```

Then add e.g. `systems/x86_64-linux/my-host/default.nix` and `modules/nixos/my-module/default.nix`; Lib discovers them and wires outputs. Package files under `packages/<name>/default.nix` are callPackage-style functions receiving `lib`, `inputs`, `namespace`, and nixpkgs attrs.

## See also

- [flake-parts](../module-ecosystems/flake-parts.md)
- [Digga / Hive](digga-hive.md)
- [std / Paisano](std-paisano.md)
- [Blueprint and others](blueprint-and-others.md)
- [flake.nix schema](../../07-flakes/anatomy/flake-nix-schema.md)

## References

- [Snowfall](https://snowfall.org/) (project hub)
- [Snowfall Lib quickstart](https://snowfall.org/guides/lib/quickstart/) — `mkFlake`, `snowfall-lib` input name, layout (verified 2026-07)
- [Snowfall Lib reference](https://snowfall.org/reference/lib/)
- Guides: [packages](https://snowfall.org/guides/lib/packages/), [modules](https://snowfall.org/guides/lib/modules/), [systems](https://snowfall.org/guides/lib/systems/), [library](https://snowfall.org/guides/lib/library/)
- Source: [snowfallorg/lib](https://github.com/snowfallorg/lib)
