---
status: complete
---

# Standalone vs NixOS Module

## Overview

[Home Manager](https://nix-community.github.io/home-manager/) manages user-level packages and [dotfiles](dotfiles-patterns.md) declaratively. The same module options apply in every install path; what changes is **how** the configuration is evaluated and activated.

Two main modes dominate day-to-day use:

1. **Standalone** — the `home-manager` CLI (and flake `homeConfigurations`) builds and switches a user profile independently of the host OS.
2. **NixOS module** — `home-manager.nixosModules.home-manager` ties Home Manager users into the system evaluation so profiles rebuild with `nixos-rebuild`.

A third path, `home-manager.darwinModules.home-manager`, does the same for [nix-darwin](../nix-darwin.md) with `darwin-rebuild`. Non-NixOS / non-Darwin hosts have only the standalone choice.

## Details

**Standalone.** You declare a Home Manager configuration (classically `~/.config/home-manager/home.nix`, or a flake `homeConfigurations.<name>` via `home-manager.lib.homeManagerConfiguration`) and activate with `home-manager switch`. That switch does **not** require `nixos-rebuild`. Prefer standalone when:

- the machine is not NixOS (or you are not using nix-darwin);
- user dotfiles should move on a different cadence than the system;
- several machines share one user config without sharing system modules.

Flake wiring for this path is covered in [homeConfigurations](../../07-flakes/workflows/home-configurations.md).

**NixOS module.** Import `home-manager.nixosModules.home-manager` into a NixOS module list and attach per-user modules under `home-manager.users.<name>`. Home Manager evaluates as part of the system config: one `nixos-rebuild switch` builds the OS **and** activates matching user profiles. Common companion options:

- `home-manager.useGlobalPkgs = true` — Home Manager modules receive the system `pkgs` (configure overlays / `nixpkgs.*` at the NixOS level instead of under Home Manager).
- `home-manager.useUserPackages = true` — install user packages into the user’s profile in the usual NixOS layout.

Because activation rides the system rebuild, backup-file and activation-script interactions follow the NixOS generation path rather than a separate `home-manager` generation. Account identity still comes from NixOS [users and groups](../../09-nixos/configuration/users-and-groups.md); Home Manager configures the home directory of those users.

**nix-darwin.** Same shape as the NixOS module: import `home-manager.darwinModules.home-manager`, set `home-manager.users.<name>`, rebuild with `darwin-rebuild`. See [nix-darwin](../nix-darwin.md).

**Flakes: where the config lives.**

| Mode | Typical flake surface | Activate with |
|------|----------------------|---------------|
| Standalone | `homeConfigurations.<name>` | `home-manager switch --flake .#<name>` |
| NixOS-embedded | `nixosConfigurations.<host>` + `home-manager.users.<name>` | `nixos-rebuild switch --flake .#<host>` |
| Darwin-embedded | `darwinConfigurations.<host>` + `home-manager.users.<name>` | `darwin-rebuild switch --flake .#<host>` |

Only standalone uses the `homeConfigurations` output key. Module modes wire Home Manager through the system flake; there is no separate `homeConfigurations` entry for those users unless you also define a standalone config.

**Choosing.** Use standalone for independence (or non-NixOS hosts). Use the NixOS (or darwin) module when you want a single rebuild, shared `pkgs`, and home config that cannot drift from the system declaration. You can keep the same `home.nix` modules in either mode; only the import and activation path change. Authoring those modules is covered in [writing HM modules](writing-hm-modules.md).

Home Manager’s flake support is **experimental** and may change incompatibly; pin the Home Manager input to a release branch that matches your Nixpkgs channel.

## Examples

Standalone flake entry (independent of NixOS):

```nix
homeConfigurations."alice" = home-manager.lib.homeManagerConfiguration {
  pkgs = nixpkgs.legacyPackages.x86_64-linux;
  modules = [ ./home.nix ];
};
```

```bash
home-manager switch --flake .#alice
```

Same `home.nix` embedded in a NixOS flake (rebuilds with the system):

```nix
nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
  system = "x86_64-linux";
  modules = [
    ./configuration.nix
    home-manager.nixosModules.home-manager
    {
      home-manager.useGlobalPkgs = true;
      home-manager.useUserPackages = true;
      home-manager.users.alice = import ./home.nix;
    }
  ];
};
```

```bash
sudo nixos-rebuild switch --flake .#hostname
```

## References

- [Home Manager manual](https://nix-community.github.io/home-manager/) — installation modes, options, activation
- [Home Manager — Nix Flakes](https://nix-community.github.io/home-manager/index.xhtml#ch-nix-flakes) — standalone, NixOS, and nix-darwin flake setups
- [Home Manager — NixOS module](https://nix-community.github.io/home-manager/index.xhtml#sec-install-nixos-module) — installing as a system module

## See also

- [Writing HM modules](writing-hm-modules.md)
- [Dotfiles patterns](dotfiles-patterns.md)
- [nix-darwin](../nix-darwin.md)
- [homeConfigurations](../../07-flakes/workflows/home-configurations.md)
- [Users and groups](../../09-nixos/configuration/users-and-groups.md)
- [Home Manager (ecosystem)](../../13-implementations/module-ecosystems/home-manager.md)
