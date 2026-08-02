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

Semantics follow the NixOS manual ([Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)) and `nixos-rebuild(8)`. Matrix columns are authoritative for build / boot / activate; notes below add mechanics not shown in the table.

**`switch`.** Internally: build `config.system.build.toplevel`, register a new system-profile generation, then run `switch-to-configuration switch`.

**`test`.** Reboot restores the previous boot default.

**`boot`.** Live system unchanged until reboot.

**`build`.** Leaves a `result` symlink to the system closure; may run as a normal user.

**`dry-activate`.** Asks `switch-to-configuration` what it would do under `test` (e.g. which systemd units would restart). The printed list is **not** guaranteed complete (`nixos-rebuild(8)`).

**`dry-build`.** Pair with `dry-activate` when you want both build planning and activation preview.

**`build-vm`.** Builds a QEMU VM for sandboxed testing (`./result/bin/run-*-vm`). The VM has no host data—configure users explicitly (e.g. `mutableUsers = false`, temporary `initialHashedPassword`); delete `*.qcow2` after such changes so they take effect.

**`repl`.** Nix REPL with system `config` loaded (tab completion; `:r` to reload). See [Troubleshooting](troubleshooting.md) for eval failures.

**`list-generations`.** Generation number, build time, NixOS/kernel versions, optional `--json`. Complements `/nix/var/nix/profiles/system-*-link` in [Rollbacks](rollbacks.md).

### Generations and activation

`switch` and `boot` that update the system profile add a generation under `/nix/var/nix/profiles`; the running system is `/run/current-system`. Older generations remain until GC—see [Rollbacks](rollbacks.md).

For `switch` / `test`, activation: bootloader update (when required) → stop units → `$out/activate` → reload/restart systemd → start units. See [Activation script](../architecture/activation-script.md) and *What happens during a system switch?* in the NixOS manual.

### Named profiles, specialisations, flakes

**Named profiles.** `nixos-rebuild switch -p test` installs under a separate profile (GRUB submenu “NixOS - Profile 'test'”).

**Specialisations.** Without `--specialisation`, `switch` and `test` activate the unspecialised base system. Pass `--specialisation NAME` (or `-c`) for a named one—see [Specialisations](../configuration/specialisations.md).

**Flakes.** Same actions via `--flake …`; input refresh before rebuild is [Upgrades](upgrades.md).

### Boundaries (what this page is not)

- [Upgrades](upgrades.md)—channel bumps, flake input updates, and pinning policy.
- [Rollbacks](rollbacks.md) deep dive—boot menu generation selection and recovery workflows.
- [Remote deploy](remote-deploy.md)—SSH rebuild to other hosts.

## Examples

Commands below match the NixOS manual and `nixos-rebuild(8)`. They require a NixOS host (or a built system closure) to run.

```bash
# sudo -i
# nixos-rebuild switch
# nixos-rebuild test
# nixos-rebuild boot
# nixos-rebuild build           # may run as normal user
# nixos-rebuild dry-activate
# nixos-rebuild dry-build
# nixos-rebuild switch -p test
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
