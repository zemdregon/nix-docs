---
status: complete
last-checked: 2026-08
---

# nixos-anywhere bootstrap

## Overview

This walkthrough wires a **remote wipe-and-install** from your laptop: a flake with `nixosConfigurations`, a disko disk layout, and one command that SSHs to bare metal or a VPS, kexecs into a NixOS installer, partitions, installs, and reboots. It is a **file-layout and first-install story**—not day-2 deploy. After the machine runs NixOS, use `nixos-rebuild --target-host` or fleet tools instead of re-running nixos-anywhere.

Pins such as `nixos-26.05` and `x86_64-linux` are illustrative. Replace the disk `device` path and SSH authorized keys before any real wipe. Flake `nix run` needs experimental [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md) on the **source** machine.

## Details

### What you get

One repository directory with a flake, a host module, and a disko layout. The `nixosConfigurations` output name (`myhost` in the snippets below) is what you pass after `#` to nixos-anywhere and, later, to `nixos-rebuild switch --flake`. Evaluating that output produces a closed system [generation](../02-concepts/generation.md) that nixos-anywhere copies to the remote disk during the `install` phase.

### Domains composed

This example pulls together teaching pages from several domains:

- [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) — SSH → kexec → disko → install → reboot; flags and requirements
- [disko](../12-deployment-and-infra/disko.md) — declarative partitioning consumed by the installer's disko phase
- [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) — `nixosSystem`, modules, and the `#name` fragment
- [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md) — experimental features required on the **source** machine for `nix run`
- [Install and bootstrap](../cheatsheets/install-and-bootstrap.md) — when to choose anywhere vs ISO vs day-2 paths
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — post-install config changes (`nixos-rebuild --target-host`)
- [Fleet deploy](../cheatsheets/fleet-deploy.md) — when one host becomes many (colmena, deploy-rs, …)

Optional deepen: combine disko with [impermanence](../09-nixos/configuration/impermanence.md) for ephemeral root and persistent `/persist`—see the worked [Disko + impermanence host](disko-impermanence-host.md) (same flake shape; different `disko.devices` and persist list).

### Default install flow

When `--phases` is unset, nixos-anywhere runs **`kexec` → `disko` → `install` → `reboot`**:

1. **kexec** — If the target is not already a NixOS installer, load a bundled kexec tarball and boot into one.
2. **disko** — Unmount and destroy target filesystems per the disko config, then create and mount partitions.
3. **install** — Build (or upload) the flake's `nixosConfigurations.<name>` closure and activate it on the target.
4. **reboot** — Unmount, export ZFS pools if any, reboot into the installed system.

Skip or reorder with `--phases` (comma-separated). The default disko phase is **destructive**—treat a full run as a wipe of disks named in your layout.

### What you need

| Side | Requirement |
|------|-------------|
| **Source** | Linux, macOS, NixOS, or WSL2 with Nix; [`flakes`](../08-experimental-features/flakes.md) + [`nix-command`](../08-experimental-features/nix-command.md). You do not install nixos-anywhere locally—use `nix run github:nix-community/nixos-anywhere`. |
| **Flake** | `nixosConfigurations.<name>` that imports disko's NixOS module and declares `disko.devices`. |
| **Target** | SSH reachability (root, or a user with passwordless sudo). **x86_64 or aarch64** Linux with kexec for the default path. |
| **kexec image** | Default bundled image is **x86_64-only**. aarch64 (and custom networking/VPN/Wi‑Fi) need `--kexec` with a matching tarball. |
| **RAM** | ≥ ~1.5 GB free RAM (excluding swap) when using kexec. |
| **Network** | Wired/public/local reachability assumptions; exotic networking may need a custom `--kexec` installer. |

### File layout

```
.
├── flake.nix
├── flake.lock                 # after nix flake lock
├── hosts/
│   └── myhost/
│       ├── default.nix        # host policy + disko import
│       └── disko.nix          # ESP + root on one disk (by-id)
```

On a real install, replace the illustrative `/dev/disk/by-id/…` in `disko.nix` with the target disk from `lsblk -o NAME,SIZE,MODEL,SERIAL`. Optionally pass `--generate-hardware-config` so nixos-anywhere writes `hardware-configuration.nix` (or `facter.json`) to a **local** path in your flake during install—import that file from the host module before bare-metal runs that need detected kernel modules.

### Annotated pieces

**`flake.nix`** — pin `nixpkgs` and disko, expose one `nixosConfigurations` entry:

```nix
{
  description = "Remote bootstrap via nixos-anywhere";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  inputs.disko.url = "github:nix-community/disko/latest";
  inputs.disko.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, disko, ... }@inputs: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit inputs; };
      modules = [
        disko.nixosModules.disko
        ./hosts/myhost/default.nix
      ];
    };
  };
}
```

See [NixOS configurations in flakes](../07-flakes/workflows/nixos-configurations.md) for `specialArgs`, multiple hosts, and dropping the legacy top-level `system` argument once `nixpkgs.hostPlatform` is set in the host module.

**`hosts/myhost/disko.nix`** — minimal GPT: EFI System Partition + ext4 root on one disk:

```nix
{
  disko.devices = {
    disk.main = {
      type = "disk";
      # Replace with the target disk — confirm with lsblk before install
      device = "/dev/disk/by-id/nvme-VENDOR_MODEL_SERIAL";
      content = {
        type = "gpt";
        partitions = {
          boot = {
            name = "ESP";
            size = "512M";
            type = "EF00";
            content = {
              type = "filesystem";
              format = "vfat";
              mountpoint = "/boot";
            };
          };
          root = {
            name = "root";
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
}
```

**`hosts/myhost/default.nix`** — host policy; imports disko layout. Enable SSH and put your public key in place **before** install, or you will lock yourself out after reboot:

```nix
{ config, pkgs, ... }: {
  imports = [ ./disko.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "myhost";
  networking.networkmanager.enable = true;

  services.openssh.enable = true;

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    # Replace with your real public key string (no private keys in the repo).
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAA…REPLACE_ME alice@laptop"
    ];
  };

  # Set once at install to the release you started on; do not bump casually.
  system.stateVersion = "26.05";
}
```

disko generates `fileSystems` from `disko.devices`—you normally omit a hand-written root `fileSystems."/"` block. Bootloader options still belong in the NixOS module ([partitioning and bootloaders](../09-nixos/configuration/partitioning-and-bootloaders.md)).

### Install / verify

Lock and dry-run the flake and disko layout in a VM before touching remote disks:

```bash
# nix.conf or --extra-experimental-features 'nix-command flakes'
nix flake lock
nix run github:nix-community/nixos-anywhere -- --flake .#myhost --vm-test
```

Install onto a reachable SSH target (destructive on disks named in `disko.nix`):

```bash
nix run github:nix-community/nixos-anywhere -- \
  --flake .#myhost \
  --target-host root@203.0.113.10
```

Useful variants from the [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) reference:

| Flag | Role |
|------|------|
| `--build-on auto\|local\|remote` | Where to build the closure (default `auto`) |
| `--kexec <path>` | Custom kexec tarball (aarch64, VPN, …) |
| `--phases kexec,disko,install` | Stop before reboot |
| `--generate-hardware-config nixos-generate-config ./hosts/myhost/hardware-configuration.nix` | Write hardware facts to a local flake path during install |
| `--no-disko-deps` | Upload only the disko script (less RAM on tight targets) |
| `--env-password` | Use `SSHPASS` for password-based `ssh-copy-id` |

After reboot, SSH host keys usually change—remove stale entries (`ssh-keygen -R 203.0.113.10`). **Day-2 updates** use the same flake with remote rebuild, not nixos-anywhere:

```bash
nixos-rebuild switch --flake .#myhost --target-host alice@203.0.113.10 --elevate=sudo
```

See [remote deploy](../09-nixos/operations/remote-deploy.md) and [fleet deploy](../cheatsheets/fleet-deploy.md) when the fleet grows beyond one-off SSH.

### Failure modes

| Symptom | Likely cause | What to check |
|---------|--------------|---------------|
| SSH login or `ssh-copy-id` fails | Wrong user/key; non-root without passwordless sudo; password auth without `SSHPASS` + `--env-password` | Reach the host manually; use `-i` or set `SSHPASS` |
| Cannot SSH after reboot | `services.openssh` off, or no `authorizedKeys` / root key in the installed config | Put keys in the flake **before** install (see host module above) |
| `Failure unpacking initrd` / kexec dies | Under ~1.5 GB free RAM (excluding swap) | Add RAM; skip kexec if already in a NixOS installer; try `--no-disko-deps` |
| Default kexec image only supports x86_64 | aarch64 target without custom image | Pass `--kexec` with a matching tarball (e.g. from nixos-images) |
| Wrong disk wiped or empty layout | `device` in `disko.nix` points at the wrong drive | Prefer `/dev/disk/by-id/…`; confirm with `lsblk`; run `--vm-test` first |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | Fresh install replaced SSH host keys | `ssh-keygen -R <host>` before reconnecting |
| Re-running nixos-anywhere for config tweaks | Tool is for **install**, not day-2 deploy | Use `nixos-rebuild --target-host` or fleet tools ([remote deploy](../09-nixos/operations/remote-deploy.md)) |
| Flake attribute missing | `#name` does not match `nixosConfigurations` key | Align `myhost` in flake, folder convention, and CLI fragment |
| `experimental Nix feature 'flakes' is disabled` | Source machine missing experimental features | Enable [`flakes`](../08-experimental-features/flakes.md) and [`nix-command`](../08-experimental-features/nix-command.md) |

## Examples

End-to-end picture: files from [File layout](#file-layout) and [Annotated pieces](#annotated-pieces), then validate and install:

```bash
nix flake lock
nix run github:nix-community/nixos-anywhere -- --flake .#myhost --vm-test
nix run github:nix-community/nixos-anywhere -- \
  --flake .#myhost \
  --target-host root@203.0.113.10
```

Match `networking.hostName`, the `nixosConfigurations` key, and the `#` suffix (`myhost` here). After the host is up, day-2:

```bash
nixos-rebuild switch --flake .#myhost --target-host alice@203.0.113.10 --elevate=sudo
```

aarch64 target (custom kexec required; build needs native aarch64, a remote builder, or `boot.binfmt.emulatedSystems`):

```bash
nix run github:nix-community/nixos-anywhere -- \
  --kexec "$(nix build --print-out-paths github:nix-community/nixos-images#packages.aarch64-linux.kexec-installer-nixos-unstable-noninteractive)/nixos-kexec-installer-noninteractive-aarch64-linux.tar.gz" \
  --flake .#myhost \
  --target-host root@203.0.113.10
```

## References

- [nixos-anywhere (GitHub)](https://github.com/nix-community/nixos-anywhere)
- [nixos-anywhere documentation](https://nix-community.github.io/nixos-anywhere/)
- [nixos-anywhere Quickstart](https://nix-community.github.io/nixos-anywhere/quickstart.html)
- [nixos-anywhere Reference](https://nix-community.github.io/nixos-anywhere/reference.html)
- [Using your own kexec image](https://nix-community.github.io/nixos-anywhere/howtos/custom-kexec.html)
- [disko (GitHub)](https://github.com/nix-community/disko)

## See also

- [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) — flags, phases, requirements
- [disko](../12-deployment-and-infra/disko.md) — declarative disks and module import
- [Install and bootstrap](../cheatsheets/install-and-bootstrap.md) — path chooser (ISO vs anywhere vs day-2)
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — post-install `nixos-rebuild --target-host`
- [Minimal flake NixOS host](minimal-flake-nixos-host.md) — local-first single-host layout without remote install
- [Disko + impermanence host](disko-impermanence-host.md) — ephemeral root + persist on a disko flake
