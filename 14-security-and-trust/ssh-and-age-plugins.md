---
status: complete
---

# SSH and age plugins

## Overview

NixOS secret tooling ([agenix](../12-deployment-and-infra/agenix-sops-nix.md), [sops-nix](https://github.com/Mic92/sops-nix)) often ties **decrypt identities** on a host to OpenSSH **host private keys**, and **recipients** in Git to the corresponding public keys converted to age format (`ssh-to-age`). That keeps fleet rekeying aligned with machine identity without a separate key ceremony per service.

**age plugins** extend age with hardware-backed or exotic identity types (YubiKey PIV, FIDO2, TPM, Ledger, …). Plugins are separate binaries (`age-plugin-*`) discovered on `PATH` when age or SOPS decrypts. On NixOS, activation must be non-interactive: the plugin binary, any daemons it needs (e.g. `pcscd` for YubiKey), and identity material must be available before `sops-install-secrets` or agenix runs—typically with **no PIN prompts** at boot.

Broader patterns: [Secrets management](secrets-management.md), [Secrets strategies](../09-nixos/configuration/secrets-strategies.md), [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md).

## Details

### Key roles — host, user, hardware

| Material | Typical path / source | Used as age **recipient** (encrypt in repo) | Used as age **identity** (decrypt at activation) | Notes |
|----------|----------------------|-----------------------------------------------|--------------------------------------------------|-------|
| OpenSSH **host** private key | `/etc/ssh/ssh_host_*_key` from `services.openssh.hostKeys` | Public host key → `ssh-to-age -i …` in `.sops.yaml` or agenix `secrets.nix` | Default for sops-nix (`sops.age.sshKeyPaths`); agenix default under `/etc/ssh/` or `age.identityPaths` | Stable per-machine identity; ed25519 host keys are the usual choice |
| OpenSSH **user** private key | `~/.ssh/id_*` | Same conversion for HM-only or laptop recipients | sops-nix HM: `sops.age.sshKeyPaths`; agenix HM: `age.identityPaths` (required) | User-scoped secrets; not the default for fleet hosts |
| age key file | e.g. `/var/lib/sops-nix/key.txt` | `age-keygen -y` public line in creation rules | `sops.age.keyFile` / `sops.age.generateKey`; agenix via `age.identityPaths` | Common when SSH host keys are undesirable; must persist on impermanent roots |
| **Plugin** identity / recipient | Encoded strings (`AGE-PLUGIN-…`, `age1…`) from the plugin | Created by plugin CLI at encrypt time | Plugin binary on `PATH` at decrypt time | Hardware or policy-enforced; boot must not block on PIN unless you accept failed activation |

Host keys answer “which machine may decrypt its own secrets.” User keys answer “which human or HM profile.” Plugin identities answer “which token or secure element holds the key”—usually for operators or high-value keys, not every host in a headless fleet.

### OpenSSH host keys

NixOS generates host keys via `services.openssh.hostKeys` when `services.openssh.enable` is true. sops-nix **defaults** `sops.age.sshKeyPaths` to the **ed25519** entries from that list (see upstream module). Override explicitly when you use another algorithm or a persisted path:

```nix
sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
```

Recipients in `.sops.yaml` or agenix’s secrets map should list the **public** host key converted with [ssh-to-age](https://github.com/Mic92/ssh-to-age) (or agenix’s built-in SSH support). Rebuild after rotating host keys and re-encrypt secrets for the new recipient.

agenix decrypts with host private keys under `/etc/ssh/` by default; point `age.identityPaths` at durable paths if keys live on a persisted volume (impermanence).

### age plugin model

age loads plugins only when a matching plugin **recipient** or **identity** string is used. The CLI looks for a binary named `age-plugin-<name>` on `PATH` and speaks a stdin/stdout protocol ([age plugin package](https://github.com/FiloSottile/age/tree/main/plugin), [age.1 Plugins section](https://github.com/FiloSottile/age/blob/main/doc/age.1.ronn)). Common community plugins:

| Plugin (examples) | Role |
|-------------------|------|
| [age-plugin-yubikey](https://github.com/str4d/age-plugin-yubikey) | PIV slot on YubiKey; often needs `services.pcscd.enable` |
| age-plugin-fido2-hmac | FIDO2 resident / HMAC-secret style identities |
| TPM- / Ledger-backed plugins | Platform-specific; same PATH + activation constraints |

Encrypt on a workstation with the plugin installed; commit ciphertext only. The **build host** does not need the token—only the activation environment on the target (or the operator’s machine for ad-hoc `sops`/`age` edits).

### sops-nix and plugins at activation

Check the [current sops-nix README](https://github.com/Mic92/sops-nix) for option names— they evolve. As of recent upstream modules, **`sops.age.plugins`** accepts a list of packages; sops-nix prepends their `bin` directories to `PATH` for `sops-install-secrets` (activation script and, when used, the `sops-install-secrets` systemd unit’s `path`).

Older setups without that option wrapped the sops package or extended `environment.systemPackages` so `age-plugin-yubikey` (and peers) appeared on PATH during activation—same requirement, manual wiring.

Operational constraints for **non-interactive boot**:

- Plugin binary must be on PATH when secrets install runs.
- YubiKey / smartcard: enable **`pcscd`** (and ensure the token is present if decrypt is host-bound—often avoided for servers).
- Prefer identities that do **not** require a PIN or touch at activation; use hardware-backed keys for operator decrypt or manual `sops edit`, or slot policies that allow boot-time use without interaction.
- Persist any file-based age identity (`sops.age.keyFile`) on durable storage; plugin-only flows still need ciphertext recipients to match what the host can satisfy.

If no plugin, SSH key, or `keyFile` identity matches, activation fails—same as plain age.

### agenix and plugins

agenix invokes `age` with configured **`age.identityPaths`**. Plugin identities are not special-cased in the module: if an identity file contains an `AGE-PLUGIN-…` line (or you rely on age’s plugin discovery for a given recipient), the corresponding **`age-plugin-*` binary must be on PATH** in the agenix activation environment. The same non-interactive and `pcscd` rules apply. agenix is file-per-secret and SSH-centric; sops-nix’s `sops.age.plugins` is the documented NixOS knob for PATH—mirror that pattern for agenix via `environment.systemPackages` or a wrapped `age` if needed.

### Choosing an approach

- **Fleet NixOS hosts, Git-ciphertext secrets:** ed25519 host keys + `ssh-to-age` recipients; default `sops.age.sshKeyPaths` or agenix host-key identities.
- **Home Manager / user secrets:** user SSH key paths in `sops.age.sshKeyPaths` or `age.identityPaths`.
- **Operator or break-glass keys:** age-plugin-yubikey (or similar) as an **additional** recipient; decrypt manually or on a subset of hosts with hardware present and PATH wired.
- **No SSH coupling:** `sops.age.generateKey` / `keyFile` or agenix age key files on persisted storage.

## Examples

**Host-key recipient + explicit decrypt path (sops-nix)** — illustrative only:

```nix
{ config, ... }:
{
  imports = [ inputs.sops-nix.nixosModules.sops ];

  services.openssh.enable = true; # host keys under /etc/ssh/

  sops.defaultSopsFile = ./secrets/host.yaml;
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];

  sops.secrets.myapp-token = { };
}
```

**Plugin on PATH for activation (sops-nix)** — verify `sops.age.plugins` in the README for your sops-nix revision; package names vary by channel:

```nix
{ pkgs, ... }:
{
  sops.age.plugins = [
    pkgs.age-plugin-yubikey
  ];
  services.pcscd.enable = true; # if the plugin needs smartcard access
}
```

Do not commit real keys, PINs, or plugin identity strings.

## References

- [Mic92/sops-nix](https://github.com/Mic92/sops-nix) — NixOS module; `sops.age.sshKeyPaths`, `sops.age.keyFile`, `sops.age.plugins` (confirm in README / module for your revision)
- [str4d/age-plugin-yubikey](https://github.com/str4d/age-plugin-yubikey) — YubiKey PIV plugin for age
- [FiloSottile/age — plugin package](https://github.com/FiloSottile/age/tree/main/plugin) — plugin protocol and Go framework
- [FiloSottile/age — age.1 Plugins](https://github.com/FiloSottile/age/blob/main/doc/age.1.ronn) — CLI behavior and `age-plugin-*` discovery on PATH
- [Mic92/ssh-to-age](https://github.com/Mic92/ssh-to-age) — convert SSH public keys to age recipients

## See also

- [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md)
- [Secrets management](secrets-management.md)
- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md)
- [Inter-machine trust](inter-machine-trust.md) — recipients as a trust ACL across hosts
