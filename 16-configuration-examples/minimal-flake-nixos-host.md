---
status: complete
last-checked: 2026-08
---

# Minimal flake NixOS host

## Overview

This walkthrough wires one NixOS machine through a flake: pinned `nixpkgs`, a `nixosConfigurations` output, a host module tree, and the commands to build, check, and switch. It is a **file-layout story**—not a tour of every NixOS option. For module semantics and activation modes, follow the links in [Domains composed](#domains-composed) instead of treating this page as the only reference.

## Details

### What you get

One repository directory with three Nix files and a lockfile after the first `nix flake lock`. The flake output name (`hostname` in the snippets below) is what you pass after `#` in rebuild and build commands. Evaluating that output produces a closed system [generation](../02-concepts/generation.md) you can activate with `nixos-rebuild switch --flake .#hostname`.

### Domains composed

This example pulls together teaching pages from several domains:

- [Declarative vs imperative](../01-philosophy/declarative-vs-imperative.md) — edit Nix, rebuild; the running system follows evaluated config
- [Flake](../02-concepts/flake.md) and [Generation](../02-concepts/generation.md) — pinned inputs, named outputs, profile history
- [`nix flake`](../05-cli-and-tooling/modern-cli/nix-flake.md) — lock, check, and build flake outputs from the CLI
- [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) and [Lockfile](../07-flakes/anatomy/lockfile.md) — `nixosSystem` wiring and input pinning
- [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md) — experimental features this workflow requires
- [configuration.nix](../09-nixos/configuration/configuration-nix.md), [hardware-configuration.nix](../09-nixos/configuration/hardware-configuration.md), and [rebuild actions](../09-nixos/operations/rebuild-switch-boot-test.md) — host module shape and activation

### File layout

```
.
├── flake.nix
├── flake.lock              # after nix flake lock
├── configuration.nix       # host policy you edit
└── hardware-configuration.nix   # machine facts (generated on real installs)
```

On a real install, `hardware-configuration.nix` comes from `nixos-generate-config` (filesystem UUIDs, initrd modules, platform). The stub below is enough for the walkthrough; do not copy it to bare metal without replacing disk and boot facts.

### Annotated pieces

**`flake.nix`** — pin `nixpkgs`, expose one `nixosConfigurations` entry, pass flake `inputs` into modules:

```nix
{
  description = "Minimal single-host NixOS flake";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs, ... }@inputs: {
    nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [ ./configuration.nix ];
    };
  };
}
```

Prefer setting `nixpkgs.hostPlatform` in `hardware-configuration.nix` (see stub) over the legacy top-level `system` argument to `nixosSystem`. See [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) for `modules`, `specialArgs`, and multiple hosts.

**`configuration.nix`** — ordinary NixOS module; imports hardware facts and sets host policy. The option set matches the checked-in corpus fixture [minimal-configuration.nix](../meta/examples/minimal-configuration.nix):

```nix
{ config, pkgs, ... }: {
  imports = [ ./hardware-configuration.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "hostname";
  networking.networkmanager.enable = true;

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };

  environment.systemPackages = with pkgs; [ git vim ];

  # Set once at install to the release you started on; do not bump casually.
  system.stateVersion = "26.05";
}
```

**`hardware-configuration.nix` (stub)** — placeholder only; replace with generator output on real hardware:

```nix
{ config, lib, pkgs, modulesPath, ... }: {
  imports = [ (modulesPath + "/installer/scan/not-detected.nix") ];

  boot.initrd.availableKernelModules = [ "xhci_pci" "ahci" "nvme" "usb_storage" "sd_mod" ];
  boot.initrd.kernelModules = [ ];
  boot.kernelModules = [ "kvm-intel" ];
  boot.extraModulePackages = [ ];

  fileSystems."/" = {
    device = "/dev/disk/by-uuid/REPLACE-ME";
    fsType = "ext4";
  };

  nixpkgs.hostPlatform = lib.mkDefault "x86_64-linux";
}
```

### Activate / verify

Enable experimental features (once per machine), then lock, check, build, and switch:

```bash
# nix.conf or --extra-experimental-features 'nix-command flakes'
nix flake lock
nix flake check
nix build .#nixosConfigurations.hostname.config.system.build.toplevel
sudo nixos-rebuild switch --flake .#hostname
```

`nix flake check` validates that each `nixosConfigurations.<name>.config.system.build.toplevel` evaluates to a valid derivation. `nix build …toplevel` produces the same closure without changing the running system or boot default. For `test`, `boot`, and rollback semantics, see [rebuild actions](../09-nixos/operations/rebuild-switch-boot-test.md).

### Failure modes

| Symptom | Likely cause |
|---------|----------------|
| `experimental Nix feature 'flakes' is disabled` | Enable [`flakes`](../08-experimental-features/flakes.md) and [`nix-command`](../08-experimental-features/nix-command.md) |
| `error: flake '…' does not provide attribute 'nixosConfigurations.…'` | Wrong `#name` after `--flake`; name must match the `nixosConfigurations` key |
| Services break after bumping `system.stateVersion` | `stateVersion` is a compatibility default for existing state, not a target release to chase |
| Boot fails or root cannot mount | Stub or stale `hardware-configuration.nix`; regenerate with `nixos-generate-config` on the target machine |
| Eval succeeds on laptop, fails on CI | Missing platform or hardware module facts; set `nixpkgs.hostPlatform` and real `fileSystems` for each host |

## Examples

End-to-end picture: three files from [File layout](#file-layout) and [Annotated pieces](#annotated-pieces) (`flake.nix`, `configuration.nix`, hardware stub), then:

```bash
nix flake lock
nix flake check
nix build .#nixosConfigurations.hostname.config.system.build.toplevel
sudo nixos-rebuild switch --flake .#hostname
```

Match `networking.hostName`, the `nixosConfigurations` key, and the `#` suffix (`hostname` here). On that machine, `nixos-rebuild switch --flake .` omits `#` when the hostname matches. Corpus twin: [minimal-configuration.nix](../meta/examples/minimal-configuration.nix).

## References

- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/)
- [nix.dev — Flakes](https://nix.dev/concepts/flakes)
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html)

## See also

- [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md)
- [configuration.nix](../09-nixos/configuration/configuration-nix.md)
- [hardware-configuration.nix](../09-nixos/configuration/hardware-configuration.md)
- [Rebuild: switch, boot, test](../09-nixos/operations/rebuild-switch-boot-test.md)
- [Flake](../02-concepts/flake.md)
- [Generation](../02-concepts/generation.md)
- [Lockfile](../07-flakes/anatomy/lockfile.md)
- [Example corpus](../meta/examples/README.md) — `minimal-configuration.nix`
