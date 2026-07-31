---
status: complete
---

# Imports and Profiles

## Overview

**Imports** compose NixOS configuration from many [modules](../architecture/module-system.md). Each path in `imports = [ ./hw.nix … ]` is evaluated as a full module—same shape as [`configuration.nix`](configuration-nix.md), with its own `imports`, `options`, and `config`. **NixOS profiles** are predefined modules shipped under `nixpkgs/nixos/modules/profiles/`; you pull them in the same way. They are not the same thing as user or system [profiles](../../02-concepts/profile.md) managed by `nix-env` or `nixos-rebuild`.

## Details

**How imports compose.** The module system merges every imported module into one evaluated `config`. Your entry module stays thin: it lists fragments and sets host-specific overrides. nixpkgs already loads a default module set from `modules/module-list.nix`; you only add imports for your own files, optional upstream profiles, or third-party modules.

**Static import resolution.** `imports` is resolved before the module fixpoint runs—before merged `config` exists. Paths and import lists must therefore be known statically. You cannot choose an import based on `config.services.x.enable` or other option values. When you need values from outside the module tree (flake inputs, computed paths), pass them through `specialArgs` or `_module.args` so they are available as function arguments during import resolution—not by reading `config` inside `imports`.

**Splitting by concern.** A common layout keeps one entry module and imports focused fragments:

| Fragment | Typical contents |
|----------|------------------|
| [`hardware-configuration.nix`](hardware-configuration.md) | Disks, filesystems, kernel modules (often generated at install) |
| `users.nix` | `users.users`, SSH keys, groups |
| `desktop.nix` | Display manager, desktop session, fonts |
| `services.nix` | Web servers, databases, networking services |

The exact filenames are yours; the pattern is one concern per module, composed through `imports`.

**NixOS profiles vs package profiles.** NixOS **profiles** are `.nix` files in [nixpkgs `nixos/modules/profiles/`](https://github.com/NixOS/nixpkgs/tree/master/nixos/modules/profiles) that set bundles of options—for example `headless.nix` for cloud VMs, `minimal.nix` for a smaller default set, `installation-device.nix` for install media, and `clone-config.nix` for editable live-system configs. Importing a profile is importing a module; it does not create or switch a Nix [profile](../../02-concepts/profile.md) symlink or add a [generation](../../02-concepts/generation.md). Profiles are not enabled with a fictional `profiles.*.enable` option—add them to `imports`. The shared word *profile* is unfortunate; keep module profiles and store profiles separate when reading configs and docs.

**Referencing nixpkgs profiles.** Inside a NixOS module, `modulesPath` points at the nixpkgs NixOS modules tree (provided via `specialArgs`). Use it instead of hard-coding `<nixpkgs/nixos/modules/…>` so paths stay correct across channels and flakes:

```nix
{ modulesPath, ... }: {
  imports = [ (modulesPath + "/profiles/headless.nix") ];
}
```

The manual also shows `<nixpkgs/nixos/modules/profiles/profile-name.nix>` for classic installs where that path resolves via `NIX_PATH`.

## Examples

Entry module mixing local fragments and an upstream profile:

```nix
{ config, pkgs, modulesPath, ... }: {
  imports = [
    ./hardware-configuration.nix
    ./users.nix
    ./services.nix
    (modulesPath + "/profiles/headless.nix")
  ];

  networking.hostName = "edge-01";
  # host-specific overrides …
}
```

Each imported file is a module on its own—for example, `./users.nix` might be:

```nix
{ ... }: {
  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };
}
```

For module structure and merge helpers, see [Writing a module](../modules/writing-a-module.md).

## References

- [NixOS manual (stable) — Modularity](https://nixos.org/manual/nixos/stable/index.html#ch-modularity)
- [NixOS manual (stable) — Profiles](https://nixos.org/manual/nixos/stable/index.html#sec-profiles)
- [NixOS profiles in nixpkgs](https://github.com/NixOS/nixpkgs/tree/master/nixos/modules/profiles)

## See also

- [configuration.nix](configuration-nix.md)
- [hardware-configuration.nix](hardware-configuration.md)
- [Module system](../architecture/module-system.md)
- [Profile (store profiles)](../../02-concepts/profile.md)
- [Writing a module](../modules/writing-a-module.md)
