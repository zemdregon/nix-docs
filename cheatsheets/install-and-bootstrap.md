---
status: complete
---

# Install and bootstrap

Pick a path by physical access, SSH reachability, and OS goal (full NixOS vs Nix / Home Manager / nix-darwin on another OS). Fresh install ≠ day-2 updates.

## Decision table

| Situation | Prefer | Leaf | Avoid if… |
|-----------|--------|------|-----------|
| Desktop at the machine; guided UI | Graphical ISO (Calamares) | [Graphical installer](../09-nixos/installation/graphical-installer.md) | Custom disk layout, dual-boot, flake-first install, or you booted a **minimal** ISO |
| Console / minimal ISO; custom disks; learning the stack | Manual: partition → `/mnt` → `nixos-generate-config` → `nixos-install` | [Manual install](../09-nixos/installation/manual-install.md) | You only need a stock erase-disk desktop wizard |
| Local / boot media + declarative disks in one step | **disko-install** (disko + `nixos-install`) | [disko](../12-deployment-and-infra/disko.md) | Remote-only host (use nixos-anywhere); dual-boot (disko destructive modes wipe the target) |
| Fresh NixOS over SSH (kexec → disko → install) | **nixos-anywhere** | [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) | Day-2 deploys; Wi‑Fi-only networking; under ~1.5 GB RAM; aarch64 without custom `--kexec` (default image is x86_64-only) |
| Rack / LAN: boot installer without USB | PXE / iPXE netboot, then manual (or SSH tools) | [Netboot and PXE](../09-nixos/installation/netboot-and-pxe.md) | No DHCP/TFTP (or HTTP) infrastructure |
| Share disk with another OS, or guest / `build-vm` | Dual-boot or VM install paths | [Dual boot and VMs](../09-nixos/installation/dual-boot-and-vms.md) | Whole-disk erase in the graphical wizard |
| macOS system modules | **nix-darwin** (`darwin-rebuild`) | [nix-darwin](../10-home-and-user/nix-darwin.md) | Expecting a NixOS ISO or Linux systemd |
| Linux/macOS host; user env only | Nix + Home Manager standalone | [Home Manager](../10-home-and-user/home-manager/README.md) · [standalone vs module](../10-home-and-user/home-manager/standalone-vs-nixos-module.md) · [Nix on other distros](../10-home-and-user/nix-on-other-distros.md) | Needing a full NixOS rootfs |
| Windows + WSL | Nix-in-distro **or** NixOS-WSL | [WSL and foreign OS](../10-home-and-user/wsl-and-foreign-os.md) | Confusing “Nix on Ubuntu-WSL” with NixOS-as-WSL |
| Only the Nix package manager (not NixOS) | Official / Lix / Determinate installers | [Installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md) | Treating curl installers as a NixOS ISO substitute |
| **After** bootstrap: change a running NixOS | `nixos-rebuild` / remote deploy | [Rebuild switch/boot/test](../09-nixos/operations/rebuild-switch-boot-test.md) · [Remote deploy](../09-nixos/operations/remote-deploy.md) | Re-running nixos-anywhere for ordinary updates |

Hub: [NixOS installation](../09-nixos/installation/README.md). ISOs: [nixos.org/download](https://nixos.org/download/).

## Failure callouts

| Symptom / mistake | Fix |
|-------------------|-----|
| Using nixos-anywhere for day-2 config pushes | Switch to [`nixos-rebuild --target-host`](../09-nixos/operations/remote-deploy.md) (or deploy tools under [deployment and infra](../12-deployment-and-infra/README.md)) |
| nixos-anywhere stalls / network oddities on Wi‑Fi | Tool assumes wired/public/local reachability; custom `--kexec` if you need VPN-like networking |
| kexec OOM or hangs | Need ≥ ~1.5 GB free RAM (excl. swap) for default kexec; see [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) |
| `The default kexec image only support x86_64` | Pass `--kexec` with a matching tarball (aarch64 / custom networking)—[nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) |
| Live Wi‑Fi worked; first boot has no wireless | Generated config often omits NM/wireless—declare networking after install ([graphical](../09-nixos/installation/graphical-installer.md) / [manual](../09-nixos/installation/manual-install.md)) |
| Treated “Nix on Ubuntu-WSL” as NixOS-WSL | Different roots: foreign-distro Nix vs NixOS-as-WSL—[WSL and foreign OS](../10-home-and-user/wsl-and-foreign-os.md) |

## See also

- [NixOS installation](../09-nixos/installation/README.md)
- [Disk and persistence](disk-and-persistence.md) — disks / wipe-root / bootloader chooser
- [Home and user](../10-home-and-user/README.md)
- [Installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md)
- [nixos-anywhere bootstrap (worked example)](../16-configuration-examples/nixos-anywhere-bootstrap.md)
- [Disko + impermanence host (worked example)](../16-configuration-examples/disko-impermanence-host.md)

## References

- [Download Nix / NixOS](https://nixos.org/download/) — ISOs and Nix package-manager install entry
- [nixos-anywhere documentation](https://nix-community.github.io/nixos-anywhere/)
- [disko](https://github.com/nix-community/disko) — declarative disks; **disko-install**
- [NixOS manual — Installation](https://nixos.org/manual/nixos/stable/#ch-installation)
