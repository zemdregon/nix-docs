---
status: draft
---

# Backups and restore

## Overview

NixOS [generations](../../02-concepts/generation.md) and [rollbacks](rollbacks.md) recover the **system closure**—packages, `/etc`, systemd units, and other paths declared in configuration—not arbitrary runtime state. User data under `/home`, database files in `/var/lib`, and application state you never put in `configuration.nix` survive or die independently of `nixos-rebuild switch --rollback`.

Treat **system rollback** and **data backup** as complementary: generations undo a bad config; backups restore files and databases after disk loss, ransomware, or operator error. On [impermanent](../configuration/impermanence.md) hosts the split is sharper—rebuild recreates undeclared paths on every boot, so anything on your persist list that matters off-box needs an explicit backup job.

## Details

### What generations cover (and do not)

Each successful `nixos-rebuild switch` or `boot` adds a system profile generation under `/nix/var/nix/profiles`. Rolling back activates an older closure via [rebuild switch / boot / test](rebuild-switch-boot-test.md) or the boot menu ([Rollbacks](rollbacks.md)). That restores whatever was in the evaluated NixOS configuration at that point.

It does **not** rewind:

- Contents of `/var/lib` (PostgreSQL, Docker layers, service state) unless those paths are managed purely by NixOS modules in config.
- Home directories, unless you declare users and home paths in config (unusual for large trees).
- Off-store secrets decrypted at activation into `/run` or `/var/lib`.
- Remote object storage, DNS records, or anything outside the machine.

After hardware failure, you need both a working system generation (or install media + config) **and** restored data.

### Declarative backup modules

nixpkgs ships NixOS modules that wrap [Restic](https://restic.net/) and [BorgBackup](https://www.borgbackup.org/) with systemd services and timers.

**`services.restic.backups`** — one attribute set per named job. Each job defines `paths` (or `command` for stdin backups such as `pg_dumpall`), `repository` / `repositoryFile`, and `passwordFile` or `environmentFile` for credentials. Backends include local paths, SFTP, S3-compatible stores, and rclone remotes. The module generates `restic-backups-<name>.service` and, when `timerConfig` is non-null (default: daily), a matching timer. Use `pruneOpts` for retention, `initialize = true` on first deploy, and `exclude` for caches and `/nix`.

**`services.borgbackup.jobs`** — client jobs with `paths`, `repo`, `encryption`, `compression`, and `startAt` (systemd calendar). **`services.borgbackup.repos`** — SSH-restricted borg serve endpoints on the same host. Remote repos use `environment.BORG_RSH` and keys outside the store.

Both modules schedule via systemd; override timing with `timerConfig` (restic) or `startAt` / timer-related job options (borg). Inspect units with `systemctl list-timers` and logs with `journalctl -u restic-backups-*` or `borgbackup-job-*`.

### Credentials and secrets

Repository passwords, cloud API keys, and SSH private keys must **not** appear as plain strings in evaluated Nix—they land in the world-readable store. Use `passCommand` (borg), `passwordFile`, or `environmentFile` (restic) pointing at paths populated by [secrets strategies](../configuration/secrets-strategies.md), [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md), or deploy-time files under `/run` or root-only locations. The borg module manual example uses `/run/keys/borgbackup_passphrase`; restic’s module requires `passwordFile` or `environmentFile`.

### Impermanence and backup scope

With an ephemeral root, NixOS and impermanence recreate undeclared paths at boot. Your persist volume holds declared survivors (`/var/lib/…`, SSH keys, logs). Decide per path:

| Category | Typical handling |
|----------|------------------|
| Rebuild from flake/channel | System closure, `/etc/nixos`, declared users |
| On persist volume | Survives reboot; still vulnerable to disk/site loss—back up if irreplaceable |
| Ephemeral only | Lost every reboot—back up continuously if it matters |
| Remote SaaS / DB | Backup via app-native dump or restic `command` job |

Document the persist list alongside backup jobs so a new machine can be reprovisioned and data restored in a known order.

### ZFS / Btrfs snapshots

Local snapshots ([ZFS and Btrfs](../configuration/zfs-and-btrfs.md)) give fast point-in-time recovery on the same disk or pool. They are not off-site backup: fire, theft, btrfs scrub failures, or `zfs destroy` on the wrong dataset still need separate copies. Pair snapshots with restic/borg to remote or cold storage.

### Restore workflow

1. **Recover hardware or provision a new host** — install NixOS or boot from install media; apply the same flake/channel config (or a known-good generation).
2. **Restore data before or after switch** — stop the affected service, restore files into the correct path (`/var/lib/postgresql`, `/var/lib/docker`, etc.) or replay SQL from a dump. Borg: `borg extract`; restic: `restic restore` (wrapper scripts `restic-<jobname>` exist when `createWrapper = true`).
3. **Apply system config if needed** — `nixos-rebuild switch` when the restored data expects newer module options or users.
4. **Verify** — start services, run application health checks, and confirm backup timers are active.

Practice restores on a VM or spare machine periodically; an untested backup is a guess.

### Boundaries (what this page is not)

- [Rollbacks](rollbacks.md) and [Garbage collection](../../04-store-and-build/garbage-collection.md)—generation lifecycle only.
- Full [secrets strategies](../configuration/secrets-strategies.md) or agenix/sops wiring.
- Filesystem layout and scrub tuning—[ZFS and Btrfs](../configuration/zfs-and-btrfs.md).

## Examples

Minimal restic job to a local repository (password file supplied outside eval):

```nix
{
  services.restic.backups.home = {
    paths = [ "/home" "/var/lib/some-app" ];
    exclude = [ "/home/*/.cache" "/nix" ];
    repository = "/mnt/backup/restic-home";
    passwordFile = "/run/agenix/restic-password";
    initialize = true;
    timerConfig = {
      OnCalendar = "daily";
      Persistent = true;
    };
    pruneOpts = [
      "--keep-daily 7"
      "--keep-weekly 4"
      "--keep-monthly 6"
    ];
  };
}
```

Borg job with passphrase via `passCommand` (pattern from the NixOS manual):

```nix
{
  services.borgbackup.jobs.etc = {
    paths = [ "/etc/nixos" "/var/lib/postgresql" ];
    exclude = [ "/nix" ];
    repo = "user@backup-host:repo";
    doInit = true;
    encryption = {
      mode = "repokey-blake2";
      passCommand = "cat /run/agenix/borg-passphrase";
    };
    environment = {
      BORG_RSH = "ssh -i /run/agenix/borg-backup-key";
    };
    compression = "auto,zstd";
    startAt = "hourly";
  };
}
```

Database via restic stdin (service runs as `postgres` user in the generated unit):

```nix
{ pkgs, ... }: {
  services.restic.backups.pg = {
    command = [
      "${pkgs.sudo}"
      "-u"
      "postgres"
      "${pkgs.postgresql}/bin/pg_dumpall"
    ];
    repository = "s3:s3.example.com/mybucket/pg";
    passwordFile = "/run/agenix/restic-password";
    environmentFile = "/run/agenix/restic-s3-env";
    timerConfig.OnCalendar = "02:00";
    pruneOpts = [ "--keep-daily 14" "--keep-weekly 8" ];
  };
}
```

After deploy, trigger a manual run and list snapshots:

```bash
sudo systemctl start restic-backups-home.service
sudo restic-home snapshots
# or: sudo borg list --rsh 'ssh -i /run/agenix/borg-backup-key' user@backup-host:repo
```

## References

- [NixOS option search — `services.restic`](https://search.nixos.org/options?query=services.restic)
- [NixOS option search — `services.borgbackup`](https://search.nixos.org/options?query=services.borgbackup)
- [NixOS manual — BorgBackup](https://nixos.org/manual/nixos/stable/index.html#module-services-borgbackup) (stable manual; restic is documented via module options and upstream Restic docs)
- [Restic documentation](https://restic.readthedocs.io/)

## See also

- [Rollbacks](rollbacks.md)
- [rebuild switch / boot / test](rebuild-switch-boot-test.md)
- [Impermanence](../configuration/impermanence.md)
- [ZFS and Btrfs](../configuration/zfs-and-btrfs.md)
- [Secrets strategies](../configuration/secrets-strategies.md)
- [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md)
