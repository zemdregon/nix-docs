---
status: complete
---

# Wayland and compositors

## Overview

NixOS desktop sessions are built from display managers, desktop environments (or standalone Wayland compositors), and XDG Desktop Portals for file pickers, screenshare, and similar integration. Plasma 6 and GNOME moved off `services.xserver.desktopManager.*` to `services.desktopManager.plasma6.enable` and `services.desktopManager.gnome.enable`; older desktops such as XFCE and MATE still use the `services.xserver.desktopManager.*` tree. Full DE modules usually wire portals, session packages, and much of the graphics stack; tiling compositors like Hyprland and Sway need explicit portal setup or rely on their program modules to add one.

## Details

**Desktop environments.** `services.desktopManager.plasma6.enable` (replacing `services.xserver.desktopManager.plasma6`) pulls in a Wayland-first Plasma stack: it enables `programs.xwayland`, sets `xdg.portal` with KDE, GTK, and KWallet portals (default `configPackages` from `plasma-workspace`), defaults `services.pipewire.enable`, registers Plasma sessions, and sets `services.displayManager.defaultSession` to `"plasma"` by default. When SDDM is already enabled, the module configures the SDDM package, theme, and `services.displayManager.sddm.wayland.enable` with KWin; it does not set `services.displayManager.sddm.enable` itself. `services.desktopManager.gnome.enable` turns on GNOME core services, enables `xdg.portal` with `xdg-desktop-portal-gnome` and `xdg-desktop-portal-gtk`, and defaults NetworkManager. It does not enable a display manager by itself (`nixos-generate-config` may seed GDM alongside GNOME, but `gnome.enable` alone does not set `services.displayManager.gdm.enable`). Enable SDDM or GDM explicitly (SDDM for Plasma, GDM for GNOME is the usual pairing).

**Display managers and default session.** `services.displayManager.sddm.enable` and `services.displayManager.gdm.enable` start the login greeter. `services.displayManager.defaultSession` picks which session file runs when the user does not choose one. Program modules for Hyprland and Sway add their packages to `services.displayManager.sessionPackages` so a DM can offer those sessions.

**Tiling compositors.** `programs.hyprland.enable` installs Hyprland, optional `programs.hyprland.xwayland.enable` (default `true`), and optional `programs.hyprland.withUWSM` for UWSM-based systemd session integration. The module imports the wayland-session helper (WLR portal disabled), enables `xdg.portal` with `xdg-desktop-portal-hyprland`, and adds Hyprland to `services.displayManager.sessionPackages`. `programs.sway.enable` installs Sway (optional `programs.sway.xwayland.enable`, default `true`), imports wayland-session (WLR and GTK extra portals), and sets `xdg.portal.config.sway` (GTK default backend; WLR for screencast and screenshot). Compositor dotfiles often live in Home Manager; see [dotfiles patterns](../../10-home-and-user/home-manager/dotfiles-patterns.md).

**XDG Desktop Portals.** `xdg.portal.enable = true` requires a non-empty `xdg.portal.extraPortals` (module assertion). Portal 1.17+ expects `xdg.portal.config` or `xdg.portal.configPackages`; otherwise the module warns. For pre-1.17-style “first portal wins” behavior on a minimal compositor setup, `xdg.portal.config.common.default = "*";` is the documented escape hatch. Enabling multiple full DEs on one system can conflict on portal packages; [specialisations](../configuration/specialisations.md) let you boot separate profiles instead.

**X11 pieces still in play.** Many configs still set `services.xserver.enable = true` for Xwayland, legacy X11 apps, or keyboard layout via `services.xserver.xkb.layout` / `variant`. Full DE modules often enable Xwayland and related pieces themselves. For 32-bit OpenGL (Wine and similar), `hardware.graphics.enable32Bit` remains the relevant switch in the X/graphics chapter.

## Examples

Plasma 6 with SDDM (Wayland session defaults from the Plasma module):

```nix
{ ... }: {
  services.displayManager.sddm.enable = true;
  services.desktopManager.plasma6.enable = true;
}
```

GNOME with GDM:

```nix
{ ... }: {
  services.displayManager.gdm.enable = true;
  services.desktopManager.gnome.enable = true;
}
```

Hyprland (the program module enables `xdg-desktop-portal-hyprland`; add a DM if you want a graphical login):

```nix
{ ... }: {
  programs.hyprland.enable = true;
  services.displayManager.sddm.enable = true;
  services.displayManager.defaultSession = "hyprland";
}
```

Standalone compositor without a portal-wiring program module — GTK portal plus legacy-style backend selection:

```nix
{ pkgs, ... }: {
  xdg.portal.enable = true;
  xdg.portal.extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
  xdg.portal.config.common.default = "*";
}
```

## See also

- [configuration.nix](../configuration/configuration-nix.md)
- [Specialisations](../configuration/specialisations.md)
- [systemd integration](../architecture/systemd-integration.md)
- [Audio and PipeWire](audio-pipewire.md)
- [Flatpak and FHS](flatpak-and-fhs.md)
- [Home Manager dotfiles patterns](../../10-home-and-user/home-manager/dotfiles-patterns.md)

## References

- [NixOS manual — Graphical user interfaces (X)](https://nixos.org/manual/nixos/unstable/#sec-x11) — display managers, desktop managers, keyboard layout, 32-bit graphics
- [nixpkgs `x-windows.chapter.md`](https://github.com/NixOS/nixpkgs/blob/master/nixos/doc/manual/configuration/x-windows.chapter.md) — upstream manual source for the X/Wayland chapter
- [nixpkgs `portal.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/config/xdg/portal.nix) — `xdg.portal.enable`, `extraPortals`, `config`, `configPackages`
- [nixpkgs `plasma6.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/services/desktop-managers/plasma6.nix) — Plasma 6 portals, SDDM Wayland settings, session registration
- [search.nixos.org — `services.desktopManager.plasma6`](https://search.nixos.org/options?query=services.desktopManager.plasma6)
- [search.nixos.org — `programs.hyprland`](https://search.nixos.org/options?query=programs.hyprland)
