---
status: complete
last-checked: 2026-08
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

### When to use what

| Situation | Prefer | Skip / avoid if… |
|-----------|--------|------------------|
| Learning disks, dual-boot, or one-off layout by hand | [Manual partition](../09-nixos/configuration/partitioning-and-bootloaders.md) + [manual install](../09-nixos/installation/manual-install.md) | You want the same layout reused across machines |
| Local / USB installer; declarative disks then `nixos-install` | disko CLI (`--mode …`) then manual install steps | Remote-only host with no console |
| Local / workstation; partition + install in one flake step | **disko-install** | Host is only reachable over SSH |
| Fresh NixOS over SSH (kexec → disks → install) | [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) (runs a disko phase) | Day-2 config updates; dual-boot / partial-disk wipe |
| Repair: remount existing layout without wiping | disko `mount` (or disko-install mount mode) | You meant a full reinstall |

Chooser hub: [Install and bootstrap](../cheatsheets/install-and-bootstrap.md). Layout patterns: [Disko recipes](../09-nixos/configuration/disko-recipes.md).

### CLI modes

From the [reference](https://github.com/nix-community/disko/blob/master/docs/reference.md) (`-m` / `--mode`):

| Mode | Effect |
|------|--------|
| `destroy` | Unmount filesystems and destroy partition tables on the selected disks |
| `format` | Create partition tables, zpools, LVMs, raids, and filesystems if they do not exist yet |
| `mount` | Mount partitions at the root mountpoint (default `/mnt`) |
| `format,mount` | Format then mount |
| `destroy,format,mount` | All three in sequence (the usual wipe-and-install path; previously `--mode disko`) |

Default CLI mode is `mount` (less destructive). Automation can pass `--yes-wipe-all-disks` to skip the destroy safety check. **disko-install** fresh installs wipe/partition; its mount-only path repairs without destroying.

### Failure modes

| Symptom / risk | Likely cause | What to check |
|----------------|--------------|---------------|
| Wrong disk wiped or empty | `device` points at `/dev/sda` (or similar) that is not the intended drive | Prefer `/dev/disk/by-id/…`; confirm with `lsblk` before any destroy/format run |
| Other OS / dual-boot data gone | Destructive modes reformat the whole target disk | Upstream: dual-boot is not supported; do not point disko at a shared disk you need to keep |
| Installed system will not boot | Bootloader not enabled in NixOS config | Still set `boot.loader.systemd-boot.enable` or GRUB (disko does not replace that choice) |
| No `fileSystems` / boot options from layout | Flake never imported `disko.nixosModules.disko` (or equivalent `module.nix`) | Add the module to `nixosConfigurations` `modules` / `imports`; keep `disko.devices` in that system |
| Prompt / unlock fails after reboot (LUKS layout) | Disks formatted with LUKS but the installed config does not carry unlock-at-boot wiring from the module | Ensure the same `disko.devices` LUKS layout is in the installed flake with the module imported—not only a one-shot installer CLI run |
| Unexpected wipe | `--mode destroy,format,mount` (or destroy alone) on the wrong config | Default is `mount`; use destroy only when you intend to erase; dry-run / double-check devices first |

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
- [Disk and persistence](../cheatsheets/disk-and-persistence.md) — layout / impermanence chooser
- [Disko recipes](../09-nixos/configuration/disko-recipes.md)
- [hardware-configuration.nix](../09-nixos/configuration/hardware-configuration.md)
- [Manual install](../09-nixos/installation/manual-install.md)
- [Install and bootstrap](../cheatsheets/install-and-bootstrap.md)
- [Disko + impermanence host (worked example)](../16-configuration-examples/disko-impermanence-host.md)
- [nixos-anywhere bootstrap (worked example)](../16-configuration-examples/nixos-anywhere-bootstrap.md)

## References

- [nix-community/disko](https://github.com/nix-community/disko)
- [Quickstart](https://github.com/nix-community/disko/blob/master/docs/quickstart.md)
- [HowTo (module install)](https://github.com/nix-community/disko/blob/master/docs/HowTo.md)
- [disko-install](https://github.com/nix-community/disko/blob/master/docs/disko-install.md)
- [Reference (CLI modes)](https://github.com/nix-community/disko/blob/master/docs/reference.md)
- [disko-templates](https://github.com/nix-community/disko-templates)
