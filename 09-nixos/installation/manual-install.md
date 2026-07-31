---
status: complete
---

# Manual Install

## Overview

Manual installation is the NixOS workflow where you partition, format, and mount the target yourself, generate a config under `/mnt`, edit it, then run `nixos-install`. It works on BIOS or UEFI; the steps are the same except where boot partitions and bootloaders differ.

For most desktop installs, prefer the [Graphical installer](graphical-installer.md). Use this page when you want full control of disks and [`configuration.nix`](../configuration/configuration-nix.md), or when booting a minimal (non-graphical) ISO. For remote/automation, see [nixos-anywhere](nixos-anywhere.md).

## Details

**Boot and shell.** Boot the NixOS installation image. On graphical images, open a Terminal (or Konsole). You are auto-logged in as `nixos` with an empty password; escalate with `sudo -i`. Run `loadkeys` if you need a different keyboard layout (for example `loadkeys de`). Networking should already be up (`ip a`); use `nmtui` or manual `ip` if not—the installer needs network access to fetch binaries. The live system also provides `nixos-help` for the NixOS manual.

**Partition, format, mount.** The installer does not partition for you. Create partitions, format them, and mount the target root on `/mnt`. On UEFI, also mount the ESP (typically at `/mnt/boot`). On low-RAM machines, activate swap (`swapon`) before installing. Partition schemes and bootloader choices are covered in [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md); follow the [NixOS manual](https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual) for concrete `parted` / `mkfs` examples rather than inventing layouts here.

**Generate and edit config.** With the target mounted:

```bash
# nixos-generate-config --root /mnt
```

This writes `/mnt/etc/nixos/configuration.nix` and `/mnt/etc/nixos/hardware-configuration.nix` (filesystems and hardware detected from the current mounts). Edit `configuration.nix`:

- **UEFI:** prefer `boot.loader.systemd-boot.enable = true` (`nixos-generate-config` usually sets this when booted in UEFI mode).
- **BIOS:** set `boot.loader.grub.device` to the install disk (required for GRUB).
- Users, networking, and other options as needed—see [Users and groups](../configuration/users-and-groups.md) and [Hardware configuration](../configuration/hardware-configuration.md). Wi-Fi works on the live image but is not enabled by default in the generated config. Avoid hand-editing `hardware-configuration.nix`; regenerating overwrites it.

**Install and reboot.** Run `nixos-install`. If it fails (bad config, network outage, and so on), fix `configuration.nix` and re-run. Set the root password when prompted (or use `--no-root-passwd` for unattended installs). If you declared a normal user, set that user’s password before reboot:

```bash
# nixos-enter --root /mnt -c 'passwd alice'
```

Then `reboot` into the installed system.

**Dual-boot.** With GRUB, `boot.loader.grub.useOSProber` can pick up other OSes (notably Windows). For multi-Linux setups, systemd-boot is preferred. Details: [Dual-boot and VMs](dual-boot-and-vms.md).

## Examples

Outline after the target root (and ESP, if UEFI) is already mounted under `/mnt`:

```bash
# sudo -i
# loadkeys us                    # optional
# nixos-generate-config --root /mnt
# nano /mnt/etc/nixos/configuration.nix   # boot.loader, users, …
# nixos-install                  # set root password when asked
# reboot
```

Partition/format commands are omitted on purpose—see the manual and [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md).

## References

- [NixOS manual — Manual Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual)
- [NixOS manual — Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation)

## See also

- [Graphical installer](graphical-installer.md)
- [Dual-boot and VMs](dual-boot-and-vms.md)
- [nixos-anywhere](nixos-anywhere.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Hardware configuration](../configuration/hardware-configuration.md)
- [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)
- [Users and groups](../configuration/users-and-groups.md)
