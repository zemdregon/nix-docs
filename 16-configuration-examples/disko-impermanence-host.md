---
status: complete
last-checked: 2026-08
---

# Disko + impermanence host

## Overview

This walkthrough wires one NixOS host through a flake with **declarative disks** ([disko](../12-deployment-and-infra/disko.md)) and an **ephemeral root** plus declared survivors ([impermanence](../09-nixos/configuration/impermanence.md)). It is a **file-layout story** for GPT + durable `/boot` and `/nix`, ext4 `/persist`, tmpfs `/`, and the impermanence bind-mount list—not a full ZFS erase-your-darlings template. For that layout, start from [Disko recipes](../09-nixos/configuration/disko-recipes.md) (`zfs-impermanence`) and still add the impermanence module yourself.

It is **not** dual-boot safe: disko destructive modes wipe the target disk. It is **not** a secrets tutorial—only enough wiring to keep decrypt identities and host keys on `/persist`. Pins like `nixos-26.05` and `x86_64-linux` are illustrative; replace device paths and persist lists before bare metal.

## Details

### What you get

One repository with a flake, a disko layout module, host policy, and a hardware stub without `fileSystems` (disko owns mounts). After install, undeclared paths under `/` vanish at reboot; paths listed under `environment.persistence."/persist"` bind back from the ext4 volume. Durable `/boot` and `/nix` stay off the wiped tree.

### Domains composed

This example pulls together teaching pages from several domains:

- [disko](../12-deployment-and-infra/disko.md) — `disko.devices`, module import, CLI / **disko-install** paths
- [Impermanence](../09-nixos/configuration/impermanence.md) — `environment.persistence."…"`, `neededForBoot`, survivor lists
- [Disko recipes](../09-nixos/configuration/disko-recipes.md) — official templates including `zfs-impermanence` (ZFS layout only; bind-mounts still need impermanence)
- [Disk and persistence](../cheatsheets/disk-and-persistence.md) — chooser: disko vs manual vs impermanence
- [hardware-configuration.nix](../09-nixos/configuration/hardware-configuration.md) — kernel modules and platform; generate with `--no-filesystems` when disko owns mounts
- [Partitioning and bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md) — disko does **not** replace bootloader choice
- [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) — `nixosSystem`, `specialArgs`, multiple inputs
- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md) — keep age/SSH decrypt identities on persist, not only on ephemeral `/`
- [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md) — required for this workflow

### File layout

```
.
├── flake.nix
├── flake.lock                         # after nix flake lock
├── hosts/
│   └── ephemeral/
│       ├── default.nix                # bootloader, impermanence, host policy
│       └── disko.nix                  # disko.devices (GPT + tmpfs root)
└── hardware-configuration.nix         # from nixos-generate-config --no-filesystems
```

On a real install, run `nixos-generate-config --no-filesystems` on the target and replace the stub below. Set `disko.devices.disk.main.device` to a stable `/dev/disk/by-id/…` path from `ls -l /dev/disk/by-id`—not `/dev/sda`.

### Annotated pieces

**`flake.nix`** — pin `nixpkgs`, `disko`, and `impermanence`; import both NixOS modules. Platform comes from `nixpkgs.hostPlatform` in the hardware stub (not a top-level `system` argument). Pins are illustrative (`nixos-26.05`):

```nix
{
  description = "Ephemeral-root NixOS host (disko + impermanence)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    disko.url = "github:nix-community/disko/latest";
    disko.inputs.nixpkgs.follows = "nixpkgs";
    impermanence.url = "github:nix-community/impermanence";
    # Dev-only inputs; unused at runtime — see impermanence README
    impermanence.inputs.nixpkgs.follows = "";
    impermanence.inputs.home-manager.follows = "";
  };

  outputs = { self, nixpkgs, disko, impermanence, ... }@inputs: {
    nixosConfigurations.ephemeral = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [
        disko.nixosModules.disko
        impermanence.nixosModules.impermanence
        ./hardware-configuration.nix
        ./hosts/ephemeral
      ];
    };
  };
}
```

**`hosts/ephemeral/disko.nix`** — GPT ESP + ext4 `/nix` and `/persist`, tmpfs `/` (adapted from upstream `example/hybrid-tmpfs-on-root.nix`: EF02 BIOS grub partition dropped for systemd-boot-only UEFI; dedicated `/persist` partition added; sizes and by-id path are placeholders). `size=25%` matches the impermanence README tmpfs sketch:

```nix
{
  disko.devices = {
    disk.main = {
      device = "/dev/disk/by-id/nvme-REPLACE_WITH_YOUR_DISK";
      type = "disk";
      content = {
        type = "gpt";
        partitions = {
          ESP = {
            size = "512M";
            type = "EF00";
            content = {
              type = "filesystem";
              format = "vfat";
              mountpoint = "/boot";
              mountOptions = [ "umask=0077" ];
            };
          };
          nix = {
            size = "200G";
            content = {
              type = "filesystem";
              format = "ext4";
              mountpoint = "/nix";
            };
          };
          persist = {
            size = "100%";
            content = {
              type = "filesystem";
              format = "ext4";
              mountpoint = "/persist";
            };
          };
        };
      };
    };
    nodev."/" = {
      fsType = "tmpfs";
      mountOptions = [ "size=25%" "defaults" "mode=755" ];
    };
  };
}
```

**`hosts/ephemeral/default.nix`** — imports disko layout, enables bootloader, marks early mounts, declares persistence. Declare any `environment.persistence.*.users.<name>` account under `users.users` as well:

```nix
{ config, pkgs, ... }: {
  imports = [ ./disko.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "ephemeral";
  system.stateVersion = "26.05";

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };

  # Upstream: mark persistent AND ephemeral root neededForBoot for early binds.
  fileSystems."/persist".neededForBoot = true;
  fileSystems."/".neededForBoot = true;

  environment.persistence."/persist" = {
    hideMounts = true;
    directories = [
      "/var/log"
      "/var/lib/nixos"
      "/etc/ssh"   # host keys for SSH + age recipients — see secrets-strategies
    ];
    files = [ "/etc/machine-id" ];
    users.alice = {
      directories = [
        { directory = ".ssh"; mode = "0700"; }
        { directory = ".gnupg"; mode = "0700"; }
      ];
    };
  };
}
```

**`hardware-configuration.nix` (stub)** — no `fileSystems` block; disko supplies mounts:

```nix
{ config, lib, pkgs, modulesPath, ... }: {
  imports = [ (modulesPath + "/installer/scan/not-detected.nix") ];

  boot.initrd.availableKernelModules = [ "xhci_pci" "nvme" "usb_storage" ];
  nixpkgs.hostPlatform = lib.mkDefault "x86_64-linux";
}
```

For a ZFS wipe-root layout instead of tmpfs, use the official `zfs-impermanence` template from [disko-templates](https://github.com/nix-community/disko-templates) and the notes in [Disko recipes](../09-nixos/configuration/disko-recipes.md)—the impermanence module is still required for bind-mounts.

### Activate / verify

Evaluate from the repo root (experimental features enabled once per machine):

```bash
# nix.conf or --extra-experimental-features 'nix-command flakes'
nix flake lock
nix flake check
nix build .#nixosConfigurations.ephemeral.config.system.build.toplevel
```

On a **fresh** machine from a NixOS ISO, partition and install with disko (destructive—confirm the by-id device first):

```bash
# Partition + mount to /mnt, then nixos-install separately:
sudo nix run github:nix-community/disko/latest -- \
  --mode destroy,format,mount ./hosts/ephemeral/disko.nix

# Or one step: disko-install with your flake output (see upstream disko-install docs)
# nix run github:nix-community/disko/latest#disko-install -- \
#   --flake .#ephemeral --disk main /dev/disk/by-id/…
```

After install, switch day-2 config with `sudo nixos-rebuild switch --flake .#ephemeral`. Regenerate hardware facts with `nixos-generate-config --no-filesystems` if modules or initrd need updating.

### Failure modes

| Symptom | Likely cause |
|---------|----------------|
| Wrong disk wiped or empty | `device` still `/dev/sda` or a copied by-id from another machine—use `/dev/disk/by-id/…` and `lsblk` before destroy/format |
| `/etc/machine-id` or early binds missing at boot | Persist or tmpfs `/` not marked `neededForBoot` |
| sops/agenix decrypt fails every reboot | Decrypt identities, host SSH keys, or ciphertext paths lived only on ephemeral `/`—persist them per [Secrets strategies](../09-nixos/configuration/secrets-strategies.md) |
| Installed system will not boot | Forgot `boot.loader.systemd-boot.enable` (or GRUB)—disko does not choose the bootloader |
| Service data gone after reboot | Path not listed under `environment.persistence."/persist"`—undeclared state is intentional loss |
| Dual-boot data lost | Destructive disko modes target whole disks; dual-boot is not a supported goal |
| Eval OK, install VM OOM | Very large `/nix/store` copied onto tmpfs during install—keep `/nix` on a real partition (as above) |

## Examples

Illustrative end-to-end picture (not evaluated offline: needs a disk, ISO or lab VM, and real by-id paths). Assemble the [File layout](#file-layout) files (`flake.nix`, `hosts/ephemeral/disko.nix`, `hosts/ephemeral/default.nix`, hardware stub without filesystems), then on a lab machine:

```bash
nix flake lock
nix flake check
nix build .#nixosConfigurations.ephemeral.config.system.build.toplevel

# From NixOS ISO — replace by-id before running:
sudo nix run github:nix-community/disko/latest -- \
  --mode destroy,format,mount ./hosts/ephemeral/disko.nix
sudo nixos-install --flake .#ephemeral
sudo nixos-rebuild switch --flake .#ephemeral
```

Match the `nixosConfigurations` key, `networking.hostName`, and the `#` suffix (`ephemeral` here). Undeclared files under `/` disappear after reboot; declared paths under `/persist` survive via impermanence bind-mounts.

## References

- [nix-community/disko](https://github.com/nix-community/disko)
- [disko HowTo (module install)](https://github.com/nix-community/disko/blob/master/docs/HowTo.md)
- [disko-install](https://github.com/nix-community/disko/blob/master/docs/disko-install.md)
- [hybrid-tmpfs-on-root.nix](https://github.com/nix-community/disko/blob/master/example/hybrid-tmpfs-on-root.nix) — upstream shape this layout adapts
- [nix-community/impermanence](https://github.com/nix-community/impermanence)
- [impermanence README](https://github.com/nix-community/impermanence/blob/master/README.org) — `environment.persistence`, `neededForBoot`, tmpfs sketch
- [nix-community/disko-templates](https://github.com/nix-community/disko-templates) — including `zfs-impermanence` (layout only)

## See also

- [disko](../12-deployment-and-infra/disko.md)
- [Impermanence](../09-nixos/configuration/impermanence.md)
- [Disko recipes](../09-nixos/configuration/disko-recipes.md)
- [Disk and persistence](../cheatsheets/disk-and-persistence.md)
- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md)
- [Minimal flake NixOS host](minimal-flake-nixos-host.md) — slimmer single-host flake without disko/impermanence
- [nixos-anywhere bootstrap](nixos-anywhere-bootstrap.md) — remote wipe-and-install of a disko flake
