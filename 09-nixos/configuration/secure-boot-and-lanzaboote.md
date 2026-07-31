---
status: complete
---

# Secure Boot and Lanzaboote

## Overview

NixOS does **not** ship turnkey UEFI Secure Boot in core modules. [Partitioning and bootloaders](partitioning-and-bootloaders.md) covers ordinary systemd-boot/GRUB and optional UKI/`ukify` wiring; signing a chain of trust for firmware enforcement is separate operator work.

**[Lanzaboote](https://github.com/nix-community/lanzaboote)** (nix-community) is the usual path: a custom UEFI stub, the `lzbt` installer, and a NixOS module for Secure Boot (and optional measured boot). It is **advanced and sharp-edged**—docs target experienced users, recommend backups and recovery comfort, and note uneven firmware support (ThinkPads and Framework machines are better tested; no guarantees). Pin a release tag; treat the stack as community tooling that still evolves.

## Details

**Prerequisites.** Install NixOS in **UEFI** mode with **systemd-boot** as the current loader first, then switch to Lanzaboote. Confirm with `bootctl status`: Firmware should be UEFI; Current Boot Loader should be systemd-boot. ESP layout and generation pressure still matter—see [Partitioning and bootloaders](partitioning-and-bootloaders.md) and [Generations and boot](../architecture/generations-and-boot.md).

**Architecture.** NixOS [bootspec](https://github.com/NixOS/rfcs/pull/125) (enabled by default since NixOS 23.05) describes bootable generations. `lzbt` consumes bootspec, signs boot artifacts, and installs them to the ESP. Packing a full UKI per generation with `systemd-stub` (kernel + initrd inside each image) pressures small ESPs when many [generations](../architecture/generations-and-boot.md) are retained. Lanzaboote’s stub keeps kernel and initrd as separate ESP files while preserving the chain of trust (signed stub/kernel; initrd integrity via hash embedded in the signed UKI).

**Module pattern (flakes).** Add a **pinned** input such as `github:nix-community/lanzaboote/v1.1.0` (or another [release tag](https://github.com/nix-community/lanzaboote/releases)—prefer tags over floating `main`). Import `lanzaboote.nixosModules.lanzaboote`. Force `boot.loader.systemd-boot.enable = lib.mkForce false` (Lanzaboote replaces that module). Enable `boot.lanzaboote.enable = true` and set `boot.lanzaboote.pkiBundle` to the key bundle path (docs use `"/var/lib/sbctl"`). Install `pkgs.sbctl` for key creation, enrollment helpers, and `sbctl verify` debugging.

**Keys and firmware.** After the module rebuilds a signed boot layout (“prepare your system”), enabling Secure Boot in firmware and enrolling keys is a **separate** step: create keys with `sbctl` (typically under `/var/lib/sbctl`), enroll into the platform (docs cover Setup Mode and enrollment), then turn enforcement on. Firmware menus and quirks vary by vendor—follow the [Lanzaboote getting-started docs](https://nix-community.github.io/lanzaboote/); do not invent board-specific steps here. Optional measured boot (TPM PCR policy for LUKS unlock) is a follow-on—see [TPM and measured boot](tpm-and-measured-boot.md).

**Operational caveats.** Lanzaboote does not replace understanding ESP size, generation limits, or recovery when the machine will not boot. Keep a recovery plan ([Troubleshooting](../operations/troubleshooting.md)). Pin the Lanzaboote release and re-read release notes when upgrading.

### Boundaries (what this page is not)

- Generic [EFI partitioning](partitioning-and-bootloaders.md)—ESP size, mount points, and bootloader choice.
- [TPM Clevis and measured boot](tpm-and-measured-boot.md)—pcrlock policy and initrd unlock paths.
- [Firmware and microcode](firmware-and-microcode.md)—CPU errata and `/lib/firmware` blobs.

## Examples

Illustrative flake fragment (not a full host config). Follow current Lanzaboote docs for key creation, enrollment, and firmware setup after the first rebuild.

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    lanzaboote = {
      url = "github:nix-community/lanzaboote/v1.1.0";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { nixpkgs, lanzaboote, ... }: {
    nixosConfigurations.yourHost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        lanzaboote.nixosModules.lanzaboote
        ({ pkgs, lib, ... }: {
          environment.systemPackages = [ pkgs.sbctl ];
          boot.loader.systemd-boot.enable = lib.mkForce false;
          boot.lanzaboote = {
            enable = true;
            pkiBundle = "/var/lib/sbctl";
          };
        })
        # …your normal configuration…
      ];
    };
  };
}
```

## See also

- [Partitioning and bootloaders](partitioning-and-bootloaders.md) — ESP, systemd-boot, UKI/`ukify`, Secure Boot as advanced follow-on
- [TPM and measured boot](tpm-and-measured-boot.md) — Lanzaboote measured boot / pcrlock after Secure Boot
- [Generations and boot](../architecture/generations-and-boot.md) — generations and boot entries
- [hardware-configuration.nix](hardware-configuration.md) — generated filesystem and ESP mount facts
- [Manual install](../installation/manual-install.md) — UEFI install path before switching loaders
- [Troubleshooting](../operations/troubleshooting.md) — boot / ESP recovery symptoms

## References

- [Lanzaboote documentation](https://nix-community.github.io/lanzaboote/) — prerequisites, prepare-your-system, enabling Secure Boot (community; evolving)
- [nix-community/lanzaboote](https://github.com/nix-community/lanzaboote) — source, releases, README architecture (`lzbt`, stub, bootspec)
- [NixOS RFC PR #125 — bootspec](https://github.com/NixOS/rfcs/pull/125) — bootspec context (enabled by default since NixOS 23.05)
