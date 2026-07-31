---
status: complete
---

# flake-parts

## Overview

[flake-parts](https://flake.parts/) is a small library that evaluates `flake.nix` **outputs** with the Nix module system. Instead of building a large attrset by hand, you call `flake-parts.lib.mkFlake { inherit inputs; } { … }` and declare flake attributes as **options** (`systems`, `perSystem`, `flake`, …), optionally split across `imports`.

The design stays close to the [flake schema](../../07-flakes/anatomy/flake-nix-schema.md): opinionated layout comes from importable modules in the ecosystem, not from a fixed monorepo convention. Flakes and the modern `nix` CLI remain **experimental** (Nix `flakes` + `nix-command`); flake-parts assumes both. It shares the module-system motivation with NixOS and [Home Manager](home-manager.md), but targets flake outputs rather than host or user configuration.

## Details

**`mkFlake`.** Add `flake-parts` as an input, then wrap the body of `outputs`:

```nix
outputs = inputs@{ flake-parts, ... }:
  flake-parts.lib.mkFlake { inherit inputs; } {
    # module body
  };
```

The second argument is a module — an attrset, a function returning one, or a path. Definitions merge the same way as in the [module system](../../09-nixos/architecture/module-system.md).

**Systems and `perSystem`.** List target platforms under `systems`. Put packages, apps, checks, and `devShells` under `perSystem`; flake-parts expands them to the conventional `packages.<system>.…` layout (see [Packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md)).

**Named arguments (pitfall).** Module functions only receive **explicitly named** parameters — flake-parts uses `builtins.functionArgs` to decide what to pass. `perSystem = args: { … }` does **not** get `pkgs` unless you name it: `perSystem = { pkgs, ... }: { … }`. The same rule applies to `flake`, `imports`, and other module functions.

**`self'` and `inputs'`.** Inside `perSystem`, these are system-preselected views of `self` and `inputs` (e.g. `inputs'.nixpkgs` is already fixed to the current `system`). Name them when you need cross-system wiring without repeating `system` in every lookup.

**`flake` and other attrs.** System-independent outputs — `nixosModules`, `overlays`, `nixosConfigurations`, and similar — go under `flake` or other top-level options flake-parts declares. You can still set almost anything; some attributes have dedicated options for merging.

**Wiring hosts to packages.** Top-level helpers `withSystem`, `moduleWithSystem`, and `getSystem` connect `nixosConfigurations` to `perSystem` packages (for example, referencing a built package from a NixOS module). See [module arguments](https://flake.parts/module-arguments) in the upstream docs.

**`imports`.** Split logic into files or reuse modules from other flakes (often exposed as `flakeModules.default`). Local paths and attrsets both work — the main scaling story for large flakes.

**Compared to other frameworks.** [Snowfall](../community-frameworks/snowfall.md) enforces a directory layout and more defaults; flake-parts stays closer to raw flake outputs. [Digga / Hive](../community-frameworks/digga-hive.md) (divnix) is a separate, largely deprecated collector stack — not the [machine mesh](../../02-concepts/machine-mesh.md) concept and not a drop-in substitute for flake-parts.

## Examples

Minimal sketch: one system, a default package from `pkgs`:

```nix
{
  description = "Tiny flake-parts example";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        # ./modules/dev.nix
        # inputs.someLib.flakeModules.default
      ];
      systems = [ "x86_64-linux" ];
      perSystem = { pkgs, self', ... }: {
        packages.default = pkgs.hello;
        # self'.packages.default is the same derivation for this system
      };
    };
}
```

Scaffold a new project with the official template: `nix flake init -t github:hercules-ci/flake-parts`.

## References

- [flake-parts documentation](https://flake.parts/) — `mkFlake`, options, ecosystem (verified 2026-07)
- [Getting started (`mkFlake`, `imports`, `perSystem`)](https://flake.parts/getting-started)
- [Module arguments](https://flake.parts/module-arguments) — named args, `self'`, `inputs'`, `withSystem`
- Source: [hercules-ci/flake-parts](https://github.com/hercules-ci/flake-parts)

## See also

- [flake.nix schema](../../07-flakes/anatomy/flake-nix-schema.md)
- [Packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md)
- [Module system](../../09-nixos/architecture/module-system.md)
- [Home Manager](home-manager.md)
- [Snowfall](../community-frameworks/snowfall.md)
- [Digga / Hive](../community-frameworks/digga-hive.md)
