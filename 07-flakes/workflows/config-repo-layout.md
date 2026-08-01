---
status: draft
---

# Config repo layout

## Overview

A **config mono-repo** is a single flake that holds NixOS systems, optional Home Manager profiles, shared modules, and sometimes custom packages. There is no upstream-mandated tree, but most repos converge on the same shape: `flake.nix` at the root, one module per host under `hosts/`, reusable role modules under `modules/`, and flake inputs threaded through `specialArgs` rather than read from `config` during import resolution.

This page describes **folder conventions** and how they connect to [nixosConfigurations](nixos-configurations.md) and [homeConfigurations](home-configurations.md). Output wiring and module semantics are covered in those pages and under [09-nixos](../../09-nixos/README.md).

## Details

**Typical directory layout.**

| Path | Role |
|------|------|
| `flake.nix` | Inputs, `nixosConfigurations`, optional `homeConfigurations`, exported modules |
| `hosts/<hostname>/default.nix` | Per-machine entry module: imports roles + `hardware-configuration.nix`, host-only overrides |
| `modules/` | Shared NixOS (or HM) modules — roles such as `desktop.nix`, `server.nix`, `networking.nix` |
| `users/<name>/home.nix` | Optional per-user Home Manager module when not colocated with the host |
| `overlays/` | Nixpkgs overlays applied from host or shared modules |
| `pkgs/` | Custom packages built with `callPackage` and referenced from modules |

Filenames are conventions, not requirements. The pattern is **thin entry modules** that `imports` focused fragments; see [Imports and profiles](../../09-nixos/configuration/imports-and-profiles.md).

**Wiring hosts in `flake.nix`.** Each machine gets a `nixosConfigurations.<host>` entry. Pass flake inputs into every module via `specialArgs` so host and role modules can use `inputs` without importing the flake root:

```nix
nixosConfigurations.laptop = nixpkgs.lib.nixosSystem {
  modules = [ ./hosts/laptop/default.nix ];
  specialArgs = { inherit inputs; };
};
```

Do not try to pass inputs by reading merged `config` inside `imports` — import lists must be static (see anti-patterns below).

**Host entry module.** `hosts/<hostname>/default.nix` typically:

1. `imports` shared role modules from `modules/` (and optionally `home-manager.nixosModules.home-manager`).
2. `imports` `./hardware-configuration.nix` (generated at install; disk and bootloader specifics stay here).
3. Sets only what differs for this host — hostname, networking, one-off service toggles.

Role modules encode **capabilities** (desktop, NAS, hypervisor); the host file picks which roles apply.

**Home Manager placement.** Two common patterns:

1. **Standalone** — `homeConfigurations.<user>` in `flake.nix`, modules under `users/<name>/home.nix`. Use on non-NixOS hosts or when dotfiles evolve on a separate cadence. See [homeConfigurations](home-configurations.md).
2. **NixOS-embedded** — import `home-manager.nixosModules.home-manager` in the host module list and set `home-manager.users.<user> = ./users/<name>/home.nix` (or an inline module). User env rebuilds with `nixos-rebuild`, not `home-manager switch`.

Both can coexist in one repo for different users or machines.

**Exporting reusable modules.** Flakes can expose `nixosModules.<name>` and `home-managerModules.<name>` so other flakes import your roles without copying files. Define them as paths or functions in `outputs` and reference them from `imports` in the same repo or in downstream flakes.

**Framework alternatives.** The same decomposition problem — many hosts, shared roles, several output keys — is solved with scaffolds that map directories to outputs:

- [flake-parts](../../13-implementations/module-ecosystems/flake-parts.md) — module-system evaluation of `outputs`, `perSystem` for packages and checks.
- [Snowfall](../../13-implementations/community-frameworks/snowfall.md), [Blueprint](../../13-implementations/community-frameworks/blueprint-and-others.md) — opinionated folder → output conventions with a thin `flake.nix`.

Use a framework when manual `flake.nix` glue becomes noisy; the underlying layout (hosts, modules, users) stays recognizable.

**Anti-patterns.**

- **One giant `configuration.nix`** — hard to review, merge-conflict prone, and difficult to reuse across hosts. Split by role and import.
- **Conditional `imports` from `config`** — `imports` is resolved before the module fixpoint; you cannot `import` a path chosen from `config.services.*.enable`. Use `mkIf` on options inside static modules, or separate host entry files per role.
- **Inputs only via `config`** — flake inputs belong in `specialArgs` / `_module.args`, not reconstructed from option values.

## Examples

Illustrative mono-repo tree:

```
.
├── flake.nix
├── hosts/
│   ├── laptop/
│   │   ├── default.nix
│   │   └── hardware-configuration.nix
│   └── server/
│       ├── default.nix
│       └── hardware-configuration.nix
├── modules/
│   ├── desktop.nix
│   └── server.nix
├── users/
│   └── alice/
│       └── home.nix
├── overlays/
│   └── default.nix
└── pkgs/
    └── my-cli/
        └── default.nix
```

Root `flake.nix` (abbreviated):

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager.url = "github:nix-community/home-manager/release-26.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { nixpkgs, home-manager, ... }@inputs: {
    nixosConfigurations.laptop = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [ ./hosts/laptop/default.nix ];
    };

    nixosModules.desktop = ./modules/desktop.nix;

    homeConfigurations.alice = home-manager.lib.homeManagerConfiguration {
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      extraSpecialArgs = { inherit inputs; };
      modules = [ ./users/alice/home.nix ];
    };
  };
}
```

Host entry with embedded Home Manager:

```nix
# hosts/laptop/default.nix
{ inputs, ... }:
{
  imports = [
    ../../modules/desktop.nix
    ./hardware-configuration.nix
    inputs.home-manager.nixosModules.home-manager
  ];

  networking.hostName = "laptop";

  home-manager.useGlobalPkgs = true;
  home-manager.useUserPackages = true;
  home-manager.users.alice = ../../users/alice/home.nix;
}
```

Deploy: `sudo nixos-rebuild switch --flake .#laptop`. Standalone HM for the same user: `home-manager switch --flake .#alice`.

## References

- [nix.dev — Flakes tutorial](https://nix.dev/tutorials/flakes.html) — inputs, outputs, and `nixosConfigurations` basics
- [flake.parts](https://flake.parts/) — module-system flake outputs
- [Home Manager manual — Nix Flakes](https://nix-community.github.io/home-manager/index.xhtml#sec-flakes) — standalone and NixOS-module integration (experimental)

## See also

- [Inputs and outputs](../anatomy/inputs-and-outputs.md) — conventional flake output keys
- [nixosConfigurations](nixos-configurations.md) — `nixosSystem` wiring and rebuild
- [homeConfigurations](home-configurations.md) — standalone Home Manager flakes
- [Imports and profiles](../../09-nixos/configuration/imports-and-profiles.md) — static `imports` and splitting configuration
- [configuration.nix](../../09-nixos/configuration/configuration-nix.md) — primary machine configuration file
- [flake-parts](../../13-implementations/module-ecosystems/flake-parts.md) — `mkFlake` and `perSystem`
- [Dotfiles patterns](../../10-home-and-user/home-manager/dotfiles-patterns.md) — organizing user-level modules
