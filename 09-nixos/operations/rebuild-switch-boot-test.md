---
status: complete
---

# nixos-rebuild actions

## Overview

After you edit [`/etc/nixos/configuration.nix`](../configuration/configuration-nix.md) (or a flake-based system config), changes take effect only when you apply them with `nixos-rebuild`. That tool builds a new system [generation](../../02-concepts/generation.md), optionally updates the boot default, and optionally activates the config on the running machine. Which of those steps run depends on the subcommand: `switch`, `test`, `boot`, `build`, `dry-activate`, and related helpers.

Activation (what `switch` and `test` do to the live system) is implemented by [`switch-to-configuration`](../architecture/activation-script.md), which updates the bootloader when asked, runs the activation script, and reconciles systemd units. How generations show up in the bootloader is covered under [Generations and boot](../architecture/generations-and-boot.md). Channel/flake refresh before a rebuild is [Upgrades](upgrades.md); recovering a bad generation is [Rollbacks](rollbacks.md); failure modes are [Troubleshooting](troubleshooting.md).

## Details

### Root and user services

Rebuild commands that activate or change the boot default must run as root: use a root shell or prefix with `sudo -i` (as the NixOS manual recommends).

`nixos-rebuild` does **not** start or stop user services automatically. It only runs a `daemon-reload` for each user that already has running user services. User units may need a manual restart after a switch.

### Action matrix

| Action | Build | Boot default | Activate now | Typical use |
|--------|-------|--------------|--------------|-------------|
| `switch` | yes | yes | yes | Day-to-day apply |
| `test` | yes | no | yes | Risky change; reboot undoes |
| `boot` | yes | yes | no | Next reboot picks it up (e.g. kernel) |
| `build` | yes | no | no | Eval/compile check only |
| `dry-activate` | yes | no | dry-run | Preview unit/activation changes |
| `dry-build` | eval/plan | no | no | Show what would be built (no build) |

Semantics below follow the NixOS manual ([Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)) and `nixos-rebuild(8)`.

**`switch`.** Build the new configuration, make it the boot default, and activate it now (restart system services as needed). This is the usual day-to-day apply. Internally: build `config.system.build.toplevel`, register a new system-profile generation, then run `switch-to-configuration switch`.

**`test`.** Build and activate now, but do **not** set the boot default. A reboot returns to the previous default generation—useful for risky changes you might want to walk away from by rebooting.

**`boot`.** Build and set the boot default, but do **not** activate now. The new generation takes effect on the next reboot. Handy when you want the next boot to pick up kernel/initrd changes without flipping the live system mid-session.

**`build`.** Build only; no activation and no boot-entry change. Leaves a `result` symlink to the system closure. A compile/eval check that the config closes cleanly; may be run as a normal user.

**`dry-activate`.** Build the new configuration, then ask `switch-to-configuration` what it would do under `test`—for example which systemd units would restart—without applying those changes. The printed list is **not** guaranteed complete (`nixos-rebuild(8)`). Useful before a disruptive `switch`.

**`dry-build`.** Show which store paths would be built or substituted without performing the build (planning / dry-run of realization). Complements `dry-activate`, which focuses on activation effects after a successful build.

**`build-vm`.** Build a QEMU VM that contains the desired configuration for sandboxed testing (`./result/bin/run-*-vm` after the build). The VM has no host data: existing user accounts and home directories are unavailable unless you configure users for the VM (for example `mutableUsers = false`, or temporary `initialHashedPassword` values—delete the `*.qcow2` disk image after such changes so they take effect).

**`repl`.** Open a Nix REPL with your system configuration loaded into the `config` variable (tab completion; `:r` to reload). Useful for inspecting option values before rebuilding; see also [Troubleshooting](troubleshooting.md) for eval failures.

**`list-generations`.** List available system generations (generation number, build time, NixOS/kernel versions, and related metadata; optional `--json`). Complements inspecting `/nix/var/nix/profiles/system-*-link` as described in [Rollbacks](rollbacks.md).

### Generations and activation

Each successful `switch` or `boot` that updates the system profile creates a new generation under `/nix/var/nix/profiles`. The running system is `/run/current-system`. Previous generations remain until garbage-collected, which is what makes [rollbacks](rollbacks.md) and the bootloader submenu possible.

For `switch` / `test`, activation roughly: update bootloader when the action requires it → stop units → run `$out/activate` → reload/restart systemd as needed → start units. Details and ordering live in [Activation script](../architecture/activation-script.md) and the NixOS manual chapter *What happens during a system switch?*.

### Named profiles, specialisations, flakes

**Named profiles.** `nixos-rebuild switch -p test` installs the generation under a separate profile so GRUB shows a submenu like “NixOS - Profile 'test'”, keeping experimental generations apart from the main system profile.

**Specialisations.** Without `--specialisation`, `switch` and `test` activate the unspecialised base system (even if you were previously in a specialisation). Pass `--specialisation NAME` (or `-c`) to activate a named one. See [Specialisations](../configuration/specialisations.md).

**Flakes (brief).** With a flake-based host, the same actions apply via `nixos-rebuild switch --flake …` (and the other subcommands with `--flake`). Activation and boot semantics above are unchanged; refreshing flake inputs before rebuild is [Upgrades](upgrades.md).

## Examples

Commands below match the NixOS manual and `nixos-rebuild(8)`. They require a NixOS host (or a built system closure) to run; comments note expected side effects.

```bash
# sudo -i
# nixos-rebuild switch          # build, boot default, activate now
# nixos-rebuild test            # build + activate; reboot undoes boot default
# nixos-rebuild boot            # build + boot default; activate on next reboot
# nixos-rebuild build           # build only (as user is fine)
# nixos-rebuild dry-activate    # build; print planned activation (incomplete list OK)
# nixos-rebuild dry-build       # show what would be built/fetched; do not build
# nixos-rebuild switch -p test  # GRUB submenu “NixOS - Profile 'test'”
# nixos-rebuild list-generations
```

After a bad `switch`, prefer `nixos-rebuild switch --rollback` or the bootloader submenu—see [Rollbacks](rollbacks.md). For channel upgrades that end in `switch`/`boot`, see [Upgrades](upgrades.md).

## References

- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)
- [NixOS manual — What happens during a system switch?](https://nixos.org/manual/nixos/stable/index.html#sec-switching-systems)
- [NixOS manual — Rollbacks](https://nixos.org/manual/nixos/stable/index.html#sec-rollback)
- [`nixos-rebuild(8)` in nixpkgs](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/ni/nixos-rebuild-ng/nixos-rebuild.8.scd) — full action list including `dry-activate`, `dry-build`, `list-generations`

## See also

- [Rollbacks](rollbacks.md)
- [Upgrades](upgrades.md)
- [Troubleshooting](troubleshooting.md)
- [Activation script](../architecture/activation-script.md)
- [Generations and boot](../architecture/generations-and-boot.md)
- [Specialisations](../configuration/specialisations.md)
