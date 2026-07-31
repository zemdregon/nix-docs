---
status: complete
---

# configuration.nix

## Overview

**configuration.nix** is the primary NixOS module where you declare host-specific system settings: bootloader, users, networking, enabled services, and packages. On a classic install it lives at `/etc/nixos/configuration.nix`; in a [flake](../../02-concepts/flake.md) setup the same module tree is wired through `nixosConfigurations.<name>.modules` (see [NixOS configurations in flakes](../../07-flakes/workflows/nixos-configurations.md)). Edits do nothing to the running system until you [rebuild](../operations/rebuild-switch-boot-test.md).

The file is not a special dialect—it is an ordinary [module](../architecture/module-system.md) evaluated like any other. Custom modules you write follow the same shape and can live beside it or in separate repositories.

## Details

**Module shape.** A configuration file is a function that returns an attribute set of option definitions:

```nix
{ config, pkgs, ... }: {
  imports = [ ./hardware-configuration.nix ];
  # option definitions …
}
```

The function arguments come from the module system. `config` reads merged values from other modules; `pkgs` is the package set for this system. The `...` rest pattern lets the evaluator pass extra labels—commonly `lib` for helpers such as `lib.mkMerge` or `lib.optionals`. Nothing about the filename changes how evaluation works; only where the module is imported.

**What belongs here.** Host policy that differs between machines: `boot.loader`, `users.users`, `networking`, `services.*`, `environment.systemPackages`, and similar top-level options. Machine-generated facts—disk layout, detected filesystem UUIDs, kernel modules—belong in [hardware-configuration.nix](hardware-configuration.md), which you import rather than merge by hand. Keep generated hardware facts separate from choices you edit deliberately.

**Imports, not monoliths.** Split concerns across files and pull them in with `imports`. Shared snippets, role-specific fragments, and optional [profiles](imports-and-profiles.md) keep the entry module readable. A single file that mixes unrelated services, desktop policy, and one-off experiments is harder to review, reuse across hosts, and roll back cleanly.

**system.stateVersion.** Set this once at install time to the NixOS release you started on (for example `"26.05"`). It is a compatibility default for stateful data—databases, user home layout expectations, and similar—not a target version to chase on every upgrade. Bumping it without understanding what changed can apply new defaults to existing state and break services. Leave it alone unless release notes or option documentation tell you to update it.

**Applying changes.** Saving `configuration.nix` only updates source text. Nix evaluates the module tree into a new system [generation](../../02-concepts/generation.md); activation happens on `nixos-rebuild switch` (or the flake equivalent, such as `nixos-rebuild switch --flake .#hostname`). Until then, services, `/etc`, and the boot menu stay on the previous generation.

**Finding options.** Every option name, type, and default is documented on [search.nixos.org](https://search.nixos.org/options) and in the [NixOS options appendix](https://nixos.org/manual/nixos/stable/options). On a NixOS machine, `man configuration.nix` summarizes common patterns. Search before inventing ad hoc shell hooks—most behavior already has an option.

**Composition.** NixOS merges every module in `imports` with the same rules: later definitions override earlier ones where options allow it, and `config` exposes the final merged tree. That is why a thin `configuration.nix` that only imports role modules and sets hostname is a valid layout—the entry file names the host; shared logic lives elsewhere.

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

Illustrative only—real hosts also need filesystem and boot facts from `hardware-configuration.nix`. The same shape is checked in as [minimal-configuration.nix](../../meta/examples/minimal-configuration.nix) (not evaluated in this vault). After editing, rebuild to activate; see [rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md). For splitting policy into reusable pieces, see [writing a module](../modules/writing-a-module.md).

## References

- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — configuration and changing the system
- [NixOS option search](https://search.nixos.org/options)
- [NixOS options appendix](https://nixos.org/manual/nixos/stable/options)

## See also

- [hardware-configuration.nix](hardware-configuration.md)
- [Imports and profiles](imports-and-profiles.md)
- [Module system](../architecture/module-system.md)
- [Writing a module](../modules/writing-a-module.md)
- [NixOS configurations in flakes](../../07-flakes/workflows/nixos-configurations.md)
- [Rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md)
- [Flake](../../02-concepts/flake.md)
- [Example corpus](../../meta/examples/README.md) — `minimal-configuration.nix`
