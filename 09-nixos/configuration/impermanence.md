---
status: complete
---

# Impermanence

## Overview

**Impermanence** is the practice of keeping an ephemeral root filesystem (tmpfs or wipe-on-boot) so undeclared state disappears at reboot, while declaring which paths must survive on a persistent volume. NixOS still needs durable `/boot` and `/nix`; a common layout adds a `/persist` (or `/persistent`) mount for everything else you keep.

The usual implementation is the community project [nix-community/impermanence](https://github.com/nix-community/impermanence)—not part of nixpkgs core. Its NixOS module exposes `environment.persistence."<persist-path>"`; option names and behavior can change, so treat the upstream README as the source of truth.

## Details

**What you need.** Three pieces: (1) a root that is cleared between boots, (2) at least one persistent volume for files you keep, and (3) the impermanence module to bind-mount or link those paths onto the ephemeral root. Layout of disks and bootloaders belongs in [partitioning and bootloaders](partitioning-and-bootloaders.md) and often [hardware-configuration](hardware-configuration.md); declarative disk tooling such as [disko](../../12-deployment-and-infra/disko.md) can create the partitions/subvolumes.

**Ephemeral root patterns.** Upstream documents tmpfs root (simple; memory-backed; size limits and crash loss) and Btrfs (or similar) wipe/recreate of the root subvolume at boot. Other filesystems and “erase your darlings” variants exist; pick one and keep `/nix` and `/boot` off the wiped tree.

**NixOS module.** Import via flake: `inputs.impermanence.url = "github:nix-community/impermanence"`, then `impermanence.nixosModules.impermanence` in `nixosConfigurations.*.modules`. The flake lists `nixpkgs` and `home-manager` as inputs for development; they are unused at runtime—set `impermanence.inputs.nixpkgs.follows = ""` and `impermanence.inputs.home-manager.follows = ""` if you want them out of `flake.lock`.

Under `environment.persistence."/persist"` (path is your persist mount), declare `directories` and `files` (strings or attribute sets with `user` / `group` / `mode`), optional nested `users.<name>.{directories,files}` for home paths, and flags such as `hideMounts`. Typical survivors from upstream examples: `/var/log`, selected `/var/lib/…`, `/etc/machine-id`, and user `.ssh` / `.gnupg` with mode `0700`. Undeclared paths disappear at reboot; declared ones are bind-mounted or linked from the persist volume.

**Home Manager.** `home.persistence` mirrors the NixOS shape under `home`. When Home Manager is used as a NixOS module, importing the NixOS impermanence module loads HM persistence automatically. Standalone-only Home Manager is awkward for this stack—upstream expects the NixOS HM module plus the NixOS impermanence module. See [standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md).

**Sharp edges.** Upstream requires marking persistent and ephemeral storage volumes `neededForBoot` (early mounts and paths such as `/etc/machine-id` otherwise race initrd ordering). Secrets that must survive reboot belong on the persist volume (or decrypt into `/run` after boot)—see [secrets strategies](secrets-strategies.md). Option details beyond this page: follow the README.

## Examples

Minimal flake wiring and a small persistence set (host/paths invented; option names match the upstream README; not evaluated offline):

```nix
{
  inputs.impermanence.url = "github:nix-community/impermanence";
  inputs.impermanence.inputs.nixpkgs.follows = "";
  inputs.impermanence.inputs.home-manager.follows = "";

  outputs = { nixpkgs, impermanence, ... }: {
    nixosConfigurations.box = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        impermanence.nixosModules.impermanence
        ({ ... }: {
          environment.persistence."/persist" = {
            hideMounts = true;
            directories = [
              "/var/log"
              "/var/lib/nixos"
              { directory = "/var/lib/bluetooth"; mode = "0700"; }
            ];
            files = [ "/etc/machine-id" ];
            users.alice = {
              directories = [
                { directory = ".ssh"; mode = "0700"; }
                { directory = ".gnupg"; mode = "0700"; }
              ];
            };
          };
        })
      ];
    };
  };
}
```

## See also

- [Partitioning and bootloaders](partitioning-and-bootloaders.md)
- [Hardware configuration](hardware-configuration.md)
- [Secrets strategies](secrets-strategies.md)
- [disko](../../12-deployment-and-infra/disko.md)
- [Disko recipes](disko-recipes.md)
- [Home Manager: standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md)
- [Generations and boot](../architecture/generations-and-boot.md)

## References

- [nix-community/impermanence](https://github.com/nix-community/impermanence) — community project
- [impermanence README](https://github.com/nix-community/impermanence/blob/master/README.org) — modules, options, system-setup patterns (source of truth)
- [NixOS Wiki: Impermanence](https://wiki.nixos.org/wiki/Impermanence) — community patterns (secondary)
