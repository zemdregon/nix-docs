---
status: complete
---

# Specialisations

## Overview

**Specialisations** are extra NixOS system closures built alongside the base configuration. Each named entry under `specialisation` is a full system toplevel linked from the parent at `$out/specialisation/<name>`. With the default `inheritParentConfig = true`, a specialisation extends the parent module tree; with `false`, it is a separate configuration that does not include the parent’s options. Nested `specialisation` definitions inside a child are ignored.

## Details

**Option shape.** `specialisation` is an attribute set of submodules (default `{}`). Each entry has:

| Option | Role |
|--------|------|
| `configuration` | Arbitrary NixOS config (imports and option values). Nested specialisations are ignored. |
| `inheritParentConfig` | Bool, default `true`. When `true`, the child extends the overall system config; when `false`, it is a completely differently configured system. |

Names must not contain `/` (asserted by the module).

**Build layout.** The parent system builder creates `$out/specialisation/` and symlinks each child’s `system.build.toplevel` under its name. After activation, those closures are available under `/run/current-system/specialisation/<name>/`.

**Runtime switch.** The option documentation shows activating a specialisation without a full rebuild path of your own, by running that child’s activation script—for example:

```bash
sudo /run/current-system/specialisation/fewJobsManyCores/bin/switch-to-configuration test
```

Use `switch` instead of `test` when you want the same permanence as a normal activation (bootloader / default generation behavior follows `switch-to-configuration` semantics). Kernel or other boot-time-only changes still need a reboot into a boot entry that loads that specialised toplevel.

**`nixos-rebuild --specialisation`.** `nixos-rebuild switch` and `test` accept `--specialisation name` (short `-c name`). When the flag is **omitted**, switch and test activate the **base, unspecialised system**—even if you are currently running a specialisation. With the flag, rebuild still builds all specialisations and makes them bootable; it then activates the named specialisation instead of the base. You can move from base → specialisation or between specialisations this way.

**Boot.** Rebuild operations that build the generation (including plain `switch` and `test`, with or without `--specialisation`) build all specialisations and make them **bootable** alongside the base system. How they appear in the boot menu depends on your [bootloader](partitioning-and-bootloaders.md); upstream notes that child configurations are directly accessible when the **parent** generation is the boot default. Prefer a reboot when the specialised config changes the kernel or other settings that activation cannot fully apply live.

**Overrides.** When inheriting the parent, later definitions in the child’s `configuration` compete with parent values via the usual [module system](../architecture/module-system.md) priority rules (`mkForce`, `mkDefault`, and friends)—same as any other module merge, not a specialisation-specific API.

## Examples

Minimal invented attrset (illustrative; not a full host config):

```nix
{ lib, ... }: {
  specialisation = {
    fewJobs = {
      configuration = {
        nix.settings.max-jobs = 1;
      };
    };

    kiosk = {
      inheritParentConfig = false;
      configuration = {
        system.nixos.tags = [ "kiosk" ];
        services.getty.autologinUser = "alice";
        users.users.alice = {
          isNormalUser = true;
          uid = 1001;
        };
      };
    };
  };
}
```

Activate `fewJobs` after the parent generation is current:

```bash
sudo /run/current-system/specialisation/fewJobs/bin/switch-to-configuration switch
# or:
sudo nixos-rebuild switch --specialisation fewJobs
```

Return to the base system (no specialisation active):

```bash
sudo nixos-rebuild switch
```

## See also

- [configuration.nix](configuration-nix.md)
- [Partitioning and bootloaders](partitioning-and-bootloaders.md)
- [Generations and boot](../architecture/generations-and-boot.md)
- [Activation script](../architecture/activation-script.md)
- [Rebuild, switch, boot, and test](../operations/rebuild-switch-boot-test.md)

## References

- [NixOS option search: `specialisation`](https://search.nixos.org/options?query=specialisation) — option declarations and runtime switch example
- [nixpkgs `specialisation.nix`](https://github.com/NixOS/nixpkgs/blob/master/nixos/modules/system/activation/specialisation.nix) — module source (`inheritParentConfig`, nested ignore, store layout)
- [`nixos-rebuild(8)` man source](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/ni/nixos-rebuild-ng/nixos-rebuild.8.scd) — `--specialisation` / `-c` (also `man nixos-rebuild` locally)
- [Introduction to NixOS specialisations (Tweag, 2022)](https://www.tweag.io/blog/2022-08-18-nixos-specialisations/) — secondary pattern article (boot-menu examples)
