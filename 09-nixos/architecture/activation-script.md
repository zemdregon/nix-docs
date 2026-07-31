---
status: complete
---

# Activation Script

## Overview

After a NixOS system [derivation](../../02-concepts/derivation.md) is built, **activation** applies that closure to the running machine: updating `/etc`, creating users, running one-shot setup, and coordinating systemd unit changes. `nixos-rebuild switch`, `test`, `boot`, and `dry-activate` all invoke **`switch-to-configuration`** (in the system closure at `$out/bin/switch-to-configuration`), which drives that process. Custom hooks go in `system.activationScripts`; most service lifecycle work belongs in declarative systemd units instead.

## Details

**What activation does.** For `switch` and `test`, `switch-to-configuration` compares the current system (systemd state, `/etc/fstab`, and related data) with the new configuration, computes stop/start/reload actions, then applies them in a fixed order (see below). For `switch` and `boot`, the bootloader is updated first so the new configuration is next to boot (unless `NIXOS_NO_SYNC=1`, the store is synced to disk first). The built-in **`etc`** snippet materializes most of `/etc` from the new closure; other default snippets are listed under **Default snippets**.

**`switch-to-configuration` order (switch / test).** After planning unit and mount changes from `/etc/fstab` and current systemd state, actions always run in this sequence:

1. **Stop** affected units (`systemctl stop`)
2. **Run activation script** (`$out/activate`)
3. **Check** whether activation requested additional unit restarts
4. **Reexec systemd** if needed (`systemd daemon-reexec`)
5. **Reset failed** unit state (`systemctl reset-failed`)
6. **Reload systemd** (`daemon-reload`, then user instances)
7. **Reactivate sysinit** (`systemctl restart sysinit-reactivation.target`) so early-boot units restart before “normal” units
8. **Reload**, **restart**, then **start** units as planned
9. **Report** units that failed or were newly started during the switch

Use `STC_DEBUG=1` for more verbose logging and `STC_DISPLAY_ALL_UNITS=1` to print every unit action (defaults filter noisy output). For risky changes, `nixos-rebuild test` runs the same activation path without updating the boot default; `dry-activate` previews without applying. See [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md) and the manual’s system-switch chapter.

**Default snippets.** NixOS merges these into every activation script (disable only if you know why):

| Snippet | Role |
|---------|------|
| `binsh` | Symlink `/bin/sh` to the runtime shell |
| `etc` | Populate `/etc` from the closure, including generated systemd units; **not** `passwd` / `group` / `shadow` |
| `users` | Manage accounts and `/etc/passwd`, `/etc/group`, `/etc/shadow`; create home directories |
| `specialfs` | Mount pseudo filesystems such as `/proc` and `/sys` |
| `usrbinenv` | Symlink `/usr/bin/env` |
| `modprobe` | Set the path used for module auto-loading |

**Custom snippets.** `system.activationScripts` is an attribute set of shell fragments merged into `$out/activate`. Each entry may be:

- a multiline string (shell commands), or
- an attribute set with `text` and optional `deps` (names of other snippets that must run first).

The builder topologically sorts snippets by `deps`. Snippets should be **idempotent and fast**—they run on every boot and every `nixos-rebuild switch`, not only on first install.

**Dry activation.** Set `supportsDryActivation = true` on a snippet to include it when running `nixos-rebuild dry-activate`. In that mode, `switch-to-configuration` sets `$NIXOS_ACTION` to `dry-activate`; snippets that opt in must not mutate the system when that variable is set. Dry activation also prints planned systemd stop/start/reload actions without applying them (as if `test` were run).

**Per-user activation.** `system.userActivationScripts` defines snippets run by a systemd user oneshot (`nixos-activation.service`) when the system is activated—same idempotency constraints as system snippets. Search [system.userActivationScripts](https://search.nixos.org/options?show=system.userActivationScripts) for the option schema; user-level ongoing work usually belongs in Home Manager or `systemd --user` units instead.

**Rebuild actions (via `switch-to-configuration`).**

| Action | Boot loader | Activate running system |
|--------|-------------|-------------------------|
| `switch` | Update default entry | Yes |
| `boot` | Add/update entry for next boot | No |
| `test` | No bootloader change | Yes |
| `dry-activate` | No | No (preview only) |

See [Generations and boot](generations-and-boot.md) for how `switch` and `boot` relate to system generations.

**Prefer systemd over ad-hoc scripts.** The manual explicitly recommends `StateDirectory`, `CacheDirectory`, and related unit options—or `preStart` when those are not enough—over custom activation for service directories and runtime layout. Reserve `system.activationScripts` for one-shot system-wide setup that is not naturally a service: global files outside `/etc`, one-time migrations, or ordering work that must run before units start. See [systemd integration](systemd-integration.md) and [service patterns](../services/service-patterns.md).

### Activation vs unit failure (operator view)

Symptoms overlap during `switch`/`test` because activation restarts units. Use this table to classify quickly; the full decision tree and recovery steps are in [troubleshooting](../operations/troubleshooting.md).

| Symptom / cause | Activation script | Systemd unit |
|-----------------|-------------------|--------------|
| **When it surfaces** | While `switch-to-configuration` runs, often inside `$out/activate` | After activation finishes, or on a later boot/restart |
| **Typical sign** | `nixos-rebuild` exits non-zero; snippet error in rebuild output | Rebuild may succeed; `systemctl status UNIT` shows `failed` or a restart loop |
| **Snippet exits non-zero** | Rebuild fails mid-activate; partial switch | — |
| **Snippet not idempotent** | Second switch or boot breaks state | — |
| **Missing `deps`** | Races with `etc` / `users`; flaky or wrong files | — |
| **Long-running work in activation** | No per-task unit; hard to restart; no `journalctl -u` trail | Prefer a `.service` with logs and `systemctl restart` |

**What to try first (activation):** `nixos-rebuild dry-activate` (optionally with `STC_DEBUG=1`), then `test` for risky changes; inspect custom snippets and `deps`. **Unit failures:** `journalctl -u UNIT -b -e` after a successful rebuild.

## Examples

Custom snippet with dry-activate guard and dependency on `etc`:

```nix
{
  system.activationScripts.my-setup = {
    deps = [ "etc" ];
    supportsDryActivation = true;
    text = ''
      if [ "$NIXOS_ACTION" = "dry-activate" ]; then
        echo "would update shared state"
      else
        install -d -m 0755 /var/lib/myapp
      fi
    '';
  };
}
```

The `deps = [ "etc" ];` line ensures `/etc` from the new configuration exists before this snippet runs. For service-owned directories, prefer `systemd.services.<name>.serviceConfig.StateDirectory` instead of `install -d` here.

Rebuild and debug commands:

```bash
# Apply now and set boot default
sudo nixos-rebuild switch

# Apply now without touching the boot loader
sudo nixos-rebuild test

# Preview activation and systemd changes (no mutations)
sudo nixos-rebuild dry-activate

# Noisier switch-to-configuration output while debugging
sudo STC_DEBUG=1 STC_DISPLAY_ALL_UNITS=1 nixos-rebuild switch
```

## References

- [NixOS manual (stable) — Activation script](https://nixos.org/manual/nixos/stable/index.html#sec-activation-script)
- [NixOS manual (stable) — What happens during a system switch](https://nixos.org/manual/nixos/stable/index.html#ch-switching)
- [NixOS option search — `system.activationScripts`](https://search.nixos.org/options?show=system.activationScripts)

## See also

- [Generations and boot](generations-and-boot.md)
- [systemd Integration](systemd-integration.md)
- [rebuild switch / boot / test](../operations/rebuild-switch-boot-test.md)
- [Troubleshooting](../operations/troubleshooting.md)
- [Service patterns](../services/service-patterns.md)
- [Generation](../../02-concepts/generation.md)
