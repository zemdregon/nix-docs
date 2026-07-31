---
status: complete
---

# Generations and Boot

## Overview

On NixOS, each successful `nixos-rebuild` that updates the system [profile](../../02-concepts/profile.md) adds a new **system generation**: a numbered snapshot of the full system closure (kernel, init, services, `/etc`). Boot loaders expose one entry per retained generation; picking an older entry at boot is the core rollback story. See [Generation](../../02-concepts/generation.md) for the general model and [Immutability and rollback](../../01-philosophy/immutability-and-rollback.md) for why this matters.

## Details

**Where generations live.** System generations are profile snapshots under `/nix/var/nix/profiles/`: `system-N-link` symlinks point at store closures, and `system` points at the current generation (same pattern as any Nix [profile](../../02-concepts/profile.md)). The running system is usually `/run/current-system`; that can differ from the profile default after `nixos-rebuild test` or after booting an older menu entry without re-registering the default.

**One boot menu entry per generation.** Configured boot loaders—commonly [systemd-boot or GRUB](../configuration/partitioning-and-bootloaders.md) via `boot.loader.*`—install an entry for each system generation that has not been garbage-collected. Selecting an older entry loads that generation’s closure. There is no in-place mutation of `/` or `/etc`; you boot a different store path.

**`switch` vs `boot` (and `test`).**

| Command | Running system | Boot loader default |
|---------|----------------|---------------------|
| `nixos-rebuild switch` | Activates now ([activation script](activation-script.md)) | Updates default entry to this generation |
| `nixos-rebuild boot` | Unchanged until reboot | Adds/updates entry; next reboot boots the new generation |
| `nixos-rebuild test` | Activates now | Unchanged (reboot returns to previous default) |

Use `boot` when you want the new configuration only after a clean restart (for example after a kernel/initrd change). Use `test` for risky changes you may want to abandon by rebooting. Full action matrix: [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md).

**Rollback paths.**

- **Boot menu** — choose a previous generation before the system fully starts (GRUB: submenu **NixOS - All configurations**; systemd-boot lists prior generations similarly). After booting an older entry, make it the default with `/run/current-system/bin/switch-to-configuration boot`.
- **`nixos-rebuild switch --rollback`** — activate the *previous* system generation (the one before the current `system` profile generation) and set it as the boot default. `--rollback` does not take a generation number.
- **Explicit generation** — run that generation’s activator, e.g. `/nix/var/nix/profiles/system-42-link/bin/switch-to-configuration switch`. Moving the profile pointer alone (`nix-env -p /nix/var/nix/profiles/system --switch-generation N`) is not enough; you still need `switch-to-configuration` to activate and update boot entries.

Operational detail and failure cases: [Rollbacks](../operations/rollbacks.md).

**GC roots and disk.** Each retained generation is a garbage-collection root. Old generations keep their entire closures alive until you delete them (`nix-env -p /nix/var/nix/profiles/system --delete-generations …`, or `nix-collect-garbage` after removing roots). Unbounded history costs disk; a full `/boot` may also need a rebuild (`nixos-rebuild boot` or `switch`) after pruning so the boot partition is rewritten.

**Not user profile generations.** System generations (`nixos-rebuild`, boot menu) are separate from user [profile](../../02-concepts/profile.md) generations (`nix-env`, `nix profile`). Rolling back one does not roll back the other.

## Examples

```bash
# List system generations (number, build time, kernel, NixOS version; since NixOS 23.11)
sudo nixos-rebuild list-generations

# Activate the previous generation now and make it the boot default
sudo nixos-rebuild switch --rollback

# Activate a specific generation (replace 42 with the generation number)
sudo /nix/var/nix/profiles/system-42-link/bin/switch-to-configuration switch

# Build and register for next boot only; running system unchanged
sudo nixos-rebuild boot

# Inspect profile links on disk
ls -l /nix/var/nix/profiles/system*
```

At boot, use the firmware/boot-loader menu to pick the prior **NixOS** generation when the current system fails to start. After recovery, register the running generation as the boot default if needed:

```bash
sudo /run/current-system/bin/switch-to-configuration boot
```

## References

- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config) — `switch` / `test` / `boot`
- [NixOS manual — Rolling Back Configuration Changes](https://nixos.org/manual/nixos/stable/index.html#sec-rollback) — boot menu, `--rollback`, `system-N-link`
- [Nix manual — Profiles](https://nix.dev/manual/nix/stable/package-management/profiles.html) — generations, profile symlinks, atomic switch
- [NixOS options index](https://nixos.org/manual/nixos/stable/options) — `boot.loader.*` (systemd-boot, GRUB, EFI)

## See also

- [Generation](../../02-concepts/generation.md)
- [Profile](../../02-concepts/profile.md)
- [Activation script](activation-script.md)
- [Rollbacks](../operations/rollbacks.md)
- [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md)
- [Partitioning and bootloaders](../configuration/partitioning-and-bootloaders.md)
- [Immutability and rollback](../../01-philosophy/immutability-and-rollback.md)
