---
status: complete
---

# Remote Builders

## Overview

A local Nix installation can **forward builds** to other machines over SSH. That offloads work for **parallelism** and enables **multi-platform builds** in a mostly transparent way: if you build a [derivation](../02-concepts/derivation.md) whose `system` does not match the local machine, Nix can send the build to a remote that supports that platform when one is configured.

This is **build scheduling**, not “point `--store` at a remote forever.” Realized paths come back over [store protocols](store-protocols.md). Trust is two-layered: SSH reachability plus the remote listing the SSH user in `trusted-users`—see [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) (build axis) vs local daemon [trusted users](../14-security-and-trust/trusted-users.md).

## Details

### Requirements

For the local Nix to forward a build, the remote must (Nix remote-builds manual):

- Have Nix installed and on `PATH` for non-interactive SSH sessions
- Run an SSH server (e.g. `sshd`)
- Be reachable from the local machine over the network
- Have the local machine’s public SSH key authorized for the SSH user (e.g. in that user’s `authorized_keys`)
- List the SSH username in [`trusted-users`](../14-security-and-trust/trusted-users.md) on the remote `nix.conf` (see also [trusted-users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md))

Without `trusted-users`, the remote daemon rejects build delegation even when SSH login succeeds. That remote `trusted-users` entry is **not** the same as local daemon trust on the coordinator, and not fleet membership—only permission for that SSH identity to ask the remote daemon to build.

### Multi-user daemon and SSH keys

In a **multi-user** installation the Nix **daemon** (typically running as root) performs builds—not your login user. Implications:

- Use a **passphrase-less** private key; the daemon cannot prompt or use `ssh-agent`.
- Place keys where the daemon user can read them—often `/root/.ssh/` (Linux) or `/var/root/.ssh` (macOS).
- Test as the daemon user, not only as yourself: `sudo ssh -i /root/.ssh/id_remote nix@builder echo ok` (or `su` then `ssh`).

Builds must stay **non-interactive** end to end.

### Testing connectivity

Verify the remote store with (`nix store info` is experimental new CLI; Nix 2.34):

```bash
nix store info --store ssh://username@host
```

To pass a specific identity file, add a query parameter:

```bash
nix store info --store ssh://username@host?ssh-key=/path/to/key
```

If SSH works but the command fails with **`nix: command not found`**, the remote’s non-interactive login shell does not put Nix on `PATH`—fix shell profile or use a wrapper on the remote before retrying.

### Builder specifications (`builders` / `/etc/nix/machines`)

Remote machines are listed as **builder specifications**: a store URI plus optional fields. Separate multiple entries with `;` or a newline. Set them via:

- `--builders` on the command line
- `builders` in `nix.conf`
- An include file: `builders = @/etc/nix/machines` (the default)

After changing `nix.conf`, restart the Nix daemon for the new settings to apply.

Each machine line is space-separated. Only the URI is required; use `-` to leave a field at its default. Fields, in order (`nix.conf` `builders`, stable manual):

1. Store URI — `ssh://[user@]host[:port]` (`ssh://` may be omitted for compatibility; hostname may be an `~/.ssh/config` alias). In practice NixOS `nix.buildMachines` and distributed-build tutorials also emit `ssh-ng://` for full remote-daemon peers; see [store protocols](store-protocols.md).
2. System types — comma-separated (e.g. `x86_64-linux` or `i686-linux,x86_64-linux`); default is the local platform
3. SSH identity file
4. Max parallel jobs on that machine
5. Speed factor (positive integer; preferred when several remotes match)
6. Supported features (must cover a derivation’s `requiredSystemFeatures`)
7. Mandatory features (machine used only if those appear in `requiredSystemFeatures`)
8. Base64-encoded public host key (else SSH `known_hosts`; value often from `base64 -w0`)

**Protocol choice:** `ssh-ng://` is the Nix store protocol used in distributed-build tutorials between NixOS peers with full daemons. Plain `ssh://` remains appropriate when the remote is not a full Nix daemon peer. On NixOS, `protocol = "ssh-ng"` in `nix.buildMachines` generates `ssh-ng://` lines in `/etc/nix/machines`.

When a derivation’s `system` matches a configured remote platform and local execution is not forced, Nix schedules the build on that machine and pulls the realized store paths back over the [store protocol](store-protocols.md). Set `builders-use-substitutes = true` on the local side so remotes may fetch inputs from their own [substituters](binary-caches.md) instead of waiting for uploads (default `false`). Use `max-jobs = 0` (or `--max-jobs 0`) to disable local builds and use only remotes (except derivations with `preferLocalBuild = true`).

### NixOS declarative setup

On a NixOS **coordinator** (the machine that offloads builds), enable distributed builds and declare remotes with module options instead of hand-editing `/etc/nix/machines`:

```nix
{
  nix.distributedBuilds = true;
  nix.settings.builders-use-substitutes = true;

  nix.buildMachines = [
    {
      hostName = "builder.example";
      sshUser = "remotebuild";
      sshKey = "/root/.ssh/id_remotebuild";
      system = "x86_64-linux"; # or systems = [ "x86_64-linux" "aarch64-linux" ];
      protocol = "ssh-ng";
      maxJobs = 8;
      speedFactor = 2;
      supportedFeatures = [ "nixos-test" "big-parallel" "kvm" ];
      publicHostKey = "base64-encoded-host-key"; # optional; avoids known_hosts MITM
    }
  ];
}
```

`nix.buildMachines` writes `/etc/nix/machines` on activation. **`nix.distributedBuilds = true` is required**—defining `buildMachines` alone does not turn on offloading. Match `supportedFeatures` to what each remote actually provides (e.g. `kvm` for VM tests, `big-parallel` for large parallel jobs).

### Remote machine pattern (NixOS)

On each **builder**, create a dedicated system user, authorize the coordinator’s public key, and trust that user for builds:

```nix
{
  users.users.remotebuild = {
    isSystemUser = true;
    group = "remotebuild";
    useDefaultShell = true; # needed for non-interactive SSH sessions
    openssh.authorizedKeys.keys = [ "ssh-ed25519 AAAA... coordinator" ];
  };
  users.groups.remotebuild = {};
  nix.settings.trusted-users = [ "remotebuild" ];
}
```

Copy the real public key from the coordinator’s `/root/.ssh/id_remotebuild.pub` (or equivalent). After `nixos-rebuild switch`, test from the coordinator as root: `ssh remotebuild@builder.example -i /root/.ssh/id_remotebuild nix --version`.

## Examples

**One-off cross-platform build** (from the manual pattern):

```bash
nix build --impure \
  --expr '(with import <nixpkgs> { system = "x86_64-darwin"; }; runCommand "foo" {} "uname > $out")' \
  --builders 'ssh://mac x86_64-darwin'
```

**Several remotes in `nix.conf`:**

```ini
builders = ssh://mac x86_64-darwin ; ssh://beastie x86_64-freebsd
```

**Default machines include:**

```ini
builders = @/etc/nix/machines
```

**Example `/etc/nix/machines` lines** (URI, systems, identity, max jobs, speed factor, supported features, mandatory features):

```text
ssh-ng://remotebuild@builder.example x86_64-linux /root/.ssh/id_remotebuild 8 2 nixos-test,big-parallel,kvm
ssh://nix@scratchy i686-linux /root/.ssh/id_scratchy 8 1 kvm
ssh://nix@itchy    i686-linux /root/.ssh/id_scratchy 8 2
ssh://nix@poochie  i686-linux /root/.ssh/id_scratchy 1 2 kvm benchmark
```

Here `itchy` is preferred for ordinary `i686-linux` builds (higher speed factor) but cannot do `kvm` builds; `poochie` supports `kvm` and requires `benchmark` in the derivation’s `requiredSystemFeatures`.

**Remote `nix.conf` (trusted SSH user):**

```ini
trusted-users = root builder
```

## Failure modes

| Symptom | Likely cause |
|---------|----------------|
| Build never leaves local machine | `nix.distributedBuilds` not enabled (NixOS), or no matching builder for `system` / features |
| SSH OK, build rejected on remote | SSH user missing from remote [`trusted-users`](../14-security-and-trust/trusted-users.md) |
| Hang or prompt during build | Passphrase-protected key; daemon cannot use `ssh-agent` |
| Host key verification failed | Missing `publicHostKey` and no matching `known_hosts` entry for the daemon user |
| Remote selected but build fails | `supportedFeatures` mismatch (`kvm`, `big-parallel`, `nixos-test`, etc.) |
| `nix: command not found` over SSH | Remote non-interactive `PATH` omits Nix |
| Wrong machine chosen | Adjust `speedFactor`, `maxJobs`, or mandatory/supported features |

## References

- [Nix reference manual — Remote builds](https://nix.dev/manual/nix/stable/advanced-topics/distributed-builds.html)
- [Nix reference manual — `nix.conf` / `builders`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-builders) — machine fields, `@/etc/nix/machines`, `builders-use-substitutes`
- [nix.dev tutorial — Setting up distributed builds](https://nix.dev/tutorials/nixos/distributed-builds-setup) — SSH keys, `ssh-ng`, NixOS `nix.buildMachines`
- [NixOS option search — `nix.buildMachines`](https://search.nixos.org/options?query=nix.buildMachines)

## See also

- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — build-trust axis (SSH + remote `trusted-users` ≠ fleet membership)
- [Trusted users](../14-security-and-trust/trusted-users.md) — why the remote SSH user must be trusted
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — local `trusted-users` vs remote builder trust
- [Store protocols](store-protocols.md) — `ssh://` vs `ssh-ng://` and how results are copied back
- [Binary caches](binary-caches.md) — substituting pre-built paths instead of building
- [Machine mesh](../02-concepts/machine-mesh.md) — remote builds as one mesh concern
