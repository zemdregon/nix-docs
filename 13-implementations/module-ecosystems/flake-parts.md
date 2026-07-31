---
status: complete
---

# flake-parts

## Overview

[flake-parts](https://flake.parts/) is a small library that evaluates `flake.nix` **outputs** with the Nix module system. Instead of building a large attrset by hand, you call `flake-parts.lib.mkFlake` and declare flake attributes as **options** (`systems`, `perSystem`, `flake`, …), optionally split across `imports`.

The core aims to mirror the [flake schema](../../07-flakes/anatomy/flake-nix-schema.md) lightly; opinionated features come from an ecosystem of importable modules. It complements raw flake outputs and is a common choice when a flake grows large enough that one monolithic `outputs` function becomes hard to maintain. Flakes and the modern `nix` CLI remain **experimental** (Nix `flakes` + `nix-command`); flake-parts assumes those features.

## Details

**`mkFlake`.** Add `flake-parts` as an input, then wrap the body of `outputs`:

```nix
outputs = inputs@{ flake-parts, ... }:
  flake-parts.lib.mkFlake { inherit inputs; } {
    # module body
  };
```

`mkFlake` takes `{ inherit inputs; }` (and optional extra args) plus a module — an attrset, a function returning one, or a path. The module system merges definitions the same way NixOS and [Home Manager](home-manager.md) do.

**Systems and `perSystem`.** List target platforms under `systems`. Put packages, apps, checks, and `devShells` under `perSystem` so flake-parts expands them to the conventional `packages.<system>.…` layout (see [Packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md)). Inside `perSystem`, name arguments you need (`pkgs`, `system`, `self'`, `inputs'`, …); only explicitly named parameters are passed.

**`flake` and other attrs.** System-independent outputs (`nixosModules`, `overlays`, `nixosConfigurations`, …) go under `flake` (or other top-level options flake-parts declares). You can still set almost anything; some attributes have dedicated options for merging.

**`imports`.** Split logic into files or reuse modules from other flakes (often exposed as `flakeModules.default`). Local paths and attrsets both work. That is the main scaling story: focused units instead of one giant `flake.nix`.

**Why modules.** Flakes are configuration. The module system gives mergeable options, `mkIf`/`mkMerge`, and shareable flake modules — similar motivation to NixOS, but flake-parts stays a thin compatibility layer rather than a monorepo of all project logic. Frameworks such as [Snowfall](../community-frameworks/snowfall.md) take a more opinionated layout; flake-parts stays closer to the raw schema.

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
      perSystem = { pkgs, ... }: {
        packages.default = pkgs.hello;
      };
    };
}
```

Scaffold a new project with the official template: `nix flake init -t github:hercules-ci/flake-parts`.

## See also

- [flake.nix schema](../../07-flakes/anatomy/flake-nix-schema.md)
- [Packages, apps, and devShells](../../07-flakes/workflows/packages-apps-devShells.md)
- [Home Manager](home-manager.md)
- [Snowfall](../community-frameworks/snowfall.md)

## References

- [flake-parts documentation](https://flake.parts/) — `mkFlake`, options, ecosystem (verified 2026-07)
- [Getting started (`mkFlake`, `imports`, `perSystem`)](https://flake.parts/getting-started)
- [Module arguments](https://flake.parts/module-arguments)
- Source: [hercules-ci/flake-parts](https://github.com/hercules-ci/flake-parts)
