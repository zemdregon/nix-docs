---
status: complete
---

# Firmware and microcode

## Overview

NixOS ships device firmware and CPU microcode through hardware options, not as ad-hoc `/lib/firmware` copies. Redistributable firmware is the usual switch for Wi‑Fi, audio, and similar blobs; “all firmware” adds unfree packages and needs an allow-unfree policy. CPU microcode is separate: when enabled, an Intel or AMD microcode image is prepended into the initrd so the kernel can apply updates early in boot. That path is distinct from [nixos-hardware](nixos-hardware.md) machine profiles and from [Secure Boot / Lanzaboote](secure-boot-and-lanzaboote.md).

## Details

**Redistributable vs all firmware.** Both options default to off (`hardware.enableAllFirmware` is `false`; `hardware.enableRedistributableFirmware` defaults to that value). Enabling redistributable firmware pulls in packages whose licenses allow redistribution. Setting `hardware.enableAllFirmware` also adds unfree blobs (for example Broadcom Bluetooth, b43 wireless, Xbox dongle, and FaceTime HD firmware on x86); those packages require allowing unfree in nixpkgs (see [Allowing unfree packages](https://nixos.org/manual/nixpkgs/unstable/#sec-allow-unfree)). Prefer the redistributable option unless you know you need the unfree set.

**What gets loaded.** When either redistributable or all firmware is enabled, the `all-firmware` module appends packages such as `linux-firmware`, `sof-firmware`, ALSA firmware, and several device-specific blobs to `hardware.firmware` (plus Raspberry Pi wireless firmware on aarch). `enableAllFirmware` adds further unfree packages on top. `hardware.wirelessRegulatoryDatabase` defaults to on whenever redistributable or all firmware is enabled, and then adds `wireless-regdb` to the same list.

**CPU microcode.** `hardware.cpu.intel.updateMicrocode` and `hardware.cpu.amd.updateMicrocode` (default `false`) prepend the corresponding microcode image into `boot.initrd.prepend` with `lib.mkOrder 1` so it runs before other initrd content. Package overrides exist as `hardware.cpu.intel.microcodePackage` / `hardware.cpu.amd.microcodePackage` if you need a non-default blob set.

**Generator and profiles.** On bare metal, `nixos-generate-config` often writes something like `hardware.cpu.*.updateMicrocode = lib.mkDefault config.hardware.enableRedistributableFirmware;` into [hardware-configuration.nix](hardware-configuration.md). Enabling redistributable firmware in [configuration.nix](configuration-nix.md) then turns microcode on via that default. [nixos-hardware](nixos-hardware.md) profiles may set the same options for a given machine; that is optional and separate from the generator.

## Examples

Typical host policy (redistributable firmware + microcode via generated defaults):

```nix
{ config, lib, ... }: {
  imports = [ ./hardware-configuration.nix ];

  hardware.enableRedistributableFirmware = true;
  # If hardware-configuration.nix has:
  #   hardware.cpu.intel.updateMicrocode =
  #     lib.mkDefault config.hardware.enableRedistributableFirmware;
  # then Intel microcode follows this flag.
}
```

Illustrative generated microcode line (do not hand-edit lasting policy into the generated file):

```nix
hardware.cpu.amd.updateMicrocode =
  lib.mkDefault config.hardware.enableRedistributableFirmware;
```

Unfree “all firmware” (requires allow-unfree for those packages):

```nix
{
  nixpkgs.config.allowUnfree = true;
  hardware.enableAllFirmware = true;
}
```

## See also

- [hardware-configuration.nix](hardware-configuration.md)
- [configuration.nix](configuration-nix.md)
- [nixos-hardware](nixos-hardware.md)
- [Partitioning and bootloaders](partitioning-and-bootloaders.md)
- [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md)

## References

- [nixpkgs `all-firmware.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/all-firmware.nix) — `enableRedistributableFirmware`, `enableAllFirmware`, `wirelessRegulatoryDatabase`, `hardware.firmware` packages
- [nixpkgs `intel-microcode.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/cpu/intel-microcode.nix) — `hardware.cpu.intel.updateMicrocode` → `boot.initrd.prepend`
- [nixpkgs `amd-microcode.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/cpu/amd-microcode.nix) — `hardware.cpu.amd.updateMicrocode` → `boot.initrd.prepend`
- [nixpkgs manual — Allowing unfree packages](https://nixos.org/manual/nixpkgs/unstable/#sec-allow-unfree) — required for unfree firmware pulled in by `enableAllFirmware`
