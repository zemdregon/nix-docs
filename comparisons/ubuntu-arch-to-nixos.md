---
status: complete
---

# Ubuntu / Arch to NixOS

## Overview

Operators coming from Ubuntu or Arch are used to imperative package managers (`apt`, `pacman`) and hand-edited files under `/etc`. NixOS inverts that: the **declared configuration** (`configuration.nix` or a flake-based `nixosConfigurations` entry) is the source of truth; rebuilds produce versioned **generations** and regenerate most of `/etc`. This page is a concise migration playbook—not a rehash of the installers. Use it to inventory what you have today, try NixOS safely, map old habits to options, install, then iterate with `nixos-rebuild test` / `switch`. For the package-manager mental model first, read [Nix vs apt / pacman](nix-vs-apt-pacman.md); for vocabulary and reading order, see the [Beginner roadmap](../00-roadmap/beginner.md).

## Details

### Mental model shift

| Ubuntu / Arch habit | NixOS equivalent |
|---------------------|------------------|
| `apt install` / `pacman -S` for CLI tools | `environment.systemPackages` (or per-user `users.users.<name>.packages`) in [configuration.nix](../09-nixos/configuration/configuration-nix.md) |
| `systemctl enable --now foo` | `services.foo.enable = true` (and related `services.*` options) |
| Edit `/etc/nginx/nginx.conf` by hand | Declare service options (or `environment.etc`, `systemd.services`) in config; activation writes `/etc` |
| `passwd`, `useradd`, `usermod` | `users.users` / `users.groups`; see [Users and groups](../09-nixos/configuration/users-and-groups.md) |
| Upgrade with `apt upgrade` / `pacman -Syu` | Refresh channel or flake lock, then rebuild—[Upgrades](../09-nixos/operations/upgrades.md) |
| Restore from backup after a bad upgrade | Boot or `switch` to a previous **generation**—[Rollbacks](../09-nixos/operations/rollbacks.md) |

**Packages vs configuration.** On Ubuntu/Arch you often install first and configure files later. On NixOS, many “installs” are option toggles: enabling `services.openssh.enable` pulls in OpenSSH and wires systemd; adding `git` to `environment.systemPackages` puts it on the system profile. Saving config does nothing until you [rebuild](../09-nixos/operations/rebuild-switch-boot-test.md).

**`/etc` is managed.** Files under `/etc` on a running NixOS system are typically generated from your module tree. Manual edits may be overwritten on the next activation. Put durable changes in `configuration.nix`, imported modules, or documented `environment.etc` / service options—not ad hoc edits you expect to survive rebuilds.

**`users.mutableUsers`.** Default `true` merges declarative users with imperative `useradd` / `passwd` changes (similar spirit to “I fixed it on the live system”). Set `false` when you want `/etc/passwd` and passwords to match config exactly on every rebuild—common for servers and declarative home setups. Password and key patterns: [Users and groups](../09-nixos/configuration/users-and-groups.md).

**Generations.** Each successful `nixos-rebuild` builds a new system generation (store path + boot menu entry). The previous generation remains until garbage collection. That is your rollback surface—see [Rollbacks](../09-nixos/operations/rollbacks.md) and [Generations and boot](../09-nixos/architecture/generations-and-boot.md).

**Flakes (optional).** A classic install keeps `/etc/nixos/configuration.nix` on a channel. A flake pins inputs in `flake.lock` and builds via `nixos-rebuild switch --flake .#hostname`. The playbook steps are the same; only where config lives and how you upgrade inputs differ. You can start on channels and adopt flakes later.

### Playbook

#### 1. Inventory (on Ubuntu or Arch)

Before touching NixOS, capture what the machine actually needs:

- **Packages:** list explicitly installed tools (`apt list --installed`, `pacman -Qe`, or your notes). Separate “user CLI tools” from “system daemons.”
- **Services:** `systemctl list-unit-files --state=enabled` (or equivalent). Note web servers, databases, VPNs, containers, printing, etc.
- **Config you rely on:** networking (static IP, Wi-Fi, VPN), disk layout, boot loader, encryption, SSH keys, sudo/wheel membership, locale, desktop/WM.
- **Secrets:** passwords, API keys, TLS material—plan declarative or file-based options; do not paste secrets into the wiki or store plaintext in git.
- **Hardware quirks:** GPU drivers, firmware, dual-boot with Windows or another Linux, Secure Boot policy.

Map each row to NixOS options using [search.nixos.org](https://search.nixos.org/options). Daemons almost always land under `services.*`; one-off CLIs under `environment.systemPackages` or home-manager later.

#### 2. Try safely (VM or dual-boot)

Do not bet your only production disk on day one.

- **VM:** Install from a graphical ISO in VirtualBox/QEMU, or exercise config with `nixos-rebuild build-vm` before bare metal—[Dual boot and VMs](../09-nixos/installation/dual-boot-and-vms.md).
- **Dual-boot:** Shrink or use free space; leave existing partitions intact. Prefer **systemd-boot** when sharing the disk with another Linux; GRUB + `boot.loader.grub.useOSProber` mainly helps **Windows**, not other Linux installs. Secure Boot is often disabled for the NixOS ISO and boot-loader setup—details in [Dual boot and VMs](../09-nixos/installation/dual-boot-and-vms.md).

Desktop trial path: [Graphical installer](../09-nixos/installation/graphical-installer.md). Full disk control or multi-boot layouts: [Manual install](../09-nixos/installation/manual-install.md).

#### 3. Declare config (before or during install)

Draft the target system in Nix, even as comments or a scratch file on your current distro:

```nix
{ config, pkgs, ... }: {
  imports = [ ./hardware-configuration.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "workstation";
  networking.networkmanager.enable = true;

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    openssh.authorizedKeys.keys = [ "ssh-ed25519 AAAA…" ];
  };

  environment.systemPackages = with pkgs; [
    git htop vim
  ];

  services.openssh.enable = true;

  system.stateVersion = "26.05"; # match the release you install from; do not bump casually
}
```

`hardware-configuration.nix` is generated at install from detected disks—do not invent partition UUIDs. Shape and apply semantics: [configuration.nix](../09-nixos/configuration/configuration-nix.md).

**Mapping examples:**

| Former command | NixOS direction |
|----------------|-----------------|
| `sudo apt install nginx` / `pacman -S nginx` | `services.nginx.enable = true` (+ virtual host options) |
| `sudo apt install docker.io` / `pacman -S docker` | `virtualisation.docker.enable = true` (or podman module) |
| `sudo apt install build-essential` | `environment.systemPackages = with pkgs; [ gcc gnumake ];` or a dev shell via Nix on any distro first |

When unsure, search options before adding packages—NixOS often exposes a service module with safer defaults than a raw package.

#### 4. Install

Follow the official installation chapters (linked under References)—do not rely on memorized partition commands here.

- **Graphical, single-disk desktop:** [Graphical installer](../09-nixos/installation/graphical-installer.md).
- **Manual partitioning, dual-boot, minimal ISO:** [Manual install](../09-nixos/installation/manual-install.md)—mount target under `/mnt`, run `nixos-generate-config --root /mnt`, merge your draft options into `/mnt/etc/nixos/configuration.nix`, then `nixos-install`.

Set user passwords at install (`nixos-enter --root /mnt -c 'passwd …'` for normal users). Pick `system.stateVersion` to match the release on the install media.

#### 5. Iterate: rebuild, test, rollback

After install, all system changes go through rebuild:

```bash
sudo nixos-rebuild test    # activate now; reboot reverts boot default if broken
sudo nixos-rebuild switch   # activate and set boot default
sudo nixos-rebuild switch --rollback   # back one generation
```

Use **`test`** for risky service or networking changes; use **`switch`** once confident. Upgrade channels or flake inputs separately from editing options—[Upgrades](../09-nixos/operations/upgrades.md). When builds fail, read the trace and check [FAQ — common errors](../cheatsheets/faq-common-errors.md).

**Anti-patterns from Ubuntu/Arch:**

- Running `apt` / `pacman` on NixOS—they are not the system package manager.
- Editing `/etc/foo.conf` without a matching config option, then wondering why it reverted.
- Bumping `system.stateVersion` like a normal package upgrade—it gates one-time state migrations; leave it at the install release unless you have audited changes.

## Examples

Minimal migration checklist (copy as a personal runbook):

1. Export enabled systemd units and package list from current OS.
2. Boot NixOS ISO in a VM; complete [graphical install](../09-nixos/installation/graphical-installer.md) or [manual install](../09-nixos/installation/manual-install.md) with spare disk space.
3. Port one service at a time into `configuration.nix`; `nixos-rebuild test` after each.
4. When stable, `nixos-rebuild switch`; keep several generations before running aggressive GC.
5. Schedule upgrades via channel or flake update + rebuild, not ad hoc package commands.

Dual-boot sketch (UEFI, systemd-boot, NixOS + existing Windows ESP untouched except shared `/boot` mount policy)—full steps in [Dual boot and VMs](../09-nixos/installation/dual-boot-and-vms.md):

```nix
boot.loader.systemd-boot.enable = true;
boot.loader.efi.canTouchEfiVariables = true;
# fileSystems from nixos-generate-config only for NixOS-owned partitions
```

## References

- [NixOS manual — Installation](https://nixos.org/manual/nixos/stable/#ch-installation)
- [NixOS manual — Manual Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual)
- [NixOS manual — Graphical Installation](https://nixos.org/manual/nixos/stable/index.html#sec-installation-graphical)
- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)
- [NixOS option search](https://search.nixos.org/options)

## See also

- [Nix vs apt / pacman](nix-vs-apt-pacman.md)
- [Beginner roadmap](../00-roadmap/beginner.md)
- [configuration.nix](../09-nixos/configuration/configuration-nix.md)
- [Manual install](../09-nixos/installation/manual-install.md)
- [Graphical installer](../09-nixos/installation/graphical-installer.md)
- [Dual boot and VMs](../09-nixos/installation/dual-boot-and-vms.md)
- [Upgrades](../09-nixos/operations/upgrades.md)
- [Rollbacks](../09-nixos/operations/rollbacks.md)
- [nixos-rebuild actions](../09-nixos/operations/rebuild-switch-boot-test.md)
- [FAQ — common errors](../cheatsheets/faq-common-errors.md)
