---
status: complete
---

# Firmware and microcode

## Overview

NixOS ships device firmware and CPU microcode through hardware options, not as ad-hoc `/lib/firmware` copies. **Redistributable firmware** is the usual switch for Wi‑Fi, audio, and similar blobs; **all firmware** adds unfree packages and needs an allow-unfree policy. **CPU microcode** is separate: when enabled, an Intel or AMD microcode image is prepended into the initrd so the kernel can apply CPU errata early in boot. That path is distinct from [nixos-hardware](nixos-hardware.md) machine profiles and from [Secure Boot / Lanzaboote](secure-boot-and-lanzaboote.md).

## Details

**Redistributable vs all firmware.** `hardware.enableAllFirmware` defaults to `false`. `hardware.enableRedistributableFirmware` defaults to that same value (`config.hardware.enableAllFirmware`). Enabling redistributable firmware pulls in packages whose licenses allow redistribution. Setting `hardware.enableAllFirmware = true` also turns on redistributable firmware (via the default) and adds unfree blobs—Broadcom Bluetooth, b43 wireless, Xbox One dongle (`xone-dongle-firmware`), and FaceTime HD firmware on x86. Those unfree packages require allowing unfree in nixpkgs (see [Allowing unfree packages](https://nixos.org/manual/nixpkgs/unstable/#sec-allow-unfree)). Prefer redistributable unless you know you need the unfree set.

**What gets loaded.** When either option is enabled, the `all-firmware` module appends packages to `hardware.firmware`: `linux-firmware`, `ipw2200-firmware`, several Realtek blobs, `zd1211fw`, `alsa-firmware`, `sof-firmware`, `libreelec-dvb-firmware`, and on aarch64 `raspberrypiWirelessFirmware`. `enableAllFirmware` adds further unfree packages on top. `hardware.wirelessRegulatoryDatabase` defaults to on whenever redistributable or all firmware is enabled and then adds `wireless-regdb` to the same list.

**CPU microcode.** `hardware.cpu.intel.updateMicrocode` and `hardware.cpu.amd.updateMicrocode` default to `false`. When enabled, the corresponding module prepends `intel-ucode.img` or `amd-ucode.img` into `boot.initrd.prepend` with `lib.mkOrder 1` so microcode runs before other initrd content. Package overrides exist as `hardware.cpu.intel.microcodePackage` and `hardware.cpu.amd.microcodePackage` if you need a non-default blob set. Microcode addresses CPU errata and security fixes—not Wi‑Fi, Bluetooth, or GPU drivers.

**Generator and profiles.** On bare metal, `nixos-generate-config` often writes `hardware.cpu.*.updateMicrocode = lib.mkDefault config.hardware.enableRedistributableFirmware;` into [hardware-configuration.nix](hardware-configuration.md). Enabling redistributable firmware in [configuration.nix](configuration-nix.md) then turns microcode on via that default. Put lasting policy in `configuration.nix`; do not hand-edit the generated file for options you intend to keep. [nixos-hardware](nixos-hardware.md) profiles may set the same options for a given machine; that is optional and separate from the generator.

**Choosing a policy.** Use the table below to pick flags; GPU drivers and Steam unfree policy are cousins but separate knobs—see [Gaming: Steam and Proton](../desktop/gaming-steam-proton.md).

| Goal | Set | Notes |
|------|-----|-------|
| Wi‑Fi / audio / most device blobs | `hardware.enableRedistributableFirmware = true` | Default recommendation after install |
| Broadcom BT, b43, FaceTime HD, Xbox dongle, etc. | `hardware.enableAllFirmware = true` plus `nixpkgs.config.allowUnfree = true` | Implies redistributable via default |
| CPU errata / security microcode | `hardware.cpu.intel.updateMicrocode` or `hardware.cpu.amd.updateMicrocode` | Often follows redistributable via `mkDefault` from generate-config |
| Regulatory Wi‑Fi limits (country codes) | `hardware.wirelessRegulatoryDatabase` | Defaults on when either firmware flag is enabled |

**Common pitfalls.**

- **Wi‑Fi or Bluetooth missing after install.** The generated config often leaves firmware off. Enable `hardware.enableRedistributableFirmware` in `configuration.nix` and rebuild; if the chip still needs an unfree blob (common on some Broadcom parts), switch to `enableAllFirmware` with allow-unfree. The graphical installer exposes an unfree toggle—see [Graphical installer](../installation/graphical-installer.md); manual installs must add the flags yourself—see [Manual install](../installation/manual-install.md).
- **Confusing microcode with device firmware.** Microcode updates the CPU; it does not load Wi‑Fi or Bluetooth firmware. Enable the firmware flags for wireless; enable `updateMicrocode` for CPU errata.
- **Editing `hardware-configuration.nix` for policy.** Re-running `nixos-generate-config` overwrites that file. Set firmware and microcode in `configuration.nix` (or a flake module) instead.
- **`enableAllFirmware` without allow-unfree.** Evaluation or build fails when nixpkgs refuses unfree packages. Set `nixpkgs.config.allowUnfree = true` or a targeted `allowUnfreePredicate`.
- **Expecting nixos-hardware or Secure Boot to replace these flags.** Profiles may set firmware options for a machine type; [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md) covers boot trust, not `/lib/firmware` content.

### Boundaries (what this page is not)

- [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md)—signed boot chain and firmware key enrollment.
- [nixos-hardware](nixos-hardware.md) machine profiles—vendor/model module bundles beyond firmware flags.
- GPU and display drivers—see [Wayland and compositors](../desktop/wayland-and-compositors.md) for `hardware.graphics`.

## Examples

Typical host policy (redistributable firmware; microcode follows generated default):

```nix
{ config, lib, ... }: {
  imports = [ ./hardware-configuration.nix ];

  hardware.enableRedistributableFirmware = true;
  # If hardware-configuration.nix contains:
  #   hardware.cpu.intel.updateMicrocode =
  #     lib.mkDefault config.hardware.enableRedistributableFirmware;
  # then Intel microcode follows this flag.
}
```

Explicit microcode when the generator did not link it (pick Intel *or* AMD):

```nix
{
  hardware.enableRedistributableFirmware = true;
  hardware.cpu.amd.updateMicrocode = true;
}
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
- [Graphical installer](../installation/graphical-installer.md)
- [Gaming: Steam and Proton](../desktop/gaming-steam-proton.md)
- [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md)

## References

- [nixpkgs `all-firmware.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/all-firmware.nix) — `enableRedistributableFirmware`, `enableAllFirmware`, `wirelessRegulatoryDatabase`, `hardware.firmware` packages
- [nixpkgs `intel-microcode.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/cpu/intel-microcode.nix) — `hardware.cpu.intel.updateMicrocode` → `boot.initrd.prepend`
- [nixpkgs `amd-microcode.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/hardware/cpu/amd-microcode.nix) — `hardware.cpu.amd.updateMicrocode` → `boot.initrd.prepend`
- [nixpkgs manual — Allowing unfree packages](https://nixos.org/manual/nixpkgs/unstable/#sec-allow-unfree) — required for unfree firmware pulled in by `enableAllFirmware`
