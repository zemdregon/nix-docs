---
status: complete
last-checked: 2026-08
---

# WSL and foreign OS

## Overview

Windows Subsystem for Linux (WSL) is a common host for Nix work, but the word “WSL” covers two different setups. **Nix on WSL** means installing the Nix package manager inside an ordinary Linux distro registered with WSL (Ubuntu, Debian, Fedora, and similar)—the host still owns the root filesystem and init story. **NixOS-WSL** is a community project that registers **NixOS itself** as the WSL distribution, so you get full NixOS modules, `nixos-rebuild`, and system activation inside WSL while Windows and WSL supply the kernel and boot environment.

For installer flags, multi-user vs single-user, and coexistence with apt/dnf, see [Nix on other distros](nix-on-other-distros.md). This page focuses on the WSL-specific fork: plain foreign-distro Nix vs NixOS-as-WSL-distro.

## Details

### Nix on WSL (foreign Linux distro)

WSL2 is Linux from Nix’s point of view. Install Nix with the same official or Determinate installer you would use on bare metal, then manage user config with [Home Manager in standalone mode](home-manager/standalone-vs-nixos-module.md) unless you later move to NixOS-WSL.

WSL2 often ships without systemd enabled. With **systemd enabled** in `/etc/wsl.conf` (`[boot] systemd=true`), prefer a **multi-user** install (`--daemon`). Without systemd, use **single-user** (`--no-daemon`). That split is documented on [Nix on other distros](nix-on-other-distros.md); do not repeat the full install matrix here.

You still have an Ubuntu/Debian/etc. base: distro packages, `/etc` layout, and upgrades stay with that distribution. Nix adds `/nix`, profiles, and flakes on top—it does not turn the VM into NixOS.

**Store location.** Keep the Nix store on WSL’s **Linux native filesystem** (the ext4 VHD that backs the distro—typically `/` with `/nix` at the root). Do **not** put `/nix` on `/mnt/c`, other DrvFS automounts, or a bind mount into the Windows NTFS side. DrvFS lacks reliable Unix semantics (symlinks, permissions, case sensitivity, locking); builds become slow and can fail in subtle ways. If you need more space, grow the WSL virtual disk or move the **entire distro** to another drive—not just the store onto `C:`.

### NixOS-WSL (NixOS as the WSL distro)

[NixOS-WSL](https://github.com/nix-community/NixOS-WSL) (maintainer [@nzbr](https://github.com/nzbr), Apache-2.0) ships NixOS modules and prebuilt `nixos.wsl` images so WSL runs a real NixOS system closure. Documentation: [NixOS-WSL book](https://nix-community.github.io/NixOS-WSL/).

**Install (current upstream flow).** Enable WSL if needed, download `nixos.wsl` from the [latest release](https://github.com/nix-community/NixOS-WSL/releases/latest) (as of 2026-06, release **2605.7.2**), then:

- **WSL ≥ 2.4.4:** double-click the file or run `wsl --install --from-file nixos.wsl` from PowerShell (optional `--name`, `--location`; defaults: distro name `NixOS`, image under `%localappdata%\wsl\…`).
- **Older WSL:** `wsl --import NixOS $env:USERPROFILE\NixOS nixos.wsl --version 2` (adjust name and paths).

Open a shell with `wsl -d NixOS` (or the name you chose). Set the default distro with `wsl -s NixOS` if desired.

**Post-install.** Default user is `nixos` (in `wheel`). NixOS-WSL defaults to passwordless sudo for `wheel`; run `passwd` when you need a login password or enable `security.sudo.wheelNeedsPassword`. Run `sudo nix-channel --update` once so `nixos-rebuild` works against your channels. See [Installation](https://nix-community.github.io/NixOS-WSL/install.html) for full steps.

**Configuration.** Enable the module and set WSL-specific options under `wsl.*`:

| Option | Role (summary) |
|--------|----------------|
| `wsl.enable` | Turn on NixOS-as-WSL support (default `false`; set `true` in your config). |
| `wsl.defaultUser` | Default login user (default `"nixos"`). |
| `wsl.wslConf` | Values written to `/etc/wsl.conf` (systemd, interop, automount, hostname, etc.). |
| `wsl.interop.*` | Windows PATH and binfmt registration tweaks. |
| `wsl.docker-desktop.enable` | Docker Desktop integration. |
| `wsl.usbip.enable` / `wsl.usbip.autoAttach` | USB/IP via Usbipd on Windows. |
| `wsl.useWindowsDriver` | Host OpenGL driver path (preferred over WSL’s ldconfig automount for NixOS). |
| `wsl.ssh-agent.enable` | Pass through to Windows ssh-agent. |
| `wsl.startMenuLaunchers` | Start Menu shortcuts for GUI apps. |

Full types and defaults: [Configuration options](https://nix-community.github.io/NixOS-WSL/options.html). Do not invent options beyond that reference.

**Kernel, bootloader, and activation.** WSL provides the Linux kernel and starts the distro; there is no bare-metal firmware boot chain inside the VM. The NixOS-WSL `wsl-distro` module reflects that: it disables normal boot paths (`boot.initrd.enable`, `boot.kernel.enable`, `boot.loader.grub.enable`, `boot.modprobeConfig.enable`) and sets `system.build.installBootLoader` to a no-op, with an in-module comment that WSL uses its own kernel and boot loader. System changes still apply through NixOS activation and `nixos-rebuild switch`—generations and services—without installing GRUB or an initrd for WSL boot.

Import the module from your flake or channel (for example `inputs.nixos-wsl.nixosModules.default` on current flakes). Rebuild with the same `nixos-rebuild` workflow as on bare metal, subject to WSL constraints (shared kernel, Windows-side WSL version).

### Contrast: plain Nix on Ubuntu-WSL vs NixOS-WSL

| | Nix on Ubuntu (or other) WSL | NixOS-WSL |
|--|------------------------------|-----------|
| **Host OS** | Ubuntu/Debian/etc. rootfs and package DB | NixOS system closure |
| **Install** | Nix installer on existing distro | Import `nixos.wsl` or `--install --from-file` |
| **System config** | Distro tools + optional Home Manager standalone | `configuration.nix`, NixOS modules, `wsl.*` |
| **Rebuild story** | `home-manager switch`; no `nixos-rebuild` for the host | `nixos-rebuild switch` / `test` / etc. |
| **Activation** | Nix profiles + HM activation; distro owns `/etc` services | Full NixOS [activation script](../09-nixos/architecture/activation-script.md) for declared system state |
| **Bootloader / kernel** | WSL kernel; distro init; Nix unrelated to boot | WSL kernel; module disables NixOS boot loader/initrd install |
| **Typical use** | Nix alongside apt; minimal change to existing WSL setup | Declarative NixOS desktop/server-in-WSL; closest to bare NixOS on Windows |

Neither path is “Nix on Windows” natively—both run inside WSL’s Linux VM. For declarative macOS system config outside WSL, see [nix-darwin](nix-darwin.md).

### Common failure modes

| Symptom or mistake | Likely cause | What to do |
|--------------------|--------------|------------|
| Multi-user Nix daemon fails to start or hangs | WSL2 without systemd but Nix installed with `--daemon` | Enable `[boot] systemd=true` in `/etc/wsl.conf` (or via `wsl.wslConf.boot.systemd` on NixOS-WSL), restart WSL, or reinstall Nix with `--no-daemon` for single-user mode |
| Very slow builds, flaky store paths, permission errors | `/nix` or `nix-daemon` temp dirs on `/mnt/c` or other **DrvFS** | Move store back to the Linux VFS root; never bind `/nix` to Windows drives. See store guidance above |
| `sudo nixos-rebuild switch` “should” work on Ubuntu WSL | **NixOS-WSL vs Nix-in-Ubuntu** confusion—foreign distro is not NixOS | On plain WSL distros use [Home Manager standalone](home-manager/standalone-vs-nixos-module.md); reserve `nixos-rebuild` for NixOS-WSL or bare NixOS |
| GUI apps crash on OpenGL / no GPU acceleration | Stock WSL **ldconfig automount** path (`wsl.wslConf.automount.ldconfig`) does not work with NixOS | On NixOS-WSL set `wsl.useWindowsDriver = true` so host drivers are wired the NixOS-WSL way; do not rely on WSL’s default ldconfig hook for NixOS |
| Unexpected passwordless `sudo`, open `wheel` | NixOS-WSL default user **`nixos`** in `wheel` with passwordless sudo | Run `passwd` for a login password; set `security.sudo.wheelNeedsPassword = true` when you want sudo to prompt |
| Windows `.exe` not found, wrong PATH, broken interop | Interop or PATH merge disabled or overridden | Check `wsl.wslConf.interop.enabled`, `wsl.wslConf.interop.appendWindowsPath`, and `wsl.interop.includePath` / `wsl.interop.register` per [options.html](https://nix-community.github.io/NixOS-WSL/options.html) |
| GUI apps do not appear (WSLg) | WSLg unavailable, wrong distro, or interop/GUI wiring | Requires a WSLg-capable Windows build and a GUI stack in your config; NixOS-WSL can expose Start Menu entries via `wsl.startMenuLaunchers`. Tune interop through `wsl.wslConf` ([Microsoft wsl.conf](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)) |
| Following NixOS module docs on a foreign WSL host | Plain WSL has **no `nixos-rebuild` for the host**—only profiles and HM | Treat the host like any foreign Linux: Nix installer + HM standalone; system modules apply only after importing NixOS-WSL or moving to bare NixOS |

For the same “foreign host, not full NixOS” story on macOS or stock Linux, see [nix-darwin](nix-darwin.md) and [Nix on other distros](nix-on-other-distros.md).

## Examples

**Nix on an existing Ubuntu WSL distro** (systemd enabled)—details and pitfalls: [Nix on other distros](nix-on-other-distros.md):

```bash
curl -L https://nixos.org/nix/install | sh -s -- --daemon
```

**Install NixOS-WSL from PowerShell** (WSL ≥ 2.4.4; after downloading `nixos.wsl`):

```powershell
wsl --install --from-file nixos.wsl
wsl -d NixOS
```

**Minimal module snippet** (illustrative; extend with your imports/flake):

```nix
{ ... }:

{
  wsl.enable = true;
  wsl.defaultUser = "nixos";

  wsl.wslConf = {
    automount.enabled = true;
    boot.systemd = true;
  };

  # User env often via Home Manager as NixOS module or standalone
}
```

After editing system config on NixOS-WSL:

```bash
sudo nixos-rebuild switch
```

## References

- [NixOS-WSL documentation](https://nix-community.github.io/NixOS-WSL/)
- [NixOS-WSL — Installation](https://nix-community.github.io/NixOS-WSL/install.html)
- [NixOS-WSL — Configuration options](https://nix-community.github.io/NixOS-WSL/options.html)
- [NixOS-WSL GitHub repository](https://github.com/nix-community/NixOS-WSL) — modules, releases (`nixos.wsl`), Apache-2.0
- [Microsoft — WSL configuration (`wsl.conf`)](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) — referenced by `wsl.wslConf` option docs

## See also

- [Nix on other distros](nix-on-other-distros.md) — Nix installer on foreign Linux and WSL2 daemon guidance
- [Home Manager: standalone vs NixOS module](home-manager/standalone-vs-nixos-module.md) — user config on non-NixOS hosts vs integrated rebuild
- [nix-darwin](nix-darwin.md) — declarative system modules on macOS (analogous “full OS module stack on foreign host” story)
- [rebuild: switch, boot, test](../09-nixos/operations/rebuild-switch-boot-test.md) — NixOS rebuild modes used on NixOS-WSL
- [Activation script](../09-nixos/architecture/activation-script.md) — what `nixos-rebuild switch` applies on NixOS-WSL
