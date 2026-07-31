---
status: complete
---

# Dual Boot and VMs

## Overview

NixOS can share a disk with another OS, or run entirely as a guest / test VM. Dual-boot means leaving existing partitions alone, installing into free space, and wiring the boot loader so both systems remain reachable. Virtual machines cover two common paths: a full guest install (for example VirtualBox) and `nixos-rebuild build-vm`, which boots your configuration in QEMU without touching bare metal. Install flows: [Graphical installer](graphical-installer.md), [Manual install](manual-install.md). Boot and partition options: [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md).

## Details

### Dual boot

**Leave other OS partitions intact.** Shrink or use free space for NixOS root (and swap if needed). Do not format the other system's partitions unless you intend to erase them. Point `fileSystems` only at the mounts NixOS owns; `nixos-generate-config` fills this from what you mounted under `/mnt` during install.

**UEFI boot loaders.** Prefer **systemd-boot** (`boot.loader.systemd-boot.enable = true`); `nixos-generate-config` usually enables it when the installer itself booted in UEFI. GRUB on UEFI is also fine: set `boot.loader.grub.efiSupport = true` and `boot.loader.grub.device = "nodev"` (the ESP holds the EFI binary; you do not install GRUB to a whole-disk device the BIOS way). Both systemd-boot and GRUB expect the EFI System Partition at `/boot` by default—align mounts with that or adjust `boot.loader.efi` / mount points. Details: [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md). Generations appear as separate boot entries: [Generations and boot](../architecture/generations-and-boot.md).

**Finding other operating systems.**

| Boot loader | Other OSes |
|-------------|------------|
| systemd-boot | Usually no special option; firmware/ESP entries for other systems remain available |
| GRUB | `boot.loader.grub.useOSProber = true` can add entries; the manual notes this mainly detects **Windows**, not other Linux installs |

For dual-booting **another Linux** distribution, the install chapter recommends systemd-boot over relying on os-prober.

**BIOS.** Set `boot.loader.grub.device` to the disk that should receive GRUB (for example `"/dev/sda"`). `useOSProber` can still add other OS menu entries when GRUB is the chain.

**Secure Boot.** The installer chapter notes you will often need to **disable Secure Boot** in firmware to boot the NixOS ISO or finish boot-loader setup. Exact menus vary by vendor (Boot / Security / Advanced).

### Virtual machines

**VirtualBox guest.** The NixOS manual has a dedicated “Installing in a VirtualBox guest” walkthrough: create a Linux VM, mount the ISO, enable PAE/NX and VT-x/AMD-V, use VMSVGA, then install as usual. Guest config typically sets `boot.loader.grub.device` (for example `"/dev/sda"`), may disable `boot.initrd.checkJournalingFS` (journal fsck can hang the guest), and can mount VirtualBox shared folders via `vboxsf` with `"nofail"` so a missing share does not block boot.

**`nixos-rebuild build-vm`.** Builds a QEMU VM from the current NixOS configuration so you can exercise options without installing or switching on the host. Related rebuild modes: [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md).

- The VM disk has **no host home or account data**. Host users are not present unless you declare them for the VM (for example `users.mutableUsers = false` with declarative passwords/keys, or a temporary `users.users.<name>.initialHashedPassword`).
- After a wrong first boot (missing users/passwords), **delete `$hostname.qcow2`** so the next run recreates the disk; otherwise password and user changes may not apply.
- Forward host ports into the guest with `QEMU_NET_OPTS` (for example SSH on host `2222` → guest `22`). Forwarding uses the guest’s virtual NIC, not loopback-only binds; open the guest firewall for those ports.

## Examples

UEFI dual-boot with systemd-boot (shape only):

```nix
{
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  # fileSystems."/" and fileSystems."/boot" from nixos-generate-config
}
```

UEFI GRUB plus Windows via os-prober:

```nix
{
  boot.loader.grub.enable = true;
  boot.loader.grub.device = "nodev";
  boot.loader.grub.efiSupport = true;
  boot.loader.grub.useOSProber = true;
}
```

Build and run a config in QEMU, then SSH via forwarded port:

```bash
nixos-rebuild build-vm
./result/bin/run-*-vm

# After fixing users/passwords in config, remove stale disk if needed:
# rm -f ./hostname.qcow2

QEMU_NET_OPTS="hostfwd=tcp:127.0.0.1:2222-:22" ./result/bin/run-*-vm
ssh -p 2222 localhost
```

Temporary hashed password for VM login (replace user and hash; generate with `mkpasswd`):

```nix
{ users.users.your-user.initialHashedPassword = "..."; }
```

## References

- [NixOS manual — Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation) — dual boot, Secure Boot, boot loaders, VirtualBox guest (stable / 26.05 as of 2026-07)
- [NixOS manual — Changing the Configuration (`build-vm`)](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config) — QEMU test VM, `qcow2`, `QEMU_NET_OPTS`

## See also

- [Graphical installer](graphical-installer.md)
- [Manual install](manual-install.md)
- [Netboot and PXE](netboot-and-pxe.md) — PXE/iPXE installer media
- [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)
- [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md)
- [Libvirt and VMs](../services/libvirt-and-vms.md) — persistent host hypervisor
- [MicroVMs](../services/microvms.md) — declarative lightweight NixOS guests
- [Generations and boot](../architecture/generations-and-boot.md)
