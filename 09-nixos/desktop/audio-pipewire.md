---
status: complete
---

# Audio and PipeWire

## Overview

On current NixOS, PipeWire is the usual desktop audio stack: a user-session daemon with optional ALSA, PulseAudio-protocol, and JACK compatibility layers. Enable it with `services.pipewire.enable = true`, turn on the shims your apps need (`alsa`, `pulse`, and optionally `jack`), and keep the classic PulseAudio daemon off so it does not fight `pipewire-pulse`. WirePlumber is the default session manager when PipeWire is enabled. Desktop modules such as Plasma 6 may default PipeWire on; minimal or tiling setups still need explicit ALSA/Pulse flags. Host policy lives in [configuration.nix](../configuration/configuration-nix.md); device firmware is separate — see [Firmware and microcode](../configuration/firmware-and-microcode.md).

## Details

**Core enable and compatibility layers.** `services.pipewire.enable` starts PipeWire (socket-activated user units by default). `services.pipewire.alsa.enable` redirects ALSA clients through PipeWire; `services.pipewire.pulse.enable` runs the `pipewire-pulse` PulseAudio-protocol shim. `services.pipewire.jack.enable` exposes JACK-compatible libraries for DAWs and low-latency tools. On x86_64, `services.pipewire.alsa.support32Bit = true` builds 32-bit ALSA plugins so older or 32-bit binaries (common in games) can reach the same stack — the Steam module can set this when PipeWire ALSA is on; see [Gaming: Steam and Proton](gaming-steam-proton.md).

**Do not mix with classic PulseAudio.** `services.pipewire.audio.enable` defaults to `true` when any of `alsa.enable`, `pulse.enable`, or `jack.enable` is on. When PipeWire acts as the sound server (`audio.enable`), NixOS asserts that `services.pulseaudio.enable` is `false`; enabling ALSA or Pulse shims with `audio.enable = false` also fails the module assertion. Leave the standalone PulseAudio service disabled; older configs may still mention `hardware.pulseaudio.enable` — confirm the current option name on [search.nixos.org](https://search.nixos.org/options?query=services.pulseaudio). Likewise, enable either PipeWire JACK emulation or `services.jack.jackd.enable`, not both (JACK-only PipeWire setups may keep `audio.enable` off).

**Realtime scheduling.** `security.rtkit.enable = true` is widely used with PipeWire so realtime threads can be granted safely. The PipeWire module also sets PAM limits for the `@pipewire` group; rtkit is optional but commonly recommended for desktop latency.

**Session manager.** `services.pipewire.wireplumber.enable` defaults to the same value as `services.pipewire.enable`. WirePlumber handles routing, default devices, and much Bluetooth/headset policy. The older `pipewire-media-session` path was removed upstream (NixOS 23.05+); do not re-enable it. Fine-grained WirePlumber tweaks can go through `services.pipewire.wireplumber.extraConfig` when needed; many installs need no changes.

**Drop-in configuration.** Override upstream defaults with `services.pipewire.extraConfig`. Sub-attrs `pipewire`, `pipewire-pulse`, `client`, and `jack` each write named drop-ins under the matching `/etc/pipewire/<name>.conf.d/` tree (for example `extraConfig.pipewire."10-clock"` → `/etc/pipewire/pipewire.conf.d/10-clock.conf`). Use dotted property names as string keys where PipeWire expects flat JSON (see module examples). Latency and clock tuning belong here; values depend on hardware and workload, so treat snippets as patterns to adjust rather than fixed recommendations.

**System-wide mode.** `services.pipewire.systemWide = true` runs system units instead of per-user ones and creates a `pipewire` group; users or systemd services that should share the daemon need `extraGroups` / `SupplementaryGroups` membership — NixOS does not add login users automatically. Upstream and the NixOS module description discourage this for normal desktops; prefer user-session PipeWire unless you have a specific multi-user or headless reason.

**Desktop defaults.** `services.desktopManager.plasma6.enable` sets `services.pipewire.enable = lib.mkDefault true` but does not by itself enable every compatibility layer — you still typically set `alsa.enable` and `pulse.enable` for a full desktop. Wayland session and portal context: [Wayland and compositors](wayland-and-compositors.md).

## Examples

Typical desktop (PipeWire + ALSA/Pulse shims + rtkit):

```nix
{
  security.rtkit.enable = true;

  services.pulseaudio.enable = false;

  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true; # x86_64 only; no-op elsewhere
    pulse.enable = true;
    # jack.enable = true;  # optional, for JACK clients
  };
}
```

Illustrative latency-related drop-ins (adjust to your hardware; not prescriptive):

```nix
services.pipewire.extraConfig = {
  pipewire."10-clock" = {
    "context.properties" = {
      "default.clock.rate" = 48000;
      "default.clock.quantum" = 1024;
    };
  };
  pipewire-pulse."10-pulse-props" = {
    "context.properties" = {
      "pulse.min.req" = "1024/48000";
    };
  };
};
```

## See also

- [Wayland and compositors](wayland-and-compositors.md)
- [Gaming: Steam and Proton](gaming-steam-proton.md)
- [configuration.nix](../configuration/configuration-nix.md)
- [Troubleshooting](../operations/troubleshooting.md)
- [Firmware and microcode](../configuration/firmware-and-microcode.md)

## References

- [search.nixos.org — `services.pipewire`](https://search.nixos.org/options?query=services.pipewire) — option reference for PipeWire, WirePlumber, and compatibility layers
- [nixpkgs `pipewire/pipewire.nix`](https://github.com/NixOS/nixpkgs/blob/nixos-unstable/nixos/modules/services/desktops/pipewire/pipewire.nix) — assertions, ALSA/Pulse/JACK wiring, `extraConfig`, `systemWide`
- [nixpkgs `pipewire/wireplumber.nix`](https://github.com/NixOS/nixpkgs/blob/nixos-unstable/nixos/modules/services/desktops/pipewire/wireplumber.nix) — WirePlumber enable default and `extraConfig`
- [NixOS Wiki — PipeWire](https://wiki.nixos.org/wiki/PipeWire) — community patterns; verify options against search.nixos.org
