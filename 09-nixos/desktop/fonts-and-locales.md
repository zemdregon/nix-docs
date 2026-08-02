---
status: complete
---

# Fonts and locales

## Overview

Desktop readability depends on two declarative layers: font packages registered with Fontconfig, and glibc locales wired into `/etc/locale.conf` and the locale archive. Font packages belong in `fonts.packages`, not only `environment.systemPackages`, so Fontconfig can index them and build a system cache. Locale defaults live under `i18n.*`. Keyboard layout and timezone are separate: virtual-console maps use `console.keyMap` (default `"us"`) or mirror XKB when `console.useXkbConfig = true`; graphical sessions use `services.xserver.xkb.*` or compositor settings (see [Wayland and compositors](wayland-and-compositors.md)); clock and calendar timezone is `time.timeZone`. None of those are `i18n.*` options.

## Details

**Installing fonts.** `fonts.packages` lists font store paths (for example `pkgs.dejavu_fonts`). The module feeds those directories into Fontconfig’s cache generation. Putting fonts only in `environment.systemPackages` may install files without registering them for Fontconfig-aware apps. `fonts.enableDefaultPackages` (default `false`; renamed from `enableDefaultFonts`) adds a basic Unicode-oriented set when you want coverage without curating a list: `dejavu_fonts`, `freefont_ttf`, `gyre-fonts`, `liberation_ttf`, `unifont`, `noto-fonts-cjk-sans`, `noto-fonts-cjk-serif`, and `noto-fonts-color-emoji`. Icon and patched fonts (including Nerd Font variants) are packaged in nixpkgs under names like `pkgs.nerd-fonts.*`; attribute names change over time — check your channel rather than copying a fixed list.

With `fonts.fontconfig.enable` on by default, NixOS builds `/etc/fonts` (cache, default families, rendering rules); most desktop setups leave it enabled. Tune rendering under `fonts.fontconfig.*`: `hinting.enable`, `hinting.style` (`none`, `slight`, `medium`, `full`), and `subpixel.rgba` (`none`, `rgb`, `bgr`, `vrgb`, `vbgr`) for LCD subpixel order. `fonts.fontconfig.includeUserConf` (default `true`) keeps Fontconfig reading `~/.config/fontconfig/` — useful alongside [Home Manager dotfile patterns](../../10-home-and-user/home-manager/dotfiles-patterns.md) for per-user overrides without rebuilding the system for every tweak.

**System locale.** `i18n.defaultLocale` sets the glibc locale name (default `"en_US.UTF-8"`) used for `LANG` and as the baseline for messages, collation, and formats. Per-category overrides go in `i18n.extraLocaleSettings` (for example `LC_TIME`, `LC_MONETARY`) without changing the default `LANG`. Character set for a category can be adjusted with `i18n.localeCharsets` when you need non-UTF-8 encodings.

The locale archive comes from `i18n.defaultLocale`, `i18n.extraLocaleSettings`, and `i18n.extraLocales`. List additional locales in `i18n.extraLocales` (format `"nl_NL.UTF-8/UTF-8"`) or set `"all"` to install every glibc locale — each entry adds eval and build cost, so list only what you need. The older `i18n.supportedLocales` option is largely auto-computed and deprecated for manual edits; prefer `i18n.extraLocales` when adding locales beyond what the defaults imply.

## Examples

Minimal desktop fonts plus mixed locale categories (in [configuration.nix](../configuration/configuration-nix.md)):

```nix
{ pkgs, ... }: {
  fonts.enableDefaultPackages = true;
  fonts.packages = with pkgs; [
    noto-fonts
    # Check your nixpkgs channel for current nerd-fonts attribute names:
    nerd-fonts.jetbrains-mono
  ];

  i18n.defaultLocale = "en_US.UTF-8";
  i18n.extraLocaleSettings = {
    LC_TIME = "de_DE.UTF-8";
    LC_MONETARY = "de_DE.UTF-8";
  };

  console.useXkbConfig = true;
  services.xserver.xkb.layout = "us";
  time.timeZone = "Europe/Berlin";
}
```

Add a non-default locale without installing everything:

```nix
{
  i18n.defaultLocale = "en_US.UTF-8";
  i18n.extraLocales = [ "ja_JP.UTF-8/UTF-8" ];
}
```

## See also

- [Wayland and compositors](wayland-and-compositors.md) — graphical keyboard layout outside `console.*`
- [configuration.nix](../configuration/configuration-nix.md) — where host-wide `i18n` and `fonts` options usually live
- [Home Manager dotfile patterns](../../10-home-and-user/home-manager/dotfiles-patterns.md) — user-level Fontconfig under `~/.config/fontconfig/`

## References

- [NixOS option search — `fonts.packages`](https://search.nixos.org/options?query=fonts.packages)
- [NixOS option search — `fonts.fontconfig`](https://search.nixos.org/options?query=fonts.fontconfig)
- [NixOS option search — `i18n.defaultLocale`](https://search.nixos.org/options?query=i18n.defaultLocale)
- [nixpkgs `packages.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/config/fonts/packages.nix) — `fonts.packages`, `enableDefaultPackages`
- [nixpkgs `fontconfig.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/config/fonts/fontconfig.nix) — Fontconfig cache, hinting, subpixel, `includeUserConf`
- [nixpkgs `i18n.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/config/i18n.nix) — `defaultLocale`, `extraLocaleSettings`, `extraLocales`, locale archive
