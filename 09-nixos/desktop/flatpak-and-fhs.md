---
status: complete
---

# Flatpak and FHS

## Overview

Flatpak and FHS helpers solve different “run upstream Linux software on NixOS” problems. Flatpak installs sandboxed apps from remotes such as Flathub, with runtime updates managed by Flatpak. FHS wrappers (`buildFHSEnv`, `steam-run`) rebuild a traditional `/usr`/`/lib` layout around a command using bubblewrap; they help unpatched tarballs and proprietary binaries but do not isolate apps from the host the way Flatpak does. Flatpak desktop integration depends on [Wayland and compositors](wayland-and-compositors.md) and [XDG Desktop Portals](wayland-and-compositors.md) for file pickers, screenshare, and similar hooks; FHS wrappers run in the host session and do not use that portal layer.

## Details

**Flatpak on NixOS.** `services.flatpak.enable = true` adds the Flatpak CLI and `fuse3` to `environment.systemPackages`, registers Flatpak with D-Bus and systemd, turns on `programs.fuse`, `security.polkit`, and `fonts.fontDir`, exports user/system Flatpak paths via `environment.profiles`, and creates the `flatpak` system user and group. The module asserts `xdg.portal.enable = true`; without portals, Flatpak apps often lack file access, screenshare, and similar desktop hooks. Full desktop modules (GNOME, Plasma, Hyprland, Sway) usually enable portals; minimal compositor setups need explicit `xdg.portal` configuration — see [Wayland and compositors](wayland-and-compositors.md).

**Flathub and remotes.** Enabling the service does not add Flathub by itself. After rebuild/switch, add remotes imperatively, for example:

```bash
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

Some community NixOS/Home Manager modules wrap remote setup in activation scripts; there is no single built-in `services.flatpak` option in upstream nixpkgs that declaratively registers Flathub — check your channel or third-party modules if you want that workflow.

**Why FHS helpers exist.** NixOS stores packages under `/nix/store` with their own interpreters and library paths. Many upstream Linux binaries assume a Filesystem Hierarchy Standard layout (`/usr/bin`, `/lib`, a glibc dynamic linker in fixed paths). `pkgs.buildFHSEnv` (see nixpkgs manual) assembles an FHS-like tree and runs a wrapper via bubblewrap so those binaries can start without repackaging every dependency into Nix. The manual notes this is similar in shape to container tech but provides **no security-relevant separation** from the host — trust the binary you run.

**`buildFHSEnv` vs `steam-run`.** `buildFHSEnv` is the general builder: you list `targetPkgs` / `multiPkgs`, set `runScript`, and get a store path whose `bin/` wrapper launches your command inside the env. Steam’s packaging uses the same mechanism at scale; `pkgs.steam.run` (often referred to as **steam-run**) exposes Steam’s FHS environment so you can run arbitrary upstream binaries without launching the Steam client — install it via `programs.steam` or add the package to `environment.systemPackages`. Steam-specific options, Proton, and unfree policy are covered in [Gaming: Steam and Proton](gaming-steam-proton.md).

**Choosing a path.**

| | Flatpak | FHS wrapper (`buildFHSEnv`, `steam-run`) |
|--|---------|------------------------------------------|
| Isolation | Sandboxed app + runtime (Flatpak/bwrap) | FHS filesystem view; host store and paths largely visible |
| Updates | `flatpak update`, remote runtimes | Rebuild or re-run the wrapper when nixpkgs changes |
| Typical use | Desktop apps distributed as Flatpaks | Game launchers, vendor `.run` installers, one-off binaries |
| NixOS switch | `services.flatpak.enable` + portals | Custom derivation or Steam module |

**Unfree and licensing.** Flatpak runtimes and apps come from Flatpak remotes, not nixpkgs licenses. FHS wrappers built in nixpkgs may pull unfree packages (Steam is the common case). Allow unfree in host policy when needed — see [configuration.nix](../configuration/configuration-nix.md) and [Gaming: Steam and Proton](gaming-steam-proton.md).

## Examples

Enable Flatpak with portals (Flathub still added imperatively after switch):

```nix
{ pkgs, ... }: {
  xdg.portal.enable = true;
  xdg.portal.extraPortals = with pkgs; [
    xdg-desktop-portal-gtk
  ];
  xdg.portal.config.common.default = "*"; # minimal backend selection; see wayland-and-compositors.md

  services.flatpak.enable = true;
}
```

Minimal custom FHS wrapper for a vendor binary (package expression — put the result in `environment.systemPackages` or a flake `packages` output; illustrative library set):

```nix
pkgs.buildFHSEnv {
  name = "vendor-binary-env";
  targetPkgs = pkgs: with pkgs; [ stdenv.cc.cc zlib libGL ];
  runScript = "bash"; # replace with your binary path inside the env
}
```

Run an unpatched binary through Steam’s environment without opening Steam:

```bash
steam-run ./some-upstream-installer.run
```

(`steam-run` is on `PATH` when `programs.steam.enable = true` or when `pkgs.steam.run` is installed.)

## See also

- [Wayland and compositors](wayland-and-compositors.md) — compositors, `xdg.portal`, sessions
- [Gaming: Steam and Proton](gaming-steam-proton.md) — `programs.steam`, `steam-run`, Proton
- [configuration.nix](../configuration/configuration-nix.md) — host policy, allow-unfree
- [Containers (OCI)](../../11-development/containers-oci.md) — another isolation/packaging model (image export, not desktop apps)

## References

- [NixOS options — `services.flatpak`](https://search.nixos.org/options?query=services.flatpak) — enable switch and package override
- [nixpkgs `flatpak.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/services/desktops/flatpak.nix) — portal assertion, FUSE, D-Bus, systemd wiring
- [nixpkgs manual — FHS environments (`buildFHSEnv`)](https://nixos.org/manual/nixpkgs/unstable/#sec-fhs-environments) — builder arguments and security note
- [nixpkgs `build-fhsenv-bubblewrap`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/build-support/build-fhsenv-bubblewrap/default.nix) — bubblewrap wrapper implementation
- [Flatpak documentation](https://docs.flatpak.org/) — remotes, runtimes, and sandbox model (secondary)
