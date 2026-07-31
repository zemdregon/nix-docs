---
status: complete
---

# Secrets Management

## Overview

The Nix [store](../02-concepts/store-path.md) is readable to all local users. Anything evaluation or a build copies into `/nix/store`—plaintext strings, `builtins.readFile` of a credential file, or a derivation that embeds secrets—is effectively public on that machine, and may also land on [binary caches](signing-and-caches.md) or remote builders. Prefer keeping ciphertext or path references in the repo and decrypting or injecting secrets at **deployment / activation / runtime**, not at evaluation time.

This page is the trust-model overview. Concrete NixOS option patterns live in [secrets strategies](../09-nixos/configuration/secrets-strategies.md); tool wiring for [agenix](https://github.com/ryantm/agenix) and [sops-nix](https://github.com/Mic92/sops-nix) lives in [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md).

## Details

### Why the store leaks secrets

The Nix reference manual states the store is readable to all users and discourages letting secrets into it. Store paths are shared across users; permissions on `/nix/store` are not a vault. On multi-user systems every local account can read them; on single-user hosts, service isolation still weakens if every unit can read every secret. Substituters and remote builds can copy the same paths elsewhere.

Treat every evaluated string and every file pulled into a derivation as public. Hashed passwords in config are a narrow exception (hash ≠ plaintext); see [secrets strategies](../09-nixos/configuration/secrets-strategies.md).

### Preferred delivery patterns

| Pattern | When | Where secret material appears |
|---------|------|-------------------------------|
| Deployment-time decrypt ([agenix](https://github.com/ryantm/agenix), [sops-nix](https://github.com/Mic92/sops-nix)) | Secrets in Git as ciphertext; host keys decrypt on the target | Encrypted blob in repo (and optionally ciphertext in the store); plaintext only after activation (typically `/run/agenix/…` or `/run/secrets/…`) |
| systemd credentials (`LoadCredential=` / related) | Unit needs a secret at start | Runtime dir via `$CREDENTIALS_DIRECTORY` (often `/run/credentials/<unit>/…`), not the store |
| Runtime / deploy-time files | Option accepts `*File` / path outside evaluation | Absolute path populated on the host; never `readFile`’d into Nix |
| Hashed account passwords | Local login only | Hash in config; plaintext never evaluated |

Shared rule from the Nix manual: **organize so secrets are read from the filesystem (with access control) at run time**, or keep them encrypted in the store and decrypt with access control on system activation.

### Evaluation purity vs impure secrets

[Flake evaluation is pure by default](../07-flakes/pure-eval-and-impure.md): no ambient `builtins.getEnv`, no reading arbitrary host paths, no undeclared network. That is good for reproducibility and bad for “sneak the secret in at eval time.”

- **Do not** rely on `--impure` plus `getEnv` or host files to inject secrets into a flake build. That fights purity, breaks CI hermeticity, and still risks landing material in the store.
- **Do** keep encrypted secrets (or non-secret hashes/paths) as declared inputs; decrypt with host-held keys during NixOS/Home Manager activation, or pass credentials via systemd / runtime files after the store closure is built.
- Pure eval and secret delivery are complementary: purity stops undeclared host state from shaping the build; deployment-time decrypt keeps plaintext out of that build.

### Trust boundaries

Secrets management intersects other trust controls: who may ask the daemon to build ([trusted users](trusted-users.md)), and whether dependencies themselves are trustworthy ([supply chain](supply-chain.md)). A correct decrypt-at-activation setup still fails if an untrusted input can rewrite units or steal the age/SOPS identity on the host.

### Home Manager and user config

Home Manager often symlinks config into the store. Do not put API tokens or private keys in `home.file` / `xdg.configFile` sources that evaluate into store paths. Use the same out-of-store or decrypt-at-activation patterns; see [dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md).

## Examples

**Avoid — plaintext (or `readFile` of plaintext) in evaluated config:**

```nix
# Do not do this — string lands in the world-readable store
services.myapp.apiToken = "sk-live-…";

# Also do not — copies file bytes into the store at eval time
services.myapp.apiToken = builtins.readFile ./secret-token.txt;
```

**Prefer — encrypted repo secret, path after activation** (conceptual; real options from agenix/sops-nix):

```nix
# Ciphertext in Git; decrypt during activation; service reads the resulting path
# agenix: config.age.secrets.<name>.path  → typically /run/agenix/<name>
# sops-nix: config.sops.secrets.<name>.path → typically /run/secrets/<name>
services.myapp = {
  enable = true;
  credentialsFile = config.sops.secrets.myapp-token.path; # illustrative option name
};
```

Never `builtins.readFile` a decrypted activation path back into an evaluated string—that reintroduces plaintext into the store.

**Prefer — systemd credential injection** (unit-level; secret file provided on the host or by a decrypt step):

```nix
systemd.services.myapp.serviceConfig = {
  LoadCredential = "token:/run/agenix/myapp-token"; # path after decrypt
  # Unit reads $CREDENTIALS_DIRECTORY/token (or %d/token), not a store path
};
```

Exact `LoadCredential=` / agenix / sops-nix option names come from upstream docs and the NixOS module system—do not invent APIs. For NixOS account and `*File` patterns, see [secrets strategies](../09-nixos/configuration/secrets-strategies.md).

## References

- [Secrets (Nix reference manual)](https://nix.dev/manual/nix/stable/store/secrets) — store is world-readable; read secrets at runtime or decrypt on activation
- [agenix](https://github.com/ryantm/agenix) — age-encrypted secrets for NixOS and Home Manager (`/run/agenix/…`)
- [sops-nix](https://github.com/Mic92/sops-nix) — SOPS-based secret provisioning for NixOS (`/run/secrets/…`)
- [systemd.exec(5) — Credentials](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Credentials) — `LoadCredential=` and `$CREDENTIALS_DIRECTORY`
- [Comparison of secret managing schemes (NixOS Wiki)](https://wiki.nixos.org/wiki/Comparison_of_secret_managing_schemes) — scheme survey linked from the Nix manual

## See also

- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md) — NixOS option-level patterns (hashes, `*File`, encrypted Git)
- [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md) — tool comparison and module usage
- [SSH and age plugins](ssh-and-age-plugins.md) — host keys, age plugins, YubiKey / FIDO patterns
- [Machine mesh](../02-concepts/machine-mesh.md) — secret recipients as mesh concern
- [Inter-machine trust](inter-machine-trust.md) — secret-trust axis
- [Dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md) — HM store symlinks vs secrets
- [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) — why flake eval rejects ambient secret injection
- [Signing and caches](signing-and-caches.md) — why store paths may leave the machine
