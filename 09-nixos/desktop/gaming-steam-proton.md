---
status: complete
---

# Gaming: Steam and Proton

## Overview

Steam on NixOS is enabled through the NixOS module `programs.steam`, not Home Manager. The module installs Steam in an FHS-compatible environment (`steam` plus `steam-run`), turns on 32-bit graphics support, and enables `hardware.steam-hardware` for controller udev rules. Proton and other compatibility tools are managed inside Steam (Valve’s Proton builds); nixpkgs does not replace that workflow — the module focuses on packaging, graphics, audio, and optional extras such as Gamescope or third-party compat tools.

## Details

**Enable and unfree policy.** `programs.steam.enable = true` adds `pkgs.steam` and `pkgs.steam.run` to `environment.systemPackages`. Steam and its dependencies are unfree; set `nixpkgs.config.allowUnfree = true` or an `allowUnfreePredicate` that includes the steam-related names on your channel (for example `steam`, `steam-original`, `steam-unwrapped`, `steam-run` — confirm with `lib.getName` on the packages you actually pull). See [configuration.nix](../configuration/configuration-nix.md) for where host policy lives.

**FHS and graphics.** The module sets `hardware.graphics.enable` and `hardware.graphics.enable32Bit` so OpenGL/Vulkan and 32-bit titles can load system libraries into Steam’s environment. That ties into the same graphics stack as other desktop workloads; for why FHS wrappers exist, see [Flatpak and FHS](flatpak-and-fhs.md). GPU firmware and drivers are configured separately — see [Firmware and microcode](../configuration/firmware-and-microcode.md).

**Audio.** When PipeWire ALSA or PulseAudio is enabled, the module turns on the corresponding 32-bit support (`services.pipewire.alsa.support32Bit` or `services.pulseaudio.support32Bit`) so 32-bit games can reach the audio stack. Details: [PipeWire and audio](audio-pipewire.md).

**Firewall helpers.** Optional booleans open the ports the module defines — you do not hand-configure port lists when using these flags:

- `programs.steam.remotePlay.openFirewall` — Remote Play (TCP/UDP ranges documented in the module)
- `programs.steam.dedicatedServer.openFirewall` — Source dedicated server (27015)
- `programs.steam.localNetworkGameTransfers.openFirewall` — local game transfers (27040; shares peer-discovery UDP with Remote Play when either is on)

**Extra tools and compat layers.** `programs.steam.extraPackages` adds packages into Steam’s FHS environment (for example `gamescope`). `programs.steam.extraCompatPackages` lists packages with a `steamcompattool` output; the module sets `STEAM_EXTRA_COMPAT_TOOLS_PATHS` so Steam can pick up Proton-GE-style tools alongside Valve Proton. Use `programs.steam.package` to override the default `pkgs.steam` wrapper instead of putting a custom Steam in `environment.systemPackages`.

**Gamescope session.** `programs.steam.gamescopeSession.enable` registers a Wayland session named `steam` that launches Steam under Gamescope and defaults `programs.gamescope.enable` on. Suboptions `args`, `env`, and `steamArgs` pass through to the wrapper script; default `steamArgs` are `-tenfoot` and `-pipewire-dmabuf`. Compositor and session context: [Wayland and compositors](wayland-and-compositors.md).

**Other module options.** `programs.steam.extest.enable` loads the extest library for Steam Input on Wayland. `programs.steam.protontricks.enable` installs protontricks wired to the same compat-tool paths. `programs.steam.fontPackages` defaults to package entries from `fonts.packages` (merged into Steam’s FHS env) for CJK and other fontconfig needs.

**Proton.** Enable Proton per game in Steam’s UI (Steam Play settings). The NixOS module does not install a standalone “Proton” system package as the primary path; optional `extraCompatPackages` supplement what Steam ships.

## Examples

Minimal enable with targeted unfree allowance:

```nix
{ config, lib, pkgs, ... }: {
  nixpkgs.config.allowUnfreePredicate = pkg:
    lib.elem (lib.getName pkg) [
      "steam"
      "steam-original"
      "steam-unwrapped"
      "steam-run"
    ];

  programs.steam.enable = true;
}
```

Optional Gamescope-driven Steam session and a compat tool (adjust package names to your channel):

```nix
{
  programs.steam = {
    enable = true;
    gamescopeSession.enable = true;
    extraCompatPackages = with pkgs; [ proton-ge-bin ];
  };
}
```

Remote Play through the host firewall:

```nix
{
  programs.steam = {
    enable = true;
    remotePlay.openFirewall = true;
  };
}
```

## See also

- [Flatpak and FHS](flatpak-and-fhs.md)
- [PipeWire and audio](audio-pipewire.md)
- [Wayland and compositors](wayland-and-compositors.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Firmware and microcode](../configuration/firmware-and-microcode.md)

## References

- [nixpkgs `steam.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/programs/steam.nix) — `programs.steam` options, graphics/audio wiring, firewall rules, Gamescope session
- [NixOS options search — `programs.steam`](https://search.nixos.org/options?query=programs.steam)
- [nixpkgs manual — Allowing unfree packages](https://nixos.org/manual/nixpkgs/unstable/#sec-allow-unfree) — required for Steam packages
- [NixOS Wiki — Steam](https://wiki.nixos.org/wiki/Steam) — community notes (secondary to module and options above)
