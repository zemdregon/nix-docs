---
status: complete
---

# configuration.nix

## Overview

**configuration.nix** is the primary NixOS module where you declare host-specific system settings: bootloader, users, networking, enabled services, and packages. On a classic install it lives at `/etc/nixos/configuration.nix`; in a [flake](../../02-concepts/flake.md) setup the same module tree is usually wired through `nixosConfigurations.<name>`. Edits do nothing to the running system until you [rebuild](../operations/rebuild-switch-boot-test.md).

## Details

**Module shape.** A configuration file is a function that returns an attribute set of option definitions:

```nix
{ config, pkgs, ... }: {
  imports = [ ./hardware-configuration.nix ];
  # option definitions …
}
```

The function arguments come from the [module system](../architecture/module-system.md). `config` reads other modules' values; `pkgs` is the package set for this system. Extra arguments (`...`) allow modules to accept labels such as `lib` when passed by the evaluator.

**What belongs here.** Host choices that differ between machines: `boot.loader`, `users.users`, `networking`, `services.*`, `environment.systemPackages`, and similar top-level options. Machine-generated facts—disk layout, kernel modules detected at install—belong in [hardware-configuration.nix](hardware-configuration.md), which you typically import rather than merge by hand.

**Imports, not monoliths.** Split concerns across files and pull them in with `imports`. Shared snippets, role-specific fragments, and optional [profiles](imports-and-profiles.md) keep the entry module readable. One large paste of unrelated options is harder to review and reuse.

**Applying changes.** Saving `configuration.nix` only updates source text. Nix evaluates the module tree into a new system [generation](../../02-concepts/generation.md); activation happens on `nixos-rebuild switch` (or the flake equivalent). Until then, services, `/etc`, and the boot menu stay on the previous generation.

**Finding options.** Every option name, type, and default is documented on [search.nixos.org](https://search.nixos.org/options) and in the [NixOS options appendix](https://nixos.org/manual/nixos/stable/options). On a NixOS machine, `man configuration.nix` summarizes common patterns.

## Examples

Minimal illustrative entry module (~15 lines):

```nix
{ config, pkgs, ... }: {
  imports = [ ./hardware-configuration.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "demo";
  networking.networkmanager.enable = true;

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };

  environment.systemPackages = with pkgs; [ git vim ];

  # Set once at install to the NixOS release you started on; do not bump casually.
  system.stateVersion = "26.05";
}
```

Illustrative only (real hosts also need filesystem/boot facts from `hardware-configuration.nix`). After editing, rebuild to activate—see [rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md).

## References

- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — configuration and changing the system
- [NixOS option search](https://search.nixos.org/options)
- [NixOS options appendix](https://nixos.org/manual/nixos/stable/options)

## See also

- [hardware-configuration.nix](hardware-configuration.md)
- [Imports and profiles](imports-and-profiles.md)
- [Module system](../architecture/module-system.md)
- [Rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md)
- [Flake](../../02-concepts/flake.md)
