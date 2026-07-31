---
status: complete
---

# ZFS and Btrfs

## Overview

NixOS treats ZFS and Btrfs as ordinary `fileSystems` entries once the pool or volume exists. Layout and bootloaders stay in [partitioning and bootloaders](partitioning-and-bootloaders.md); declarative disk creation often uses [disko](../../12-deployment-and-infra/disko.md). Native ZFS/Btrfs encryption is **not** LUKS—TPM/measured-boot unlock paths aimed at LUKS (for example Lanzaboote’s measured boot guide) do not integrate filesystem-level encryption.

## Details

### ZFS

**hostId.** Enabling ZFS asserts that `networking.hostId` is set (eight hex characters). Without it, evaluation fails with a clear assertion.

**Enable and kernel.** Enable ZFS in `boot.supportedFilesystems` (and `boot.initrd.supportedFilesystems` for root pools). `fileSystems` entries with `fsType = "zfs"` drive pool import and mounts but do not replace that enable step. Userland tools default to `pkgs.zfs`; the kernel module comes from `boot.kernelPackages`. OpenZFS and the Linux kernel do not always move in lockstep—pick a kernel package whose ZFS module is not broken for your channel, and expect pairing to lag after kernel bumps.

**Mounts.** Prefer datasets with `mountpoint=legacy` and explicit `fileSystems."…" = { device = "pool/dataset"; fsType = "zfs"; … }` so NixOS/systemd owns the mounts and imports the pool. If you keep ZFS native mountpoints and still list them in `fileSystems`, community practice adds `options = [ "zfsutil" ]` (see the [NixOS Wiki ZFS](https://wiki.nixos.org/wiki/ZFS) page). For pools you manage only with ZFS commands (no `fileSystems` driving import), list them in `boot.zfs.extraPools`.

**Encryption at import.** `boot.zfs.requestEncryptionCredentials` is a bool or a list of dataset names (default `true`). When true, import requests keys/passwords for encrypted datasets; a list limits which datasets are unlocked. Root-pool keys can come from a prompt (`keylocation=prompt`) or a file (`keylocation=file://…`).

**Scrub.** `services.zfs.autoScrub.enable` schedules periodic `zpool scrub` (default interval `monthly`; optional `pools` list, else all pools).

**Hibernation.** Hibernation with ZFS is risky and poorly supported by OpenZFS. Unless `boot.zfs.unsafeAllowHibernation` is set, the module adds the `nohibernate` kernel parameter. Enabling hibernation while `boot.zfs.forceImportRoot` or `boot.zfs.forceImportAll` is on fails evaluation (data-corruption risk). Read current module docs and the wiki before enabling.

### Btrfs

Declare mounts with `fsType = "btrfs"` and mount `options` such as `subvol=…` (and usual performance/compression flags as needed). Multi-device or multi-subvolume layouts are still just `fileSystems` entries.

**Scrub.** `services.btrfs.autoScrub.enable` runs periodic `btrfs scrub`. Set `interval` (default `monthly`) and optionally `fileSystems` (paths). If enabled with an empty list and no btrfs mounts, the module asserts; otherwise it defaults to unique btrfs mount points from `fileSystems`.

### Encryption vs LUKS

Block-device LUKS unlock (`boot.initrd.luks.devices`, TPM enrollment via systemd-cryptenroll, Lanzaboote measured boot) is a different stack from ZFS native encryption or Btrfs native encryption. Lanzaboote’s measured-boot documentation states it does **not** support filesystem-level encryption integration for ZFS or Btrfs—you would wire that yourself. See [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md) for the LUKS-oriented path.

## Examples

Illustrative ZFS root dataset (legacy mountpoint) plus auto-scrub—not an install guide:

```nix
{
  networking.hostId = "8425e349"; # eight hex chars; invent your own

  boot.supportedFilesystems = [ "zfs" ];

  fileSystems."/" = {
    device = "rpool/root";
    fsType = "zfs";
  };

  services.zfs.autoScrub = {
    enable = true;
    interval = "monthly";
  };
}
```

Illustrative Btrfs with a subvolume and auto-scrub:

```nix
{
  fileSystems."/" = {
    device = "/dev/disk/by-uuid/00000000-0000-0000-0000-000000000001";
    fsType = "btrfs";
    options = [ "subvol=@" "compress=zstd" ];
  };

  services.btrfs.autoScrub = {
    enable = true;
    interval = "monthly";
    fileSystems = [ "/" ];
  };
}
```

## See also

- [Partitioning and bootloaders](partitioning-and-bootloaders.md) — `fileSystems`, ESP, LUKS block devices
- [disko](../../12-deployment-and-infra/disko.md) — declarative partition/filesystem layouts
- [Disko recipes](disko-recipes.md) — template layouts including ZFS impermanence
- [Impermanence](impermanence.md) — ephemeral root patterns often paired with Btrfs (or ZFS) persist volumes
- [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md) — LUKS Secure Boot path
- [TPM and measured boot](tpm-and-measured-boot.md) — LUKS/TPM measured boot; not FS-native encryption
- [hardware-configuration.nix](hardware-configuration.md) — generated mount facts

## References

- [nixpkgs `filesystems/zfs.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/tasks/filesystems/zfs.nix) — `boot.zfs.*`, `services.zfs.autoScrub`, hostId assertion
- [nixpkgs `filesystems/btrfs.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/tasks/filesystems/btrfs.nix) — `services.btrfs.autoScrub`
- [NixOS Wiki: ZFS](https://wiki.nixos.org/wiki/ZFS) — community patterns (`zfsutil`, install sketches, hibernation notes)
- [NixOS Wiki: Btrfs](https://wiki.nixos.org/wiki/Btrfs) — community Btrfs notes
- [Lanzaboote: enable measured boot](https://github.com/nix-community/lanzaboote/blob/master/docs/how-to-guides/enable-measured-boot.md) — no FS-level ZFS/Btrfs encryption integration
