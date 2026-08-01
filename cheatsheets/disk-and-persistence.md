---
status: complete
---

# Disk and persistence

Three separate concerns: **declare disks** (partitions / `fileSystems` / disko), **wipe root** (impermanence / erase-your-darlings), and **bootloader** (`boot.loader.*`—not owned by disko). Fresh layout ≠ day-2 FS tuning. Bootstrap chooser: [Install and bootstrap](install-and-bootstrap.md).

## Decision table

| Situation | Prefer | Leaf | Avoid if… |
|-----------|--------|------|-----------|
| Desktop at the machine; stock erase-disk layout | Guided ISO (Calamares) | [Graphical installer](../09-nixos/installation/graphical-installer.md) · [Install and bootstrap](install-and-bootstrap.md) | Custom GPT/LUKS/ZFS, dual-boot, or flake-first disko |
| Console / minimal ISO; learn fdisk → `/mnt` → install | Manual partition + `nixos-generate-config` | [Manual install](../09-nixos/installation/manual-install.md) | You want the layout in Nix and reusable across hosts |
| Declarative disks in config; apply from installer | **disko** (`destroy,format,mount` then install) | [disko](../12-deployment-and-infra/disko.md) | Sharing the disk with another OS; wrong `/dev/disk/by-id/…` |
| Local / boot media: partition + `nixos-install` in one step | **disko-install** | [disko](../12-deployment-and-infra/disko.md) | Remote-only host (use nixos-anywhere); dual-boot (destructive wipe) |
| Need a starter GPT / LUKS / ZFS-impermanence layout | **disko-templates** / recipe patterns | [Disko recipes](../09-nixos/configuration/disko-recipes.md) | Expecting bootloader or impermanence bind-mounts from the template alone (`zfs-impermanence` ≠ the module) |
| Pool/subvol knobs, scrub, native encryption vs LUKS | ZFS / Btrfs modules after layout exists | [ZFS and Btrfs](../09-nixos/configuration/zfs-and-btrfs.md) | Still choosing partitions—finish disko / manual layout first |
| Ephemeral root; declare survivors on `/persist` (or `/persistent`) | **impermanence** module + durable `/nix` `/boot` | [Impermanence](../09-nixos/configuration/impermanence.md) | Secrets / decrypt keys left only on wiped root; layout template alone without the module |
| Share disk with Windows / another Linux | Careful manual or shared-ESP dual-boot path | [Dual boot and VMs](../09-nixos/installation/dual-boot-and-vms.md) · [Partitioning and bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md) | disko destructive modes aimed at whole-disk wipe |
| Fresh NixOS over SSH (kexec → disko → flake) | **nixos-anywhere** | [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) | Day-2 updates; keeping an existing foreign OS on the target disk |

disko owns mounts → generate hardware with `nixos-generate-config --no-filesystems`: [hardware-configuration](../09-nixos/configuration/hardware-configuration.md). Persist decrypt identities: [Secrets strategies](../09-nixos/configuration/secrets-strategies.md).

## Failure callouts

| Symptom / mistake | Fix |
|-------------------|-----|
| Wrong `/dev/disk/by-id/…` (or `/dev/sdX`) + destroy/format | Verify `ls -l /dev/disk/by-id` before any destructive disko mode; wrong device = wiped data ([disko](../12-deployment-and-infra/disko.md) · [recipes](../09-nixos/configuration/disko-recipes.md)) |
| Dual-boot + disko destructive layout | Dual-boot is not a disko goal—use [manual](../09-nixos/installation/manual-install.md) / [dual-boot](../09-nixos/installation/dual-boot-and-vms.md) paths that leave the other OS intact |
| Forgot `neededForBoot` on persist / ephemeral volumes | Mark persistent **and** ephemeral storage volumes `neededForBoot` so early bind/link (e.g. `/etc/machine-id`) works—[Impermanence](../09-nixos/configuration/impermanence.md) |
| `zfs-impermanence` (or other template) but state still vanishes / no bind-mounts | Template only creates pool/datasets; wire [impermanence](../09-nixos/configuration/impermanence.md) (`environment.persistence."…"`) or equivalent—[Disko recipes](../09-nixos/configuration/disko-recipes.md) |
| Secrets or age/SSH decrypt keys only on ephemeral root | Keep identities + ciphertext on the persist volume; decrypt into `/run`—[Secrets strategies](../09-nixos/configuration/secrets-strategies.md) |
| Disks mounted but no bootloader enabled | disko ≠ bootloader—set `boot.loader.systemd-boot.enable` or `boot.loader.grub.enable` ([Partitioning and bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md)) |

## See also

- [Install and bootstrap](install-and-bootstrap.md)
- [disko](../12-deployment-and-infra/disko.md)
- [Disko recipes](../09-nixos/configuration/disko-recipes.md)
- [Impermanence](../09-nixos/configuration/impermanence.md)
- [Partitioning and bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md)
- [Disko + impermanence host (worked example)](../16-configuration-examples/disko-impermanence-host.md)

## References

- [nix-community/disko](https://github.com/nix-community/disko) — declarative disks; modes; **disko-install**
- [disko Reference (CLI modes)](https://github.com/nix-community/disko/blob/master/docs/reference.md) — `destroy` / `format` / `mount`
- [disko-templates](https://github.com/nix-community/disko-templates) — flake init layouts
- [impermanence README](https://github.com/nix-community/impermanence/blob/master/README.org) — modules, options, system-setup patterns
