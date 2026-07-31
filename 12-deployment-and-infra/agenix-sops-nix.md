---
status: complete
---

# agenix / sops-nix

## Overview

[agenix](https://github.com/ryantm/agenix) and [sops-nix](https://github.com/Mic92/sops-nix) keep secrets in a NixOS (or Home Manager) repo as ciphertext. Recipients are typically host SSH keys (or age keys derived from them); private identities on the target decrypt during activation. Plaintext should not land in evaluation or the Nix store—only ciphertext is copied into the store; decrypted files appear under `/run/…` (or a user runtime dir) after activation.

| | agenix | sops-nix |
|---|--------|----------|
| Crypto | [age](https://filippo.io/age/) (often via SSH keys) | [SOPS](https://github.com/getsops/sops) with age and/or PGP |
| Repo shape | One encrypted `.age` file per secret | Encrypted YAML/JSON/dotenv/… (or binary) documents |
| Module surface | `age.secrets.*` → `/run/agenix/…` | `sops.secrets.*` → `/run/secrets/…` (+ templates) |
| HM | `agenix.homeManagerModules.default` (`age-home`) | home-manager / `sops-nix` HM module |

Shared rule: never `builtins.readFile` a decrypted path into an evaluated string—that reintroduces plaintext into the store. Prefer options that take a file path at runtime. Broader strategy: [Secrets strategies](../09-nixos/configuration/secrets-strategies.md); threat-model framing: [Secrets management](../14-security-and-trust/secrets-management.md).

## Details

**agenix (ryantm/agenix).** Encrypt with the `agenix` CLI against public SSH (or age) keys listed in a secrets map (`secrets.nix`). That map drives the CLI only—it is **not** imported into the NixOS module. The NixOS module copies `.age` files into the store as ciphertext, then decrypts with host (or configured) private keys at activation and mounts under `/run/agenix/<name>` by default (`age.secretsDir`). Default identities are the host SSH keys under `/etc/ssh/`; override with `age.identityPaths`. Home Manager uses the same `age.secrets` options via `age-home` / `homeManagerModules.default`, with `age.identityPaths` required and a per-user secrets dir (typically `$XDG_RUNTIME_DIR/agenix`).

**sops-nix (Mic92/sops-nix).** Edit secrets with `sops` against a `.sops.yaml` creation-rules file (age recipients and/or PGP fingerprints—commonly SSH host keys converted with `ssh-to-age`). The module decrypts at activation using host SSH keys (`sops.age.sshKeyPaths`, often `/etc/ssh/ssh_host_ed25519_key`), a dedicated age key file (`sops.age.keyFile`, e.g. `/var/lib/sops-nix/key.txt`), and/or GPG. Each declared `sops.secrets.<name>` becomes a file (default `/run/secrets/…`); nested YAML/JSON keys map to individual secret files. Templates (`sops.templates` + `sops.placeholder`) inject values into config files only at activation, not during eval.

**Contrast.** agenix is smaller and file-per-secret; rekeying and multi-recipient workflows stay close to age/SSH. sops-nix fits structured multi-secret documents, readable encrypted diffs, team/GPG workflows, and template injection. Both work with ordinary rebuilds and fleet tools such as [Colmena](colmena.md)—no out-of-band secret upload step.

**Operational notes.** Encrypted blobs in the repo are fine; plaintext in `configuration.nix` / flakes is not. Keep decrypt identities on the host (SSH host key, age key file, etc.) outside evaluation. Rotate by editing ciphertext (rekey recipients when hosts change) and rebuilding. For Home Manager-only secrets patterns, see [Dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md).

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
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — recipient lists = secret trust ACL
- [Machine mesh](../02-concepts/machine-mesh.md)
- [Clan and mesh](clan-and-mesh.md)
- [Dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md)
- [Colmena](colmena.md)
