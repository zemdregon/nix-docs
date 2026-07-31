---
status: complete
---

# Troubleshooting

## Overview

Common NixOS failure modes and what to try first. Prefer fixing config and using documented recovery (`test`, boot menu, `--rollback`, store `--repair`) over inventing one-off procedures. Symptom → cause cheat sheet: [FAQ: common errors](../../cheatsheets/faq-common-errors.md). Related ops: [rebuild actions](rebuild-switch-boot-test.md), [rollbacks](rollbacks.md), [upgrades](upgrades.md), [activation](../architecture/activation-script.md), [systemd integration](../architecture/systemd-integration.md), [generations and boot](../architecture/generations-and-boot.md).

## Details

### Decision tree (order of attack)

1. **Classify** — eval (before “building …”), build (builder exit / hash mismatch), activation (`switch`/`test` after the system closure is built), or boot (machine will not come up on the new generation). Match the symptom table in [FAQ: common errors](../../cheatsheets/faq-common-errors.md), then return here for the longer recipe.
2. **Eval** — fix options/types; use `nixos-option`, `nixos-rebuild repl`, and `--show-trace` on the rebuild.
3. **Build** — re-run with `-L` / `--print-build-logs`; then `nix log` on the failed `.drv` or store path. Deeper: [debugging builds](../../04-store-and-build/debugging-builds.md).
4. **Activation vs unit** — activation-script failure (rebuild exits during `switch-to-configuration`) versus a systemd unit that fails after activation or on a later boot — see below and [systemd integration](../architecture/systemd-integration.md). First commands: `systemctl status UNIT` and `journalctl -u UNIT -b` (or `-xe` / follow during the rebuild).
5. **Unbootable or locked up** — boot a previous generation from the bootloader, or `nixos-rebuild switch --rollback` if the machine still runs. Prefer `nixos-rebuild test` for risky changes. Details: [rollbacks](rollbacks.md).
6. **Store / disk** — repair with `--repair` / `nix-store --verify …`; free space on `/boot`, `/nix`, or root — see disk sections below.

### Evaluation errors (unknown option, type mismatch, conflicting definitions)

**Symptoms:** `nixos-rebuild` fails before building; messages like “The option … does not exist”, “is not a …”, or conflicting / multiple definitions.

**What to try:**

- Fix the configuration: typo’d option path, wrong type, or two modules setting incompatible values.
- Inspect the merged value: `nixos-option OPTION` (for example `nixos-option services.xserver.enable`).
- Explore interactively: `nixos-rebuild repl` — configuration is in `config`; `:r` reloads after edits.
- Re-run with `--show-trace` for a fuller stack when the error site is unclear.

### Infinite recursion during eval

**Symptoms:** Eval aborts with “infinite recursion” while evaluating modules.

**What to try:** Conditionals that branch on `config.…` with plain `if` often close a cycle. Use `mkIf` so the condition is delayed into individual definitions — see [mkIf / mkMerge / mkOrder](../modules/mkIf-mkMerge-mkOrder.md).

### Failed builds during `nixos-rebuild`

**Symptoms:** Eval succeeds; a derivation’s builder exits non-zero, or a fixed-output hash mismatches. The rebuild prints a store/drv path.

**What to try:**

- Stream builder output on the next attempt: pass `-L` / `--print-build-logs` to the underlying `nix` invocation (for example `nixos-rebuild switch --print-build-logs`, or set logging on the Nix command your wrapper uses).
- After failure, print the stored log (Nix looks under `/nix/var/log/nix/drvs` and in substituter log URLs):

  ```bash
  nix log /nix/store/….drv
  # or a realized output path if you have it
  nix log /nix/store/…-package-version
  ```

  `nix log` is part of the experimental `nix-command` feature; enable it if your install does not already (see the Nix manual for `nix log`). Prefer it over digging under `/nix/var/log/nix/drvs` by hand.
- Keep a failed build tree when you need files on disk: classic `nix-build -K` / `--keep-failed` on the failing attribute when applicable — see [debugging builds](../../04-store-and-build/debugging-builds.md).
- Hash mismatch on a fetcher: update the declared hash; do not bypass FOD checks.

### Activation failure vs systemd unit failure

These overlap in symptoms but happen at different stages. Both can surface while `nixos-rebuild switch` or `test` runs, because activation restarts affected units. How NixOS wires units and reload/restart during switch: [systemd integration](../architecture/systemd-integration.md). What `$out/activate` runs: [activation script](../architecture/activation-script.md).

| | Activation failure | Systemd unit failure |
|---|-------------------|----------------------|
| **When** | During `switch-to-configuration` while the rebuild command is still running — often while `$out/activate` or its snippets run | After activation completes, or on a later boot/restart of the service |
| **Typical signs** | Rebuild exits non-zero; messages from `activate` or “Failed to start …” before `nixos-rebuild` finishes; `dry-activate` preview shows script errors | `nixos-rebuild` may succeed; `systemctl status UNIT` shows `failed` or restart loop; problem persists across reboots until config or runtime state is fixed |
| **First look** | Rebuild output and `journalctl -f` on another tty during the switch; activation-script snippets and ordering | `systemctl status UNIT`, then `journalctl -u UNIT -b -e`; compare with the previous generation if the service worked before |

**What to try (activation):**

- Prefer `nixos-rebuild test` for risky changes: activates without making the generation the boot default, so a reboot returns to the last `switch`/`boot` default ([Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)).
- Inspect custom `system.activationScripts` and `dry-activate` output for the failing snippet.
- Roll back or boot an older generation if activation leaves the system unusable — [rollbacks](rollbacks.md), [generations and boot](../architecture/generations-and-boot.md).

**What to try (unit failure after activation):**

- `journalctl -u UNIT -xe` and `journalctl -b -p err` for this boot.
- Fix the service config or runtime preconditions (permissions, missing state, wrong port); activation only applies declarative unit files — it does not fix application-level misconfiguration.
- If the unit never worked in the new generation but worked before, diff config or roll back to confirm which option change broke it.

### Unbootable system (boot stage)

**Symptoms:** The system closure built and activation may have succeeded, but the new generation will not reach multi-user target — hangs, emergency shell, or immediate reboot loop.

**What to try:**

- At the bootloader, boot a previous generation (GRUB: **NixOS - All configurations**; systemd-boot lists prior entries). See [generations and boot](../architecture/generations-and-boot.md).
- On a running system that still works enough: `nixos-rebuild switch --rollback`. After booting an older menu entry, make it the default with `/run/current-system/bin/switch-to-configuration boot`. Details: [rollbacks](rollbacks.md).

### Store corruption after a crash

**Symptoms:** Missing or wrong store paths, hash mismatches, builds complaining about corrupt closures (often after power loss; Ext4 may zero unsynced files).

**What to try** (from the NixOS manual, Nix Store Corruption):

- Closure of the system config: `nixos-rebuild switch --repair` — checks paths in the closure and rebuilds or redownloads on hash mismatch.
- Full store: `nix-store --verify --check-contents --repair` — corrupt paths are redownloaded from a binary cache when available; otherwise they cannot be repaired.
- Broader Nix DB / substituter quirks (malformed SQLite, unreachable caches): [nix.dev Troubleshooting](https://nix.dev/guides/troubleshooting).

### Substituter or network failures

**Symptoms:** Builds stall or fail with “cannot download”, timeout, 401/403, or “no substituter”; hash verification errors when fetching from a cache.

**What to try:**

- Confirm `substituters` and `trusted-public-keys` in `nix.conf` (or NixOS `nix.settings`) match the caches you expect — see [binary caches](../../04-store-and-build/binary-caches.md) and [trusted users and substituters](../../05-cli-and-tooling/config/trusted-users-and-substituters.md).
- Test reachability to the cache URL; corporate proxies and offline hosts need matching `netrc` / proxy settings in Nix config.
- If substituters are unreachable, Nix falls back to building from source when possible — expect long rebuilds, not an instant fix.
- After store corruption or partial downloads, `--repair` paths from the store-corruption section above.

### `/boot` full

**Symptoms:** Rebuild fails while updating bootloader entries; little free space on the boot partition.

**What to try:** Delete old system generations carefully (they are GC roots), then run `nixos-rebuild boot` or `nixos-rebuild switch` so bootloader entries and `/boot` contents are refreshed. See [generations and boot](../architecture/generations-and-boot.md).

### `/nix` or root filesystem full

**Symptoms:** `No space left on device` during builds or `switch`; `nixos-rebuild` fails before or after building; `df` shows `/` or `/nix` at 100%.

**What to try:**

- Check space: `df -h / /nix /boot` (layout varies — store may be on `/` or a separate `/nix` mount).
- Free store space with garbage collection, but remember generations and profiles are GC roots — deleting old generations before `nix-store --gc` frees more than GC alone. See [garbage collection](../../04-store-and-build/garbage-collection.md).
- Avoid deleting paths under `/nix/store` by hand; use GC and generation management so live system closures stay intact.
- If builds trigger emergency GC repeatedly, review `min-free` / `max-free` in Nix settings — documented in [garbage collection](../../04-store-and-build/garbage-collection.md).
- Separate issue from `/boot` full: bootloader kernels/initrds live on `/boot`; store paths live under `/nix/store`.

### User services still on old units after `switch`

**Symptoms:** System services restarted as expected; `systemd.user` units did not start/stop.

**What to try:** Documented limitation — `nixos-rebuild` does not start/stop user services automatically; it only runs a `daemon-reload` for users that already have running user services. Restart affected units manually (`systemctl --user …`). See [rebuild actions](rebuild-switch-boot-test.md) and [activation](../architecture/activation-script.md).

### Channel vs flake / unexpected package versions

**Symptoms:** Rebuilds pull different nixpkgs than expected; “I upgraded but nothing changed” or the reverse.

**Decision checklist — which model does this host use?**

1. **Root channel:** as root, `nix-channel --list | grep nixos`. A line like `https://channels.nixos.org/nixos-… nixos` means channel-based rebuilds (default `nixos-rebuild switch` reads root’s `nixos` channel).
2. **Flake:** `/etc/nixos/flake.nix` exists and rebuilds use an explicit flake path, e.g. `nixos-rebuild switch --flake /etc/nixos#hostname` or a wrapper that passes `--flake`. Lockfile at `flake.lock` pins inputs.
3. **Mixed confusion:** a flake config can still ignore channels; conversely, editing `configuration.nix` without updating the channel or lockfile leaves you on the old nixpkgs. Match your upgrade step to the model you actually rebuild with.

**What to try:**

- Channel path: update root’s channel, then rebuild — [upgrades](upgrades.md) (channel section), [Channel](../../02-concepts/channel.md).
- Flake path: update lockfile (`nix flake update` or targeted input bumps), then rebuild with `--flake` — [upgrades](upgrades.md) (flake section), [Flake](../../02-concepts/flake.md).
- Multi-host drift: confirm each machine’s channel or flake input, not just your laptop — [remote deploy](remote-deploy.md).

### NixOS containers and isolation

**Symptoms:** Expecting VM-like security boundaries from `containers.*` / `nixos-container`.

**What to know:** NixOS containers are not perfectly isolated; root inside the container can affect the host. Do not give container root to untrusted users. Details: [containers and nspawn](../services/containers-and-nspawn.md).

### Where to look for logs

| Situation | First command |
|-----------|----------------|
| Unit failed after switch | `systemctl status UNIT` then `journalctl -u UNIT -b -e` |
| Activation / switch in progress | `journalctl -f` (second tty) while `nixos-rebuild …` runs |
| Errors this boot | `journalctl -b -p err` |
| Failed package build | `nix log /nix/store/….drv` (and rebuild with `-L`) |
| Eval stack | `nixos-rebuild … --show-trace` |

For deeper store/build failure workflows, see [debugging builds](../../04-store-and-build/debugging-builds.md).

## Examples

```bash
# Inspect a merged option
nixos-option networking.hostName

# Explore config in a REPL
sudo nixos-rebuild repl

# Eval with a fuller stack
sudo nixos-rebuild switch --show-trace

# Risky change without changing the boot default
sudo nixos-rebuild test

# Preview activation without applying (activation-script debugging)
sudo nixos-rebuild dry-activate

# Stream build logs on a rebuild (Nix --print-build-logs / -L)
sudo nixos-rebuild switch --print-build-logs

# After a failed build: log for the printed .drv (needs nix-command)
nix log /nix/store/….drv

# Previous generation on a still-running system
sudo nixos-rebuild switch --rollback

# After booting an older menu entry, make it the default
sudo /run/current-system/bin/switch-to-configuration boot

# Repair system closure after suspected store corruption
sudo nixos-rebuild switch --repair

# Scan and repair the whole store (slow)
sudo nix-store --verify --check-contents --repair

# Which nixpkgs source does this host use?
sudo nix-channel --list | grep nixos
test -f /etc/nixos/flake.nix && echo flake layout

# Disk pressure on store vs boot
df -h / /nix /boot

# Service / activation logs
systemctl status sshd
journalctl -u sshd -b -e
journalctl -b -p err
```

## See also

- [FAQ: common errors](../../cheatsheets/faq-common-errors.md)
- [rebuild switch / boot / test](rebuild-switch-boot-test.md)
- [rollbacks](rollbacks.md)
- [upgrades](upgrades.md)
- [activation script](../architecture/activation-script.md)
- [systemd integration](../architecture/systemd-integration.md)

## References

- [Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config) — `switch` / `test` / `boot`, user-services warning, `nixos-rebuild repl`
- [Rolling Back](https://nixos.org/manual/nixos/stable/index.html#sec-rollback) — boot menu, `nixos-rebuild switch --rollback`, `switch-to-configuration boot`
- [What happens during a system switch](https://nixos.org/manual/nixos/stable/index.html#ch-switching) — activation / unit restart flow
- [Nix Store Corruption](https://nixos.org/manual/nixos/stable/index.html#sec-nix-store-corruption) — `nixos-rebuild switch --repair`, `nix-store --verify --check-contents --repair`
- [NixOS Boot Entries](https://nixos.org/manual/nixos/stable/index.html#sect-nixos-gc-boot-entries) — `/boot` full: clear old profiles, then `nixos-rebuild boot|switch`
- [Container Management](https://nixos.org/manual/nixos/stable/index.html#ch-containers) — incomplete isolation warning
- [Modularity](https://nixos.org/manual/nixos/stable/index.html#sec-modularity) — `nixos-option`
- [Delaying Conditionals](https://nixos.org/manual/nixos/stable/index.html#sec-option-definitions-delaying-conditionals) — infinite recursion from plain `if` on `config`
- [`nix log`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-log.html) — build logs from local `/nix/var/log/nix/drvs` or substituters (`nix-command`, experimental)
- [nix.dev Troubleshooting](https://nix.dev/guides/troubleshooting) — substituters, Nix DB repair tips
