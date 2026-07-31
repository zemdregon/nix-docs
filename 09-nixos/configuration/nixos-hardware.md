---
status: complete
---

# nixos-hardware

## Overview

**[nixos-hardware](https://github.com/NixOS/nixos-hardware)** is a NixOS-org collection of optional modules and profiles for machine-specific quirks—laptops, SBCs, and common PCs. Profiles typically set kernel parameters, firmware-related options, and device workarounds. They are **not** a replacement for [`hardware-configuration.nix`](hardware-configuration.md) from `nixos-generate-config`: import a matching profile **plus** your generated hardware config (filesystems, detected modules, partitioning).

## Details

**Role vs generated hardware config.** [`hardware-configuration.nix`](hardware-configuration.md) records scanned facts (mounts, swap, initrd modules). nixos-hardware adds curated, model- or class-specific tweaks on top. Keep both: the profile for quirks, the generated file (and your [partitioning / bootloader](partitioning-and-bootloaders.md) choices) for the machine’s layout. Import them from [`configuration.nix`](configuration-nix.md) or your flake’s module list the same way as other [imports and profiles](imports-and-profiles.md).

**Choosing a profile.** Prefer an exact model when one exists (README table / `flake.nix` `nixosModules` names—e.g. `dell-xps-13-9380`, `lenovo-thinkpad-x220`). If none matches, use a broader `common-*` profile such as `common-pc` or `common-pc-laptop`. Do not invent option lists from memory; check the upstream profile file and the [README profile table](https://github.com/NixOS/nixos-hardware/blob/master/README.md).

**Flakes.** Add an input (often `github:NixOS/nixos-hardware/master`, or pin a rev) and include `nixos-hardware.nixosModules.<name>` in `nixosSystem`’s `modules`. Attribute names live in the flake’s [`nixosModules`](https://github.com/NixOS/nixos-hardware/blob/master/flake.nix) attrset. Keep importing `./hardware-configuration.nix` (or equivalent) alongside the hardware profile. See [NixOS configurations with flakes](../../07-flakes/workflows/nixos-configurations.md).

**Channels / path imports.** Add the channel, then import a **path** under that channel—not the flake attr name:

```text
sudo nix-channel --add https://github.com/NixOS/nixos-hardware/archive/master.tar.gz nixos-hardware
sudo nix-channel --update
```

Example path: `<nixos-hardware/lenovo/thinkpad/x220>`. The path form mirrors the repo tree; the flake form uses kebab-case module names.

**Firmware and microcode.** Some profiles enable firmware or CPU microcode-related settings. For the general story of `hardware.enableRedistributableFirmware` and CPU microcode, see [Firmware and microcode](firmware-and-microcode.md) and what [`nixos-generate-config`](hardware-configuration.md) already emits—do not treat nixos-hardware as the sole firmware guide.

**Pinning.** Tracking `master` is common but churny. Prefer locking via `flake.lock` (automatic with flakes) or a fixed commit/`fetchGit` revision for channels and non-flake fetches.

**Contributing.** To add a new device profile, follow the upstream [CONTRIBUTING](https://github.com/NixOS/nixos-hardware/blob/master/CONTRIBUTING.md) guidance linked from the README.

### Boundaries (what this page is not)

- [hardware-configuration.nix](hardware-configuration.md) from `nixos-generate-config`.
- [Firmware and microcode](firmware-and-microcode.md) flags in isolation—CPU and `/lib/firmware` policy.
- [disko recipes](disko-recipes.md)—declarative partitioning and install templates.

## Examples

Flake: hardware input plus a model module, keeping generated hardware config:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixos-hardware.url = "github:NixOS/nixos-hardware/master";
  };

  outputs = { nixpkgs, nixos-hardware, ... }: {
    nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        ./hardware-configuration.nix
        nixos-hardware.nixosModules.lenovo-thinkpad-x220
      ];
    };
  };
}
```

Channel-style alternative (same idea; path instead of flake attr):

```nix
{ ... }: {
  imports = [
    <nixos-hardware/lenovo/thinkpad/x220>
    ./hardware-configuration.nix
  ];
}
```

## See also

- [hardware-configuration.nix](hardware-configuration.md)
- [Firmware and microcode](firmware-and-microcode.md)
- [Partitioning and bootloaders](partitioning-and-bootloaders.md)
- [configuration.nix](configuration-nix.md)
- [Imports and profiles](imports-and-profiles.md)
- [Manual install](../installation/manual-install.md)
- [NixOS configurations (flakes)](../../07-flakes/workflows/nixos-configurations.md)

## References

- [NixOS/nixos-hardware](https://github.com/NixOS/nixos-hardware)
- [nixos-hardware README](https://github.com/NixOS/nixos-hardware/blob/master/README.md) (setup, profile table, contributing pointer)
- [flake.nix `nixosModules`](https://github.com/NixOS/nixos-hardware/blob/master/flake.nix)
