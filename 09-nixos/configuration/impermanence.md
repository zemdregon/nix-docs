---
status: complete
last-checked: 2026-08
---

# Impermanence

## Overview

**Impermanence** is the practice of keeping an ephemeral root filesystem (tmpfs or wipe-on-boot) so undeclared state disappears at reboot, while declaring which paths must survive on a persistent volume. NixOS still needs durable `/boot` and `/nix`; a common layout adds a `/persist` (or `/persistent`) mount for everything else you keep.

The usual implementation is the community project [nix-community/impermanence](https://github.com/nix-community/impermanence)—not part of nixpkgs core. Its NixOS module exposes `environment.persistence."<persist-path>"`; option names and behavior can change, so treat the upstream README as the source of truth.

## Details

**What you need.** Three pieces: (1) a root that is cleared between boots, (2) at least one persistent volume for files you keep, and (3) the impermanence module to bind-mount or link those paths onto the ephemeral root. Layout of disks and bootloaders belongs in [partitioning and bootloaders](partitioning-and-bootloaders.md) and often [hardware-configuration](hardware-configuration.md); declarative disk tooling such as [disko](../../12-deployment-and-infra/disko.md) can create the partitions/subvolumes (see also [Disko recipes](disko-recipes.md), including `zfs-impermanence`).

### When to use / when not

| Prefer impermanence when… | Prefer a durable root when… |
|---------------------------|-----------------------------|
| You want the machine clean by default and state only where you declared it | You need large working trees or downloads on `/` without babysitting tmpfs size / OOM |
| You want failed experiments and undeclared junk to vanish on reboot | Crash or power loss must not erase anything you forgot to move to persist |
| You are willing to maintain `directories` / `files` (and HM persistence) over time | Many services write unpredictable paths under `/var/lib` and you will not track them |
| Rebuild-from-config is the recovery story for the OS tree | Dual-boot or other OSes expect a normal persistent `/` |
| You run Home Manager as a NixOS module (or NixOS-only persistence) | You rely on standalone-only Home Manager for user state (upstream HM persistence expects the NixOS HM module + NixOS impermanence module) |

Upstream’s stated goals match the left column: keep the system clean, force declared keepers, and experiment without clutter. The right column is mostly the tmpfs drawbacks and operational cost of an incomplete persist list—not a rejection of wipe-on-boot Btrfs/ZFS layouts, which avoid memory limits but still lose undeclared paths after the wipe.

### Ephemeral root patterns

Upstream documents tmpfs root (simple; memory-backed; size limits and crash loss) and Btrfs (or similar) wipe/recreate of the root subvolume at boot, optionally retaining old roots for a while. Other filesystems and “erase your darlings” variants exist; pick one and keep `/nix` and `/boot` off the wiped tree. The persist mount name is yours (`/persist`, `/persistent`, …)—multiple `environment.persistence."…"` attributes are supported if you split backed-up vs not-backed-up volumes.

### NixOS module

Import via flake: `inputs.impermanence.url = "github:nix-community/impermanence"`, then `impermanence.nixosModules.impermanence` in `nixosConfigurations.*.modules`. The flake lists `nixpkgs` and `home-manager` as inputs for development; they are unused at runtime—set `impermanence.inputs.nixpkgs.follows = ""` and `impermanence.inputs.home-manager.follows = ""` if you want them out of `flake.lock`.

Under `environment.persistence."/persist"` (path is your persist mount), declare `directories` and `files` (strings or attribute sets with `user` / `group` / `mode`), optional nested `users.<name>.{directories,files}` for home paths, and flags such as `hideMounts` (and `allowTrash`, `enable` as in the README). File entries may set `method` (`"auto"` default vs `"symlink"`) and `parentDirectory` permissions. Typical survivors from upstream examples: `/var/log`, selected `/var/lib/…`, `/etc/machine-id`, and user `.ssh` / `.gnupg` with mode `0700`. Undeclared paths disappear at reboot; declared ones are bind-mounted or linked from the persist volume.

### Home Manager

`home.persistence` mirrors the NixOS shape under `home`. When Home Manager is used as a NixOS module, importing the NixOS impermanence module loads HM persistence automatically. Standalone-only Home Manager is awkward for this stack—upstream requires the Home Manager NixOS module **and** the NixOS persistence module for intended behavior. See [standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md).

### Failure modes

| Failure | What goes wrong | Mitigation (README / ops) |
|---------|-----------------|---------------------------|
| **`neededForBoot` race** | Persist (and ephemeral) volumes not marked `neededForBoot` → early bind/link of paths such as `/etc/machine-id` races initrd / mount ordering | Mark **persistent and ephemeral** storage volumes `neededForBoot` (upstream “Important note”) |
| **Undeclared path lost** | App or service wrote under `/` or home outside the persist list → gone after reboot (or after root wipe) | Add the path (or a parent) to `directories` / `files` / `users.*.…`; treat “lost after reboot” as a missing declaration |
| **Secrets on ephemeral root** | Ciphertext or decrypt identities only on wiped `/` → activation cannot decrypt; credentials vanish | Keep decrypt identities and any out-of-store secret files on the persist volume; decrypted material still under `/run/…` after activation—see [Secrets strategies](secrets-strategies.md) |
| **SSH host keys + agenix/sops identities** | Host keys under `/etc/ssh` or `age.identityPaths` / `sops.age.keyFile` / `sops.age.sshKeyPaths` not on persist → new host identity each boot, secret decrypt fails, SSH trust breaks | Persist host key paths (and dedicated age key files) via `environment.persistence`, or point identity options at durable paths on the persist mount; pair with [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md) |
| **`/etc/machine-id`** | Not persisted → new machine-id each boot; journal / D-Bus / some licenses treat the host as new | Declare `/etc/machine-id` under `files` (upstream example); ensure persist is `neededForBoot` so the link/bind is early enough |
| **HM standalone awkwardness** | `home.persistence` alone without NixOS HM + NixOS impermanence modules → does not work as intended | Use Home Manager’s NixOS module with `impermanence.nixosModules.impermanence`, or keep user state only via NixOS `environment.persistence.*.users` |
| **tmpfs root pressure** | Large downloads or data on `/` → OOM or “disk full” in RAM-backed root; crash before copy-to-persist loses files | Cap `size=…` knowingly; write big data under persist mounts; or use wipe-on-boot disk root instead of tmpfs |

Option details beyond this page: follow the README. Do not invent flags not listed there.

### Boundaries (what this page is not)

- [Secrets strategies](secrets-strategies.md) alone—decrypting credentials into ephemeral roots still needs that page.
- [Home Manager dotfiles](../../10-home-and-user/home-manager/dotfiles-patterns.md)—user-level persistence patterns.
- [ZFS snapshots](zfs-and-btrfs.md) and filesystem-level rollback semantics.
- Disk-layout chooser / disko-vs-manual matrix—[Disk and persistence](../../cheatsheets/disk-and-persistence.md); layouts also on [Disko recipes](disko-recipes.md).

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
          # fileSystems."/persist".neededForBoot = true;  # and ephemeral root — required by upstream
          environment.persistence."/persist" = {
            hideMounts = true;
            directories = [
              "/var/log"
              "/var/lib/nixos"
              { directory = "/var/lib/bluetooth"; mode = "0700"; }
              # Often also: "/etc/ssh" (or individual host key files) for stable SSH + age recipients
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

- [Disk and persistence](../../cheatsheets/disk-and-persistence.md) — layout / impermanence chooser
- [Partitioning and bootloaders](partitioning-and-bootloaders.md)
- [Hardware configuration](hardware-configuration.md)
- [Secrets strategies](secrets-strategies.md)
- [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md)
- [disko](../../12-deployment-and-infra/disko.md)
- [Disko recipes](disko-recipes.md)
- [Disko + impermanence host (worked example)](../../16-configuration-examples/disko-impermanence-host.md)
- [Home Manager: standalone vs NixOS module](../../10-home-and-user/home-manager/standalone-vs-nixos-module.md)
- [Generations and boot](../architecture/generations-and-boot.md)

## References

- [nix-community/impermanence](https://github.com/nix-community/impermanence) — community project
- [impermanence README](https://github.com/nix-community/impermanence/blob/master/README.org) — modules, options, system-setup patterns (source of truth)
- [NixOS Wiki: Impermanence](https://wiki.nixos.org/wiki/Impermanence) — community patterns (secondary)
- [etu: NixOS tmpfs as root](https://elis.nu/blog/2020/05/nixos-tmpfs-as-root/) — tmpfs install walkthrough (secondary)
- [grahamc: Erase your darlings](https://grahamc.com/blog/erase-your-darlings) — ZFS snapshot wipe rationale (secondary)
