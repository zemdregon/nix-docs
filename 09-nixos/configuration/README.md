---
status: index
---

# NixOS Configuration

Authoring system configuration.

## Contents

- [configuration.nix](configuration-nix.md) — Main system configuration
- [hardware-configuration.nix](hardware-configuration.md) — Hardware scan output
- [Imports and Profiles](imports-and-profiles.md) — Modular config layout
- [Networking](networking.md) — Network options
- [Overlay networks](overlay-networks.md) — VPN/overlay fabric for builders, deploy, private caches
- [Users and Groups](users-and-groups.md) — User management
- [Enterprise identity](enterprise-identity.md) — LDAP / AD / SSSD patterns on NixOS
- [Secrets Strategies](secrets-strategies.md) — Handling secrets on NixOS

- [Partitioning and Bootloaders](partitioning-and-bootloaders.md) — Disk and bootloader setup
- [Impermanence](impermanence.md) — Ephemeral root with declared persistence
- [Secure Boot and Lanzaboote](secure-boot-and-lanzaboote.md) — UEFI Secure Boot via Lanzaboote
- [TPM and measured boot](tpm-and-measured-boot.md) — TPM PCR policy unlock (Lanzaboote / Clevis notes)
- [nixos-hardware](nixos-hardware.md) — Hardware quirk profiles for common machines
- [Firmware and microcode](firmware-and-microcode.md) — Redistributable firmware and CPU microcode
- [ZFS and Btrfs](zfs-and-btrfs.md) — Declarative mounts, scrub, native encryption notes
- [Disko recipes](disko-recipes.md) — Common disko layout patterns and templates
- [Specialisations](specialisations.md) — Extra boot/runtime system variants in one generation
