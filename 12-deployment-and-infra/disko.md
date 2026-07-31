---
status: complete
---

# disko

## Overview

[disko](https://github.com/nix-community/disko) (nix-community) is declarative disk partitioning for NixOS. You describe devices, disks, partitions, filesystems, and mount points in Nix (`disko.devices`); disko partitions, formats, and mounts them—on a live installer, via [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md), or with **disko-install** (disko + `nixos-install` in one step).

It complements [hardware-configuration.nix](../09-nixos/configuration/hardware-configuration.md) by owning the filesystem layout (often with `nixos-generate-config --no-filesystems`). The NixOS module turns `disko.devices` into `fileSystems` and related boot options. It does not replace [bootloader](../09-nixos/configuration/partitioning-and-bootloaders.md) choice on its own—you still enable GRUB or systemd-boot in the NixOS config.

## Details

**What you declare.** Under `disko.devices`, nest `disk` (and related) entries with `type`, `device`, and nested `content` for partition tables (GPT, MBR, mixed), partitions, formats (ext4, vfat, btrfs, ZFS, bcachefs, …), and `mountpoint`s. Layouts can include LVM, LUKS, mdadm, and recursive nesting. Official examples and [disko-templates](https://github.com/nix-community/disko-templates) cover common single-disk and hybrid schemes.

**How you import the module.** Prefer a flake input (`github:nix-community/disko/latest`) and `disko.nixosModules.disko` in `nixosConfigurations` (see HowTo). Alternatives include niv, npins, nix-channel, or `fetchTarball`. Put the disk layout in the system configuration (imported module + `disko.devices` or a separate `disko-config.nix`).

**How it runs.**

- **Installer / manual path** — From a NixOS ISO (or similar), run disko against a disk config (`--mode destroy,format,mount`), then finish with `nixos-install` as in a [manual install](../09-nixos/installation/manual-install.md).
- **disko-install** — Combines partitioning and install: `nix run 'github:nix-community/disko/latest#disko-install' -- --flake … --disk <name> <device>`. Useful for fresh installs and bootable media; has a mount-only mode for repairing existing installs.
- **nixos-anywhere** — Remote install flow runs a disko phase before activating the flake’s `nixosConfigurations` entry.

**Relation to other config.** Hardware scan still covers kernel modules, firmware, and similar; filesystem entries normally come from disko rather than a generated `fileSystems` block. Prefer stable device paths (`/dev/disk/by-id/…`) when you can. Destructive modes wipe the target disk—dual-boot with other OSes is not a supported goal.

## Examples

Minimal GPT layout (ESP + root), adapted from the upstream README:

```nix
{
  disko.devices = {
    disk = {
      main = {
        device = "/dev/sda";
        type = "disk";
        content = {
          type = "gpt";
          partitions = {
            ESP = {
              type = "EF00";
              size = "500M";
              content = {
                type = "filesystem";
                format = "vfat";
                mountpoint = "/boot";
                mountOptions = [ "umask=0077" ];
              };
            };
            root = {
              size = "100%";
              content = {
                type = "filesystem";
                format = "ext4";
                mountpoint = "/";
              };
            };
          };
        };
      };
    };
  };
}
```

Partition, format, and mount from an installer (destructive):

```bash
sudo nix --experimental-features "nix-command flakes" \
  run github:nix-community/disko/latest -- \
  --mode destroy,format,mount /tmp/disk-config.nix
```

Flake input (recommended module install):

```nix
{
  inputs.disko.url = "github:nix-community/disko/latest";
  inputs.disko.inputs.nixpkgs.follows = "nixpkgs";
  # … then: modules = [ disko.nixosModules.disko … ];
}
```

## See also

- [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md)
- [Partitioning and bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md)
- [Disko recipes](../09-nixos/configuration/disko-recipes.md)
- [hardware-configuration.nix](../09-nixos/configuration/hardware-configuration.md)
- [Manual install](../09-nixos/installation/manual-install.md)

## References

- [nix-community/disko](https://github.com/nix-community/disko)
- [Quickstart](https://github.com/nix-community/disko/blob/master/docs/quickstart.md)
- [HowTo (module install)](https://github.com/nix-community/disko/blob/master/docs/HowTo.md)
- [disko-install](https://github.com/nix-community/disko/blob/master/docs/disko-install.md)
- [disko-templates](https://github.com/nix-community/disko-templates)
