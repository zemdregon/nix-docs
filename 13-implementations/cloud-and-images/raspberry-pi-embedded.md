---
status: complete
---

# Raspberry Pi / Embedded

## Overview

NixOS on Raspberry Pi and similar SBCs is usually delivered as an **SD card image**, not a PC-style ISO. Nixpkgs ships installer modules under `nixos/modules/installer/sd-card/` (notably `sd-image-aarch64.nix`) that build a bootable image exposing `config.system.build.sdImage`. Board-specific quirks—kernels, firmware, `config.txt`, peripherals—come from optional modules in [NixOS/nixos-hardware](https://github.com/NixOS/nixos-hardware), not from a generated [hardware-configuration.nix](../../09-nixos/configuration/hardware-configuration.md) alone.

**Support varies by board.** AArch64 boards (Pi 3/4 families, Zero 2 W, and Pi 5 with a suitable image) are the practical path: Hydra and `cache.nixos.org` cover `aarch64-linux`. Older 32-bit ARM boards (Pi 1, Zero, Pi 2 on ARMv7) can still be built from Nixpkgs in principle, but there is no official binary cache and community effort is thinner. Peripheral, GPU, and boot-firmware behaviour depend on the chosen kernel and board revision—treat each target as its own validation surface.

## Details

**SD images.** Import an sd-card module (for example `${nixpkgs}/nixos/modules/installer/sd-card/sd-image-aarch64.nix`) into a NixOS system, then build `config.system.build.sdImage`. The resulting image has a FAT firmware partition and a root filesystem; after first boot you configure and `nixos-rebuild` like any other NixOS host. From NixOS **25.05**, `nixos-rebuild build-image --image-variant sd-card` (with `system` set) is the generators successor for the same idea; [nixos-generators](nixos-generators.md) still documents the older format names.

**nixos-hardware.** Profiles such as `raspberry-pi-3`, `raspberry-pi-4`, and `raspberry-pi-5` (flake: `nixos-hardware.nixosModules.…`) select Raspberry Pi–oriented kernels and declarative firmware/`config.txt` helpers. Import the profile that matches the board; pin the `nixos-hardware` revision with the rest of your inputs. A profile is not a disk layout—pair it with an sd-image module (or an existing install) when you need a flashable card. Stock generic AArch64 images use the mainline-ish NixOS kernel; hardware profiles often pin a Raspberry Pi downstream kernel instead. Choose deliberately and test on hardware.

**Cross vs native builds.** Building an `aarch64-linux` (or `armv7l-linux`) system from `x86_64-linux` means either:

- **True cross-compilation** — set `nixpkgs.buildPlatform` to the builder and `nixpkgs.hostPlatform` to the board (for example `aarch64-linux`). Not every package or out-of-tree module cross-builds cleanly.
- **Emulated native builds** — register QEMU via `boot.binfmt.emulatedSystems` on a NixOS builder so aarch64 derivations run locally (slower).
- **Remote / native ARM builders** — forward builds to an aarch64 machine; see [Remote builders](../../04-store-and-build/remote-builders.md). Prefer this when cross fails or emulation is too slow.

Firmware population for custom sd-images has improved for cross builds in nixos-hardware, but package-level support still varies—expect iteration.

**Caveats.** Pi 5 and newer boot-file requirements may lag a given stable release channel; check current ARM/sd-image notes before flashing a “stable” image onto a new board. Downstream kernels may disable or break modules the base image assumes (ZFS is a common example—force it off for sd-image builds when the pinned kernel does not build it). EEPROM/USB/NVMe boot paths are board- and firmware-version specific and are outside the generic NixOS install story. For non-Pi embedded boards, reuse the sd-image / cross-build patterns only where Nixpkgs and hardware modules actually exist for that SoC.

## Examples

Minimal sketch: AArch64 sd-image with a Pi 4 hardware profile (build on an aarch64 host or via remote/binfmt/cross as above):

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixos-hardware.url = "github:NixOS/nixos-hardware/master";
  };

  outputs = { nixpkgs, nixos-hardware, ... }: {
    nixosConfigurations.rpi4 = nixpkgs.lib.nixosSystem {
      system = "aarch64-linux";
      modules = [
        "${nixpkgs}/nixos/modules/installer/sd-card/sd-image-aarch64.nix"
        nixos-hardware.nixosModules.raspberry-pi-4
        ({ lib, ... }: {
          # Downstream Pi kernels often cannot build ZFS; base image may enable it.
          boot.supportedFilesystems.zfs = lib.mkForce false;
        })
        ./configuration.nix
      ];
    };
  };
}
```

Build the image attribute (flake path varies):

```bash
nix build .#nixosConfigurations.rpi4.config.system.build.sdImage
```

Cross from x86_64 (illustrative; adjust when packages fail to cross):

```nix
{
  nixpkgs.buildPlatform = "x86_64-linux";
  nixpkgs.hostPlatform = "aarch64-linux";
}
```

## See also

- [nixos-generators](nixos-generators.md)
- [hardware-configuration.nix](../../09-nixos/configuration/hardware-configuration.md)
- [Remote builders](../../04-store-and-build/remote-builders.md)

## References

- [NixOS/nixos-hardware](https://github.com/NixOS/nixos-hardware) — board modules (Raspberry Pi 2–5 and others); README (verified 2026-07)
- [Nixpkgs `sd-image-aarch64.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/installer/sd-card/sd-image-aarch64.nix) — generic AArch64 SD image module
- [Building Images with nixos-rebuild build-image](https://nixos.org/manual/nixos/stable/#sec-image-nixos-rebuild-build-image) — `sd-card` variant (NixOS ≥ 25.05)
- [NixOS Wiki: NixOS on ARM / Raspberry Pi](https://wiki.nixos.org/wiki/NixOS_on_ARM/Raspberry_Pi) — board matrix, images, and caveats
- [NixOS Wiki: Building Images](https://wiki.nixos.org/wiki/NixOS_on_ARM/Building_Images) — native, emulated, and cross builds
