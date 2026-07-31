---
status: complete
---

# Manual Install

## Overview

Manual installation is the classic NixOS path: boot the live image, prepare disks yourself, mount the target under `/mnt`, run `nixos-generate-config`, edit `configuration.nix`, then `nixos-install`. It works on BIOS or UEFI; only partitioning, ESP mount points, and bootloader options differ.

**Which install path?**

| Your situation | Use |
|----------------|-----|
| Desktop, first install, want a guided UI | [Graphical installer](graphical-installer.md) |
| Minimal ISO, custom layouts, dual-boot, servers, or learning the stack | This page |
| Machine already on the network; install from your flake over SSH | [nixos-anywhere](nixos-anywhere.md) |

The graphical installer covers most desktop cases. Choose manual when you need full control of disks and [`configuration.nix`](../configuration/configuration-nix.md), when you booted a **minimal** (non-graphical) ISO, or when the graphical flow cannot express your layout (multi-boot, unusual encryption, ZFS/Btrfs recipes). For remote or repeatable automation, prefer nixos-anywhere instead of typing the same steps on a console.

Flake-based installs (declarative disk layouts, `nixosConfigurations.<name>`) are common post-install; the live ISO still uses the generate-config-under-`/mnt` workflow described here. After your first boot, see [nixosConfigurations](../../07-flakes/workflows/nixos-configurations.md) for flake wiring.

## Details

**Boot and shell.** Boot the NixOS installation image. On graphical images, open Terminal or Konsole. You are logged in as `nixos` with an empty password; escalate with `sudo -i`. Run `loadkeys` if you need another keyboard layout (for example `loadkeys de`). Networking must work before install—the live system fetches binaries from cache (`ip a` to check; use `nmtui` or manual `ip` if needed). `nixos-help` opens the NixOS manual in a browser.

**Partition, format, mount.** The installer does not partition for you. Create partitions, format them, and mount the root filesystem on `/mnt`. On UEFI, also mount the EFI System Partition (typically at `/mnt/boot`). On low-RAM machines, activate swap (`swapon`) before installing. Do not copy ad-hoc `parted`/`mkfs` recipes from memory—follow the [NixOS manual](https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual) and [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md) for layout and bootloader choices.

**Generate and edit config.** With the target mounted:

```bash
nixos-generate-config --root /mnt
```

This writes `/mnt/etc/nixos/configuration.nix` and `/mnt/etc/nixos/hardware-configuration.nix` (filesystem UUIDs and detected hardware from current mounts). Edit `configuration.nix`:

- **UEFI:** prefer `boot.loader.systemd-boot.enable = true` (often set automatically when booted in UEFI mode).
- **BIOS:** set `boot.loader.grub.device` to the install disk—required for GRUB.
- Add users, networking, and other options as needed—see [Users and groups](../configuration/users-and-groups.md) and [Hardware configuration](../configuration/hardware-configuration.md). Wi-Fi works on the live image but is not enabled by default in the generated config. Avoid hand-editing `hardware-configuration.nix`; re-running `nixos-generate-config` overwrites it.

**Install and reboot.** Run `nixos-install`. If it fails (bad config, network outage), fix `configuration.nix` and re-run. Set the root password when prompted (or pass `--no-root-passwd` for unattended installs). For a normal user declared in config, set that password before reboot:

```bash
nixos-enter --root /mnt -c 'passwd alice'
```

Then `reboot` into the installed system.

**Dual-boot.** With GRUB, `boot.loader.grub.useOSProber` can detect other OSes (notably Windows). For multi-Linux setups, systemd-boot is often preferred. Details: [Dual-boot and VMs](dual-boot-and-vms.md).

## Examples

Outline after root (and ESP, if UEFI) is mounted under `/mnt`:

```bash
sudo -i
loadkeys us                    # optional
nixos-generate-config --root /mnt
nano /mnt/etc/nixos/configuration.nix   # boot.loader, users, …
nixos-install                  # set root password when asked
reboot
```

Partition and format commands are omitted on purpose—see the manual and [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md).

## References

- [NixOS manual — Manual Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual)
- [NixOS manual — Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation)

## See also

- [Graphical installer](graphical-installer.md)
- [nixos-anywhere](nixos-anywhere.md)
- [Dual-boot and VMs](dual-boot-and-vms.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Hardware configuration](../configuration/hardware-configuration.md)
- [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)
- [Users and groups](../configuration/users-and-groups.md)
- [nixosConfigurations](../../07-flakes/workflows/nixos-configurations.md) — flake output after first install
