---
status: complete
---

# homeConfigurations

## Overview

**`homeConfigurations.<name>`** is the flake output that exposes a standalone [Home Manager](../../10-home-and-user/README.md) user environment. Each name (commonly the login username, for example `jdoe`) maps to the result of `home-manager.lib.homeManagerConfiguration`, which evaluates Home Manager modules and produces an activation script for that user’s home directory.

This page covers **flake wiring** for Home Manager—inputs, output keys, and how you apply or rebuild. Choosing between standalone, NixOS-embedded, or nix-darwin-embedded setups, and writing Home Manager modules themselves, belong in [Home and user environments](../../10-home-and-user/README.md); see [Inputs and outputs](../anatomy/inputs-and-outputs.md) for how `homeConfigurations` fits the general output schema.

Home Manager’s flake integration is **experimental** and may change in backwards-incompatible ways; pin inputs and read upstream release notes when upgrading. Match the Home Manager release branch to your Nixpkgs/NixOS release (examples below use **release-26.05** / **nixos-26.05** as of mid-2026).

## Details

**Three integration modes.** The Home Manager manual describes the same three paths as non-flake installs:

1. **Standalone** — declare `homeConfigurations` in your flake and activate with the `home-manager` CLI. Required on non-NixOS/non-Darwin platforms; also common when user dotfiles should evolve independently of system configuration.
2. **NixOS module** — import `home-manager.nixosModules.home-manager` inside a [nixosConfigurations](nixos-configurations.md) module list; user profiles rebuild with `nixos-rebuild`.
3. **nix-darwin module** — import `home-manager.darwinModules.home-manager` inside `darwinConfigurations`; profiles rebuild with `darwin-rebuild`.

Only the standalone path uses the `homeConfigurations` output key directly. The module paths wire Home Manager through system flakes instead.

**Defining a standalone configuration.** The conventional form is:

```nix
homeConfigurations.jdoe = home-manager.lib.homeManagerConfiguration {
  pkgs = nixpkgs.legacyPackages.x86_64-linux; # match your system
  modules = [ ./home.nix ];
  extraSpecialArgs = { inherit inputs; }; # optional: pass flake inputs into modules
};
```

`pkgs` is mandatory and should come from the same `nixpkgs` input you intend to build against (typically `nixpkgs.legacyPackages.<system>`). Pass flake-level values into `home.nix` or imported modules via `extraSpecialArgs`; module-side wiring is covered in [writing HM modules](../../10-home-and-user/home-manager/writing-hm-modules.md). Prefer `extraSpecialArgs` for values that originate outside the module graph (such as flake inputs); use `_module.args` inside modules only when the argument must come from within the module graph.

**Applying standalone.** After the configuration evaluates, activate (build + switch generation) with:

```bash
home-manager switch --flake .#jdoe
```

When your shell’s working directory is the flake root, `home-manager switch --flake .` also works if the default configuration name matches your setup. Update [flake.lock](../anatomy/lockfile.md) with `nix flake update` when you intentionally bump inputs—Home Manager does not refresh flake inputs automatically on switch.

**As a NixOS module.** Add the Home Manager NixOS module to an existing `nixosSystem` `modules` list, set per-user modules under `home-manager.users.<name>`, and commonly enable `home-manager.useGlobalPkgs` and `home-manager.useUserPackages` so Home Manager shares the system package set and user profile layout. Rebuild with `sudo nixos-rebuild switch --flake .#<hostname>`. See [Standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md) for trade-offs; the flake-side system wiring is documented in [nixosConfigurations](nixos-configurations.md).

**Input pinning.** Match the Home Manager input branch to your Nixpkgs release (for example `github:nix-community/home-manager/release-26.05` alongside `github:NixOS/nixpkgs/nixos-26.05`). To avoid a second Nixpkgs checkout in the lock graph, reuse your root pin:

```nix
inputs.home-manager = {
  url = "github:nix-community/home-manager/release-26.05";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

`follows` aligns the **source revision** of Nixpkgs Home Manager sees with your flake’s `nixpkgs` input; it does not by itself make module-mode Home Manager use the same `pkgs` value as NixOS—that is what `home-manager.useGlobalPkgs = true` is for. See [follows and overrides](../anatomy/follow-and-overrides.md).

## Examples

Minimal flake with a pinned `nixpkgs` input, a matching Home Manager release branch, and one standalone configuration:

```nix
{
  description = "Home Manager flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager.url = "github:nix-community/home-manager/release-26.05";
  };

  outputs = { nixpkgs, home-manager, ... }@inputs: {
    homeConfigurations.jdoe = home-manager.lib.homeManagerConfiguration {
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      extraSpecialArgs = { inherit inputs; };
      modules = [ ./home.nix ];
    };
  };
}
```

Activate with `home-manager switch --flake .#jdoe`. The `./home.nix` file follows normal Home Manager option syntax.

Brief NixOS module import on the same flake (user env tied to system rebuilds):

```nix
nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
  system = "x86_64-linux";
  modules = [
    ./configuration.nix
    home-manager.nixosModules.home-manager
    {
      home-manager.useGlobalPkgs = true;
      home-manager.useUserPackages = true;
      home-manager.users.jdoe = ./home.nix;
    }
  ];
};
```

Deploy with `sudo nixos-rebuild switch --flake .#hostname` instead of `home-manager switch`.

## References

- [Home Manager manual — Nix Flakes](https://nix-community.github.io/home-manager/index.xhtml#ch-nix-flakes) — standalone, NixOS, and nix-darwin flake setups (experimental)
- [Home Manager — standalone flake setup](https://github.com/nix-community/home-manager/blob/master/docs/manual/nix-flakes/standalone.md) — `homeManagerConfiguration` and `extraSpecialArgs`
- [Home Manager manual](https://nix-community.github.io/home-manager/) — options, activation, and module reference
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — inputs, outputs, and reproducibility overview

## See also

- [nixosConfigurations](nixos-configurations.md) — NixOS systems via flakes; HM as a module inside `nixosSystem`
- [follows and overrides](../anatomy/follow-and-overrides.md) — deduplicating `nixpkgs` across inputs
- [Inputs and outputs](../anatomy/inputs-and-outputs.md) — conventional output keys including `homeConfigurations`
- [Flake (concept)](../../02-concepts/flake.md) — vocabulary and motivation for flakes
- [Standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md) — when to use each integration mode
- [Home and user environments](../../10-home-and-user/README.md) — Home Manager modules, dotfiles, and related topics
