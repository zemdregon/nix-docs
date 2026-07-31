---
status: complete
---

# nixosConfigurations

## Overview

**`nixosConfigurations.<name>`** is the flake output that exposes a complete NixOS system configuration. Each name (often the machine hostname) maps to the result of `nixpkgs.lib.nixosSystem`, which evaluates the [module system](../../09-nixos/architecture/module-system.md) and produces a closed system closure. The Nix CLI and `nixos-rebuild` consume this output to build, check, and switch generations on real hardware.

This page covers **flake wiring**—how inputs, modules, and output names connect. Module semantics, `configuration.nix` structure, and activation mechanics live under [09-nixos](../../09-nixos/README.md); see [Inputs and outputs](../anatomy/inputs-and-outputs.md) for how `nixosConfigurations` fits the general output schema.

## Details

**Defining a configuration.** Wire each host with `nixpkgs.lib.nixosSystem`:

```nix
nixosConfigurations.<name> = nixpkgs.lib.nixosSystem {
  modules = [
    ./configuration.nix
    # optional: other modules, Home Manager’s NixOS module, etc.
  ];
  specialArgs = { inherit inputs; }; # optional: pass flake inputs into modules
};
```

Documented arguments (from the Nixpkgs flake):

| Argument | Role |
|----------|------|
| `modules` | List of paths or inline modules merged into the system |
| `specialArgs` | Extra args available to every module (not overridable via `modules`) |
| `modulesLocation` | Default location for non-path modules (error messages) |

`system` and `pkgs` are **legacy** aliases for `nixpkgs.hostPlatform` and `nixpkgs.pkgs`. Prefer setting the platform in `hardware-configuration.nix` (or an equivalent module) rather than relying on the top-level `system` argument.

`nixosSystem` returns an evaluated NixOS config; `.config.system.build.toplevel` is the system derivation—the same artifact `nixos-rebuild` activates.

**Inputs and pinning.** Declare `inputs.nixpkgs.url` on a release branch (for example `github:NixOS/nixpkgs/nixos-26.05`) so system builds share a pinned package set with [flake.lock](../anatomy/lockfile.md). Pass other inputs into modules via `specialArgs` when modules need `inputs.home-manager`, custom flakes, or vendored sources.

**Home Manager.** Compose user environments on the same system by importing `home-manager.nixosModules.home-manager` (and a per-user module) in the `modules` list. Standalone HM flake wiring is covered in [homeConfigurations](home-configurations.md); here HM is just another module source for `nixosSystem`.

**Checking.** `nix flake check` verifies that each `nixosConfigurations.<name>.config.system.build.toplevel` evaluates to a valid derivation (experimental `nix-command` / `flakes`). Use this in CI before deploying.

**Building without switching.** Produce the system closure without activating it:

```bash
nix build .#nixosConfigurations.<name>.config.system.build.toplevel
```

The resulting symlink (or `./result`) is the same store path `nixos-rebuild switch` would register as a new [generation](../../02-concepts/generation.md).

**Applying on a machine.** On the target system (with flakes enabled):

```bash
sudo nixos-rebuild switch --flake .#<name>
```

Omitting `#<name>` makes `nixos-rebuild` look up `nixosConfigurations.<current-hostname>`. Use `boot` or `test` instead of `switch` for reboot-required or non-persistent trial activation; see [rebuild: switch, boot, test](../../09-nixos/operations/rebuild-switch-boot-test.md). Remote hosts use the same flake reference with `--target-host` and related flags—[remote deploy](../../09-nixos/operations/remote-deploy.md).

**Multiple machines.** One flake commonly defines several `nixosConfigurations` keys (`laptop`, `server`, `pi`) sharing base modules and differing only in hardware or role-specific imports. Each name is an independent output addressable as `.#<name>` in rebuild and build commands.

## Examples

Minimal flake with a pinned `nixpkgs` input and one NixOS configuration:

```nix
{
  description = "Example NixOS flake";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs, ... }@inputs: {
    nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [ ./configuration.nix ];
    };
  };
}
```

`./configuration.nix` is a normal NixOS module (often importing `./hardware-configuration.nix`); see [configuration.nix](../../09-nixos/configuration/configuration-nix.md). After evaluation succeeds, deploy with:

```bash
sudo nixos-rebuild switch --flake .#hostname
```

## References

- [NixOS manual](https://nixos.org/manual/nixos/stable/) — configuring and changing the system
- [nix.dev — Flakes](https://nix.dev/concepts/flakes) — inputs, outputs, experimental status
- [Nixpkgs `lib.nixosSystem`](https://github.com/NixOS/nixpkgs/blob/master/flake.nix) — documented arguments (`modules`, `specialArgs`, legacy `system` / `pkgs`)
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — validates `nixosConfigurations.*.config.system.build.toplevel`

## See also

- [Inputs and outputs](../anatomy/inputs-and-outputs.md) — conventional output keys including `nixosConfigurations`
- [Flake (concept)](../../02-concepts/flake.md) — vocabulary and motivation for flakes
- [Generation](../../02-concepts/generation.md) — what `nixos-rebuild switch` registers in `/nix/var/nix/profiles`
- [Module system](../../09-nixos/architecture/module-system.md) — how `nixosSystem` merges modules
- [configuration.nix](../../09-nixos/configuration/configuration-nix.md) — primary machine configuration file
- [Rebuild: switch, boot, test](../../09-nixos/operations/rebuild-switch-boot-test.md) — activation modes
- [Remote deploy](../../09-nixos/operations/remote-deploy.md) — `--target-host` and related workflows
- [homeConfigurations](home-configurations.md) — Home Manager as a flake output
- [nixos-rebuild (frontend)](../../13-implementations/frontends-and-ux/nixos-rebuild.md) — CLI flags and flake default hostname lookup
