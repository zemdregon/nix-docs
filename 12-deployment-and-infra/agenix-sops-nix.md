---
status: complete
last-checked: 2026-08
---

# agenix / sops-nix

## Overview

[agenix](https://github.com/ryantm/agenix) and [sops-nix](https://github.com/Mic92/sops-nix) keep secrets in a NixOS (or Home Manager) repo as ciphertext. Recipients are typically host SSH keys (or age keys derived from them); private identities on the target decrypt during activation. Plaintext should not land in evaluation or the Nix store—only ciphertext is copied into the store; decrypted files appear under `/run/…` (or a user runtime dir) after activation.

| | agenix | sops-nix |
|---|--------|----------|
| Crypto | [age](https://filippo.io/age/) (often via SSH keys) | [SOPS](https://github.com/getsops/sops) with age and/or PGP |
| Repo shape | One encrypted `.age` file per secret | Encrypted YAML/JSON/dotenv/… (or binary) documents |
| Module surface | `age.secrets.*` → `/run/agenix/…` | `sops.secrets.*` → `/run/secrets/…` (+ templates) |
| CLI / map | `agenix` CLI + `secrets.nix` (CLI only, not NixOS import) | `sops` + `.sops.yaml` creation rules |
| HM | `agenix.homeManagerModules.default` (`age-home`) | home-manager / `sops-nix` HM module |

Shared rule: never `builtins.readFile` a decrypted path into an evaluated string—that reintroduces plaintext into the store. Prefer options that take a file path at runtime. Broader strategy: [Secrets strategies](../09-nixos/configuration/secrets-strategies.md); threat-model framing: [Secrets management](../14-security-and-trust/secrets-management.md).

## Details

### Chooser

| Criterion | Prefer |
|-----------|--------|
| Few file-shaped secrets; one `.age` blob per secret | **agenix** |
| Host SSH / age recipients only; no GPG workflow | **agenix** |
| Small audit surface / “just age + SSH” | **agenix** |
| Structured multi-secret YAML/JSON (or dotenv) in one file | **sops-nix** |
| Team edit with GPG (or mixed age + PGP) recipients | **sops-nix** |
| Readable encrypted diffs; SOPS-style creation rules | **sops-nix** |
| Inject secrets into a config file at activation (`sops.templates` + `sops.placeholder`) | **sops-nix** |
| Already standardized on SOPS elsewhere (CI, other repos) | **sops-nix** |

Either tool works with ordinary rebuilds and fleet tools such as [Colmena](colmena.md)—no out-of-band secret upload step. For SSH host-key ↔ age recipient/identity wiring and plugins, see [SSH and age plugins](../14-security-and-trust/ssh-and-age-plugins.md).

### agenix (ryantm/agenix)

Encrypt with the `agenix` CLI against public SSH (or age) keys listed in a secrets map (`secrets.nix`). That map drives the CLI only—it is **not** imported into the NixOS module. The NixOS module copies `.age` files into the store as ciphertext, then decrypts with host (or configured) private keys at activation and mounts under `/run/agenix/<name>` by default (`age.secretsDir`). Default identities are the host SSH keys from `services.openssh.hostKeys` (typically under `/etc/ssh/`); override with `age.identityPaths` (paths as strings—never Nix path literals that would copy private keys into the store). Home Manager uses the same `age.secrets` options via `age-home` / `homeManagerModules.default`, with `age.identityPaths` required and a per-user secrets dir (typically `$XDG_RUNTIME_DIR/agenix`). Rekey with `agenix --rekey` after changing recipients in `secrets.nix` (you must still be able to decrypt).

### sops-nix (Mic92/sops-nix)

Edit secrets with `sops` against a `.sops.yaml` creation-rules file (age recipients and/or PGP fingerprints—commonly SSH host keys converted with `ssh-to-age`). The module decrypts at activation using host SSH keys (`sops.age.sshKeyPaths`, often `/etc/ssh/ssh_host_ed25519_key`), a dedicated age key file (`sops.age.keyFile`, e.g. `/var/lib/sops-nix/key.txt`), and/or GPG. Each declared `sops.secrets.<name>` becomes a file (default `/run/secrets/…`); nested YAML/JSON keys map to individual secret files. Templates (`sops.templates` + `sops.placeholder`) inject values into config files only at activation, not during eval. After adding hosts to `.sops.yaml`, update ciphertext recipients (illustrative: `sops updatekeys …` on affected files).

### Failure modes / ops

- **Missing identity on the host** — activation fails to decrypt (no usable key at `age.identityPaths` / `sops.age.sshKeyPaths` / `sops.age.keyFile`). Common with impermanence if keys are not on a persisted volume.
- **Wrong recipients** — ciphertext was encrypted for keys the target does not hold; rebuild/activation cannot decrypt until you re-encrypt for the correct public keys.
- **Rekey when hosts change** — add/remove machines (or rotate host keys) → update recipient lists (`secrets.nix` or `.sops.yaml`) → rekey/updatekeys → rebuild. Old generations may still hold older ciphertext until GC.
- **Home Manager identity paths** — HM modules do not assume system host keys; set `age.identityPaths` (agenix) or the HM age/SSH key options (sops-nix) to keys the user can read at activation.
- **Activation vs eval** — decryption happens at activation. `builtins.readFile` of a decrypted path (or any plaintext evaluated into config) puts secrets in the store. Wire `*File` / path options to `config.age.secrets.*.path` or `config.sops.secrets.*.path` instead.
- **Password-protected SSH keys** — age does not use ssh-agent; passphrase-protected identities are painful for rekey and unsuitable for unattended activation (agenix README notice).

### Operational notes

Encrypted blobs in the repo are fine; plaintext in `configuration.nix` / flakes is not. Keep decrypt identities on the host outside evaluation. For Home Manager-only secrets patterns, see [Dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md).

## Examples

**agenix — declare and consume a path (illustrative):**

```nix
{ config, ... }:
{
  # imports = [ agenix.nixosModules.default ];  # from flake input

  age.secrets.db-password.file = ../secrets/db-password.age;

  # Service option that reads a file at runtime — not builtins.readFile
  services.myapp.passwordFile = config.age.secrets.db-password.path;
  # → /run/agenix/db-password after activation
}
```

**sops-nix — default file + one secret (illustrative):**

```nix
{ config, ... }:
{
  # imports = [ sops-nix.nixosModules.sops ];

  sops.defaultSopsFile = ./secrets/example.yaml;
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];

  sops.secrets."myservice/api_token" = { };

  services.myservice.tokenFile = config.sops.secrets."myservice/api_token".path;
  # → /run/secrets/myservice/api_token
}
```

Do not put real tokens, private keys, or passwords in examples or committed plaintext.

## References

- [ryantm/agenix](https://github.com/ryantm/agenix) — age-encrypted secrets for NixOS and Home Manager
- [Mic92/sops-nix](https://github.com/Mic92/sops-nix) — SOPS-based secret provisioning for NixOS / HM / darwin
- [getsops/sops](https://github.com/getsops/sops) — encryption tool used by sops-nix
- [FiloSottile/age](https://github.com/FiloSottile/age) — age format used by agenix (and often by sops)

## See also

- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md)
- [Secrets management](../14-security-and-trust/secrets-management.md)
- [SSH and age plugins](../14-security-and-trust/ssh-and-age-plugins.md) — host/user keys, `ssh-to-age`, plugin identities at activation
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — recipient lists = secret trust ACL
- [Machine mesh](../02-concepts/machine-mesh.md)
- [Clan and mesh](clan-and-mesh.md)
- [Dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md)
- [Colmena](colmena.md)
