---
status: complete
last-checked: 2026-08
---

# Signing and Caches

## Overview

Binary caches publish store paths as NAR payloads plus `.narinfo` metadata. For ordinary (input-addressed) paths, clients treat those payloads as trustworthy only when the metadata is **signed** with a key the client already trusts. Nix uses **Ed25519** key pairs for this: the secret key (`secret-key-files` on the signer) signs on builders or cache hosts; clients verify the `.narinfo` **`Sig:`** field against matching entries in `trusted-public-keys`, under `require-sigs` (default `true`).

This is **not** the same as daemon [trusted users](trusted-users.md). `trusted-users` controls who may *configure* substituters, import unsigned paths, or change trust settings; `trusted-public-keys` controls which signatures make a substituted input-addressed path acceptable. Being a trusted user does not by itself make unsigned cache payloads safe.

Wrong trust configuration is a real risk. Adding an attacker’s public key, disabling signature checks, or marking a malicious store `trusted=true` lets a substituter inject binaries into `/nix/store`. Signing is the main defence against a compromised or untrusted cache URL—not HTTPS alone.

## Details

**Key pair.** Generate with `nix-store --generate-binary-cache-key` (Ed25519). It takes a key *name* (for example `cache.example.org-1`), a secret-key file path, and a public-key file path. The name identifies the key in signatures; clients look it up against `trusted-public-keys`. Public key lines look like `name:BASE64=`. Keep the secret key only on machines that **sign** (builders that write to the cache, or the cache host). Distribute only the public key to consumers.

**Client verification.** With `require-sigs = true` (default), a non-content-addressed path copied from a substituter must carry a signature from a key in `trusted-public-keys`, or from the public half of a key listed in local `secret-key-files`. Content-addressed paths are inherently trustworthy and are unaffected. Alternatives that skip ordinary key checks: `require-sigs = false`, or a store URL with `trusted=true`—both are security-sensitive.

**Official cache key.** The default `trusted-public-keys` value is:

```text
cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=
```

That is the Ed25519 public key for `https://cache.nixos.org/`. Setting `trusted-public-keys` in `nix.conf` **replaces** the default list, so keep this entry if you still want the official cache. Prefer `extra-trusted-public-keys` when you only need to append.

**Who may change trust (orthogonal axis).** On multi-user installs, only [trusted users](trusted-users.md) (and daemon config) can add substituters and keys or import unsigned paths. Unprivileged users are limited to URLs in `trusted-substituters`. That permission model does not replace signature verification: a trusted user who adds a cache without its public key (and with `require-sigs` on) still gets signature rejections; a trusted user who also disables checks or trusts the store wholesale has elevated the binary-authenticity risk. See [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md).

**Chooser: signing vs `trusted=true`.** Prefer signing whenever you control the publish path.

| Situation | Prefer |
|-----------|--------|
| You operate the cache (or build farm) and can run `secret-key-files` / sign before upload | Sign; put the public key on clients; leave `require-sigs = true` |
| Third-party or shared cache that already publishes signed `.narinfo` | Trust that operator’s public key only—do not mark the store `trusted=true` |
| Temporary lab / air-gapped store with no signer yet | `trusted=true` on that store URL (or briefly `require-sigs = false`) only until you can sign; treat as full trust of whoever can write the store |
| “I’m in `trusted-users`, so signatures don’t matter” | Wrong axis—still configure keys; see failure modes below |

Treating a substituter as fully trusted means you trust whoever can write that cache. Signing keeps authenticity tied to a key you control even if the HTTP endpoint is later compromised or mirrored.

**Operational split.** Signing keys belong on the write path (build farm, cache publisher). Clients need only public keys and substituter URLs. Hosting and publish workflows: [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md). Wire format (`.narinfo` `Sig:` fields): [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md).

### Failure modes

| Mistake | What happens | Fix |
|---------|--------------|-----|
| Set `trusted-public-keys = mycache-1:…` and omit `cache.nixos.org-1:…` | List **replaces** the default; official cache substitutes are ignored as unsigned | Keep `cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=` in the list, or append with `extra-trusted-public-keys` |
| Key **name** on the client does not match the name used when signing (e.g. pub line `cache.example.org-1:…` but signatures were made as `mycache-1`) | Substitutes rejected: not signed by any trusted key | Regenerate or republish with a consistent name; sync the exact `name:BASE64=` line to clients |
| Secret key file shipped to clients, CI images, or the public cache tree | Anyone with the secret can mint valid signatures for that key name | Restrict `secret-key-files` to signers only; rotate the key pair and update `trusted-public-keys` if exposure is possible |
| `require-sigs = false`, or substituter URL with `trusted=true` | Non-CA paths from that store (or globally) skip ordinary signature checks | Prefer signing + `require-sigs = true`; use these only for untrusted-lab exceptions you fully understand |
| Confusing `trusted-users` with signature trust | Operator can *enable* caches / import unsigned objects, but clients still need matching `trusted-public-keys` for normal signed substitution; conversely, being trusted does not make a random cache safe | Configure keys for authenticity; use `trusted-users` / `trusted-substituters` only for who may change policy—see [Trusted users](trusted-users.md) |

## Examples

**Generate a cache key pair:**

```bash
nix-store --generate-binary-cache-key \
  cache.example.org-1 \
  ./cache-priv-key.pem \
  ./cache-pub-key.pem
```

Keep `cache-priv-key.pem` on the signer only. The public file contains one line (`cache.example.org-1:…`); put that line on clients.

**Builder / cache host — sign locally built paths** (`nix.conf`):

```ini
secret-key-files = /var/keys/cache-priv-key.pem
```

**Client — trust that cache’s key and URL** (include the official key when still using `cache.nixos.org`):

```ini
substituters = https://cache.example.org/ https://cache.nixos.org/
trusted-public-keys = cache.example.org-1:BASE64PUBLICKEY= cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=
require-sigs = true
```

On multi-user systems, also list the custom URL in `trusted-substituters` if unprivileged users need it. To append a key without replacing the default list:

```ini
extra-trusted-public-keys = cache.example.org-1:BASE64PUBLICKEY=
```

**Avoid unless you understand the risk** — disables signature checking for non-content-addressed substitutes:

```ini
# require-sigs = false
```

## References

- [Nix reference manual — Serving a Nix store via HTTP](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) — binary cache / substituter setup
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `trusted-public-keys`, `require-sigs`, `secret-key-files`, `substituters`
- [Nix reference manual — `nix-store --generate-binary-cache-key`](https://nix.dev/manual/nix/stable/command-ref/nix-store/generate-binary-cache-key.html) — Ed25519 key pair generation
- [Nix reference manual — Using the post-build-hook](https://nix.dev/manual/nix/stable/advanced-topics/post-build-hook.html) — generate keys, sign, upload, and configure clients

## See also

- [Inter-machine trust](inter-machine-trust.md) — binary authenticity axis across machines
- [Machine mesh](../02-concepts/machine-mesh.md)
- [Trusted users](trusted-users.md) — who may alter substituters and import unsigned paths
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — daemon trust settings in `nix.conf`
- [Binary caches (cheatsheet)](../cheatsheets/binary-caches.md) — consume / host / sign chooser
- [Binary caches](../04-store-and-build/binary-caches.md) — substituters and operator configuration
- [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md) — `.narinfo` metadata and signatures on the wire
- [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) — running and publishing a cache
