---
status: complete
last-checked: 2026-08
---

# Disko recipes

## Overview

This page collects **layout patterns** for [disko](../../12-deployment-and-infra/disko.md)—common GPT, LUKS, and ZFS shapes you copy or start from templates. It does not replace the tool page: module import, `destroy`/`format`/`mount`, **disko-install**, and [nixos-anywhere](../installation/nixos-anywhere.md) wiring live there.

Official starters live in [disko-templates](https://github.com/nix-community/disko-templates). Init one into a flake, point `disko.devices.disk.*.device` at a stable path, then choose a [bootloader](partitioning-and-bootloaders.md) separately.

## Details

### When to use what

| Approach | Use when |
|----------|----------|
| **Template** (`disko-templates`) | Disk count and filesystem story match an official output (single ext4, LUKS root + ZFS data mirror, or ZFS wipe-root layout). Prefer this over inventing GPT types and nestings. |
| **Hand-roll / adapt** | Close to a template or a [disko `example/`](https://github.com/nix-community/disko/tree/master/example) file, but you need different sizes, encryption, pool names, or disk count. Start from the nearest config and edit—do not invent LUKS/ZFS nesting from memory. Upstream `example/` files are also regression tests and may include uncommon options; strip what you do not need. |
| **Manual install** ([manual install](../installation/manual-install.md)) | Dual-boot, one-off recovery, learning `parted`/`mkfs`, or you intentionally avoid declarative disk tooling. Disko’s destructive modes are not aimed at sharing a disk with another OS. |

After any declarative layout: still enable systemd-boot or GRUB in the NixOS config, and keep [hardware-configuration](hardware-configuration.md) for kernel modules/firmware (`nixos-generate-config --no-filesystems` when disko owns mounts).

### Current templates

Flake outputs as of 2026-08 (re-checked against `github:nix-community/disko-templates`; still three—refresh this table if upstream adds or renames):

| Template | Layout sketch |
|----------|----------------|
| `single-disk-ext4` | One disk, GPT: EF02 BIOS grub partition (1M), ESP vfat `/boot` (1G), ext4 `/` |
| `single-ext4-luks-and-double-zfs-mirror` | Disk `root`: ESP + LUKS→ext4 `/`; disks `data1`/`data2`: ZFS mirror pool `data` with encrypted dataset at `/data` |
| `zfs-impermanence` | One disk: ESP + ZFS pool `zroot`; datasets `local/{home,nix,persist,root}`; blank snapshot on `local/root` for erase-your-darlings style wipe |

No other official template outputs exist at check time—do not invent names.

### Device paths and ops pitfalls

**by-id mistakes.** Prefer `/dev/disk/by-id/…` (or another stable symlink) over `/dev/sda` / `/dev/nvme0n1`. Set the path on each disk entry the template expects (`disko.devices.disk.main.device`, or `root` / `data1` / `data2` for the hybrid). Enumerate with `ls -l /dev/disk/by-id` and `lsblk` before any destructive mode. Copy-pasting another machine’s by-id, picking a `-partN` symlink instead of the whole disk, or leaving the template’s placeholder device unchanged will format the wrong target.

**Template drift.** Output names and `disko-config.nix` contents can change upstream. Pin or re-read the template you init; after `nix flake init --template …`, treat the copied file as yours and diff against upstream when upgrading layouts. This page’s table is a snapshot, not a lock.

**`zfs-impermanence` ≠ impermanence module.** The template only creates pool/datasets (including `/persist` and a blankable root). Bind-mounts, `environment.persistence."…"`, and wipe-on-boot activation still require the [impermanence](impermanence.md) stack (or equivalent). Without that, you have a ZFS layout, not declared persistence.

**Bootloader still required.** Disko owns partitions and filesystems (and may wire some GRUB device hints); you still enable systemd-boot or GRUB under `boot.loader.*`. See [partitioning and bootloaders](partitioning-and-bootloaders.md).

**Destructive by design.** Modes that destroy/format wipe the target disks. Dual-boot with another OS is not a goal of these recipes.

### Boundaries (what this page is not)

- The [disko tool overview](../../12-deployment-and-infra/disko.md)—CLI, module API, and install integration.
- [Manual partitioning](../installation/manual-install.md) or live-ISO fdisk workflows.
- [ZFS and Btrfs](zfs-and-btrfs.md) filesystem tuning and native encryption deep dive.
- Full [impermanence](impermanence.md) module options and persist lists.

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

- [Disk and persistence](../../cheatsheets/disk-and-persistence.md) — layout / impermanence chooser
- [disko](../../12-deployment-and-infra/disko.md) — module, CLI modes, disko-install
- [Partitioning and bootloaders](partitioning-and-bootloaders.md)
- [ZFS and Btrfs](zfs-and-btrfs.md) — mounts, scrub, native encryption notes after layout
- [hardware-configuration.nix](hardware-configuration.md)
- [Impermanence](impermanence.md) — persistence module; pair with `zfs-impermanence` layout
- [Manual install](../installation/manual-install.md) — non-disko partition/format path
- [nixos-anywhere](../installation/nixos-anywhere.md)

## References

- [nix-community/disko](https://github.com/nix-community/disko)
- [disko Quickstart](https://github.com/nix-community/disko/blob/master/docs/quickstart.md) — templates vs `example/`, device adjustment, bootloader note
- [disko HowTo](https://github.com/nix-community/disko/blob/master/docs/HowTo.md) — module import; by-id device example
- [nix-community/disko-templates](https://github.com/nix-community/disko-templates)
