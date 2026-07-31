---
status: complete
---

# Disko recipes

## Overview

This page collects **layout patterns** for [disko](../../12-deployment-and-infra/disko.md)—common GPT, LUKS, and ZFS shapes you copy or start from templates. It does not replace the tool page: module import, `destroy`/`format`/`mount`, **disko-install**, and [nixos-anywhere](../installation/nixos-anywhere.md) wiring live there.

Official starters live in [disko-templates](https://github.com/nix-community/disko-templates). Init one into a flake, point `disko.devices.disk.*.device` at a stable path, then choose a [bootloader](partitioning-and-bootloaders.md) separately.

## Details

**Templates vs hand-rolled.** Prefer a template when it matches your disk count and filesystem story; adapt `disko-config.nix` rather than inventing GPT types and nestings from scratch. The tool page covers how the NixOS module turns `disko.devices` into `fileSystems`; this page only names layouts.

**Current templates** (flake outputs as of 2026-07-30; check upstream if names drift):

| Template | Layout sketch |
|----------|----------------|
| `single-disk-ext4` | One disk, GPT: optional EF02 BIOS grub partition, ESP (vfat `/boot`), ext4 `/` |
| `single-ext4-luks-and-double-zfs-mirror` | Root on ext4 + LUKS; separate ZFS mirror raid for data |
| `zfs-impermanence` | Pool `zroot`; datasets under `local/{home,nix,persist,root}`; blank-snapshot / erase-your-darlings style root |

**Device paths.** Prefer `/dev/disk/by-id/…` (or another stable symlink) over `/dev/sda`. Set the path on each disk entry, e.g. `disko.devices.disk.main.device`. Wrong device + destructive mode means wiped data.

**Bootloader is separate.** Disko owns partitions and filesystems; you still enable systemd-boot or GRUB in the NixOS config. See [partitioning and bootloaders](partitioning-and-bootloaders.md). Pair with [hardware-configuration](hardware-configuration.md) for kernel modules and firmware (`nixos-generate-config --no-filesystems` when disko owns mounts).

**Impermanence.** The `zfs-impermanence` template is a disk layout for wipe-on-boot roots; persistence bind-mounts and module options belong on [Impermanence](impermanence.md).

**Destructive by design.** Modes that destroy/format wipe the target disks. Dual-boot with another OS is not a goal of these recipes.

## Examples

Init a template, then import its `disko-config.nix` into the host (after wiring the disko module—see the [disko](../../12-deployment-and-infra/disko.md) page):

```bash
nix flake init --template github:nix-community/disko-templates#single-disk-ext4
```

Minimal GPT ESP + root fragment (illustrative; invented by-id path):

```nix
{
  disko.devices.disk.main = {
    device = "/dev/disk/by-id/nvme-ACME_EXAMPLE_001";
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
}
```

For LUKS+ZFS hybrid or ZFS impermanence dataset trees, start from the matching template instead of expanding this snippet.

## See also

- [disko](../../12-deployment-and-infra/disko.md) — module, CLI modes, disko-install
- [Partitioning and bootloaders](partitioning-and-bootloaders.md)
- [ZFS and Btrfs](zfs-and-btrfs.md) — mounts, scrub, native encryption notes after layout
- [hardware-configuration.nix](hardware-configuration.md)
- [Impermanence](impermanence.md)
- [nixos-anywhere](../installation/nixos-anywhere.md)

## References

- [nix-community/disko](https://github.com/nix-community/disko)
- [nix-community/disko-templates](https://github.com/nix-community/disko-templates)
