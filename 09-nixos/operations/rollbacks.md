---
status: complete
---

# Rollbacks

## Overview

When a NixOS rebuild leaves the system in a bad state, you return to a previous [generation](../../02-concepts/generation.md) that still exists in the store—not by undoing file edits. Generations that have not been garbage-collected remain bootable and activatable. That is the practical side of [immutability and rollback](../../01-philosophy/immutability-and-rollback.md); how generations attach to the boot loader is covered in [Generations and boot](../architecture/generations-and-boot.md).

## Details

**Boot into an older generation.** The boot loader exposes previous configurations that have not been GC’d. Under GRUB they appear in the submenu **NixOS - All configurations**; systemd-boot likewise lists prior generations. Use this when the new generation fails to boot or is unusable after login.

**Make that generation the boot default.** After you have booted an older generation, it is active for the running system but is not necessarily the default for the next reboot. Set the default with:

```bash
# /run/current-system/bin/switch-to-configuration boot
```

`/run/current-system` is the generation you are running now, so this registers *that* closure as the boot default without needing to know its generation number.

**Rollback from a running system.** If the machine still boots and you can open a shell:

```bash
# nixos-rebuild switch --rollback
```

That activates the previous system generation and makes it the boot default. It is equivalent to running `switch-to-configuration switch` on the corresponding profile link:

```bash
# /nix/var/nix/profiles/system-N-link/bin/switch-to-configuration switch
```

where `N` is the generation number you want.

**List available generations.** Inspect the system profile links:

```bash
$ ls -l /nix/var/nix/profiles/system-*-link
```

(Or `nixos-rebuild list-generations` for a tabular summary—documented in `man nixos-rebuild`, available since NixOS 23.11.) Only generations still linked here can be selected at boot or activated with `switch-to-configuration`.

**Garbage collection removes rollback targets.** Old generations are GC roots. Blind `nix-collect-garbage` / deleting generations after a bad upgrade can erase the only working closure. Keep enough generations (or delay GC) until you know the new config is good. See [Upgrades](upgrades.md) for the upgrade workflow that produces new generations.

**Prefer `test` before making a risky change the boot default.** `nixos-rebuild test` activates the new config in the running system but does **not** change the boot default—so a lockup or misconfiguration is often fixable with a reboot into the previous default. That is the preventive counterpart to rollback; details of `switch` / `boot` / `test` are in [rebuild switch / boot / test](rebuild-switch-boot-test.md). If you still cannot recover, see [Troubleshooting](troubleshooting.md).

### Boundaries (what this page is not)

- [Garbage collection](../../04-store-and-build/garbage-collection.md) and generation pruning policy.
- [Upgrades](upgrades.md)—how new generations are produced.
- [Troubleshooting](troubleshooting.md) symptom tables—broader failure diagnosis.

## Examples

```bash
# See what generations still exist
ls -l /nix/var/nix/profiles/system-*-link

# Running system is broken but boots: go back one generation
sudo nixos-rebuild switch --rollback

# Activate a specific generation (replace 268 with the number from ls)
sudo /nix/var/nix/profiles/system-268-link/bin/switch-to-configuration switch

# After booting an older entry from the boot menu, make it the default
sudo /run/current-system/bin/switch-to-configuration boot

# Risky change: try without changing boot default first
sudo nixos-rebuild test
```

At the firmware/boot-loader menu, open **NixOS - All configurations** (GRUB) or the equivalent systemd-boot generation list and pick a known-good entry when the newest generation will not start.

## References

- [NixOS manual — Rolling Back Configuration Changes](https://nixos.org/manual/nixos/stable/index.html#sec-rollback)
- [NixOS manual — Changing Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config) (`switch` / `boot` / `test`)

## See also

- [rebuild switch / boot / test](rebuild-switch-boot-test.md)
- [Upgrades](upgrades.md)
- [Troubleshooting](troubleshooting.md)
- [Generations and boot](../architecture/generations-and-boot.md)
- [Generation](../../02-concepts/generation.md)
- [Immutability and rollback](../../01-philosophy/immutability-and-rollback.md)
