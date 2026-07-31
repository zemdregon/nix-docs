---
status: complete
---

# Secrets Strategies

## Overview

Nix evaluation produces immutable [store paths](../../02-concepts/store-path.md) that are typically world-readable under `/nix/store`. Anything that ends up in the store—including strings baked into `configuration.nix` or files copied in via `source` / `builtins.readFile`—is a poor place for secrets. NixOS configuration should reference secret *material* indirectly: hashes, paths outside the store, or ciphertext decrypted only on the target during activation.

Threat-model framing: [Secrets management](../../14-security-and-trust/secrets-management.md). Tool wiring for encrypted Git secrets: [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md).

## Details

**Why the store is the wrong vault.** During evaluation, Nix copies inputs into the store and builds a closure rooted at the system [generation](../../02-concepts/generation.md). Store paths are not access-controlled per user or service. Treat every evaluated string and every file pulled into a derivation as public.

### Pattern matrix — which strategy?

Use this table to pick an approach before wiring modules. “What lands in eval + store” is what any local user (or a cache/substituter) can read from `/nix/store`.

| Need | What lands in eval + store | When to use | Go-to tools / options |
|------|----------------------------|-------------|------------------------|
| Local account login | **Inline hash:** the `mkpasswd` hash string | Hash publication is acceptable; small fleets, low sensitivity | `hashedPassword` / `initialHashedPassword` |
| Local account login | **Path only:** string like `/var/lib/secrets/alice.hashedPassword` | Do not want the hash world-readable in the store | `hashedPasswordFile` (`passwordFile` is a deprecated alias—file must contain a **hash**, not plaintext) |
| Service API key, TLS key, DB password | **Path only:** absolute path to credential file | Module exposes `*File` / credential-path options; material lives outside eval | Populate `/run/…` or `/var/lib/…` at deploy/activation; wire `credentialsFile`, `passwordFile`, `privateKeyFile`, etc. |
| Secret tracked in Git (team, CI, many hosts) | **Ciphertext** in repo; path strings in config | Reproducible config with encrypted blobs; decrypt only on target | [sops-nix](https://github.com/Mic92/sops-nix) → `/run/secrets/…`; [agenix](https://github.com/ryantm/agenix) → `/run/agenix/…`; then point `*File` options at the activation path |
| Runtime unit credential (no store path) | **Path string** to source file on disk | Service reads via systemd credential dir at start, not from evaluated strings | `LoadCredential=` on the unit (see [Secrets management](../../14-security-and-trust/secrets-management.md)); source often an agenix/sops path |
| Ephemeral root / impermanence | **Key paths + ciphertext** on persisted volume; decrypted material still under `/run/…` | Root is tmpfs or wiped each boot; identities must survive reboot | Persist `sops.age.keyFile`, host SSH keys, `age.identityPaths`; details in upstream impermanence notes—exact module options out of scope here |
| Full-disk / initrd unlock | **Not** app secrets—unlock material for LUKS/TPM/FIDO | Boot-time disk access only; orthogonal to service credentials | Bootloader/initrd options; not a substitute for sops-nix/agenix |

**Never use** `users.users.<name>.password` with a real password—the value is world-readable in the store. See [Users and groups](users-and-groups.md) and the NixOS manual User Management chapter.

### Recipes (by pattern)

**Account passwords.** Generate a hash offline (`mkpasswd`), never evaluate plaintext. Inline hash is the narrow exception where publishing the hash is acceptable. `hashedPasswordFile` reads the hash file on each activation, so only the path string enters the store.

**Service `*File` options.** Many modules accept a path to credential material on disk. Populate that path at deploy or activation under a root-owned location (`/run/…`, `/var/lib/…`). Never `builtins.readFile` those files into evaluated Nix—that copies bytes into the store.

**Encrypted secrets in Git (sops-nix, agenix).** Shared flow: **encrypted blob in repo → decrypt on target during activation → inject resulting path into `*File` options**. sops-nix uses [SOPS](https://github.com/getsops/sops) (age, PGP, …); agenix uses [age](https://github.com/FiloSottile/age). Comparison and module usage: [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md)—do not duplicate full tooling here.

**Impermanence.** On hosts with an ephemeral root, keep *decrypt identities* and any out-of-store secret files on the persisted volume—not only ciphertext in Git. sops-nix documents that `sops.age.keyFile` or host SSH keys used for decrypt must live on durable storage; agenix needs `age.identityPaths` pointing at keys that survive reboot. Persisted mounts hold keys and state; decrypted material still belongs under `/run/…` after activation.

**Hardware-backed disk unlock.** LUKS/TPM/FIDO initrd unlock is boot-time secret delivery, not application secret management. Unlock material must not be duplicated as evaluated Nix strings. Use sops-nix/agenix (or deploy-time files) for service credentials.

**Operational rules.** Never commit raw secrets. Prefer narrow permissions and root-only paths for decrypted material. Rotate by updating ciphertext or deploy-time files, then rebuilding—do not edit secrets in place inside the store.

## Examples

**Avoid — plaintext in evaluated config.** The string is copied into the store and readable to any local user:

```nix
# Do not do this
users.users.alice = {
  isNormalUser = true;
  password = "do-not-put-secrets-here";
};
```

**Prefer — hash offline; keep hash out of the store via file** (file created on the host or via decrypt tooling; contents = one `mkpasswd` line):

```nix
users.users.alice = {
  isNormalUser = true;
  hashedPasswordFile = "/var/lib/secrets/alice.hashedPassword";
};
```

**Acceptable — hash inline** when publishing the hash is acceptable:

```nix
users.users.alice = {
  isNormalUser = true;
  hashedPassword = "$6$rounds=…$…"; # from: mkpasswd
};
```

**Prefer — encrypted repo secret → activation path** (conceptual; exact module options differ by tool):

```nix
# sops-nix or agenix decrypts at activation; services read the resulting path
services.myapp = {
  enable = true;
  credentialsFile = config.sops.secrets.myapp-token.path; # illustrative
};
```

Use upstream module documentation for real option names; do not invent module APIs. See [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md) for concrete patterns.

## References

- [NixOS manual (stable) — User Management](https://nixos.org/manual/nixos/stable/#sec-user-management) — accounts, `hashedPassword`, `mkpasswd`
- [users.users.\<name\>.hashedPasswordFile](https://search.nixos.org/options?show=users.users.%3Cname%3E.hashedPasswordFile) — path to hash file, read on activation
- [sops-nix](https://github.com/Mic92/sops-nix) — SOPS decrypt at activation; impermanence note for key paths
- [agenix](https://github.com/ryantm/agenix) — age-encrypted secrets; `/run/agenix/…` after activation

## See also

- [Users and groups](users-and-groups.md)
- [Secrets management](../../14-security-and-trust/secrets-management.md)
- [Machine mesh](../../02-concepts/machine-mesh.md)
- [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md)
- [agenix / sops-nix](../../12-deployment-and-infra/agenix-sops-nix.md)
- [Configuration.nix](configuration-nix.md)
