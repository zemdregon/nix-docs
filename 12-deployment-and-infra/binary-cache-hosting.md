---
status: complete
---

# Binary Cache Hosting

## Overview

**Hosting a binary cache** means publishing signed store paths so other machines can [substitute](../04-store-and-build/binary-caches.md) them instead of building. The wire format is the same HTTP (or S3) layout that [cache.nixos.org](https://cache.nixos.org) uses: `.narinfo` metadata plus NAR payloads. This page covers **running or using** a cache—local daemons, self-hosted servers, SaaS, and object storage—not the substitution protocol itself (see [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md)).

Typical flow: generate a signing key, serve or upload signed paths, then tell clients the cache URL and corresponding `trusted-public-keys`. CI and [Hydra](hydra.md) often push build products into a private cache so laptops and deploy hosts share the same prebuilts.

## Details

**Serving a live store (read from `/nix/store`).** The classic tool is [`nix-serve`](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html): install from Nixpkgs (not shipped with Nix itself), run it on a port, and point clients at `http://host:port/`. [Harmonia](https://github.com/nix-community/harmonia) is a Rust replacement that also serves `/nix/store` over HTTP (HTTP ranges, optional builtin TLS, NixOS module in nixpkgs). Both advertise `/nix-cache-info` and answer `.narinfo` / NAR requests for paths already on that machine. They do not upload to remote storage; builders must have built (or copied) the paths locally first. For signed `.narinfo` responses, configure a secret key (`NIX_SECRET_KEY_FILE` for nix-serve; Harmonia `sign_key_paths` / NixOS `services.harmonia.signKeyPaths`).

**Dedicated cache servers and SaaS.** [Attic](https://github.com/zhaofengli/attic) is a self-hostable, multi-tenant cache with an S3-compatible (or local) backend, global deduplication, garbage collection, and **server-side signing** on fetch—pushers never hold the signing key ([docs](https://docs.attic.rs/); still described upstream as an early prototype). [Cachix](https://docs.cachix.org/) is a hosted binary-cache service: create a cache, push with the `cachix` CLI, and use `cachix use` (or manual `nix.conf`) on clients. Choose by ops budget: nix-serve/Harmonia for “share this builder’s store,” Attic/S3 for durable shared storage, Cachix when you want managed hosting.

**Object storage and plain HTTP.** Nix store backends include an [HTTP binary cache](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) and an [S3 binary cache](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) (`s3://bucket`). Populate writable caches with `nix copy --to` (for example `file:///path/to/cache` or `s3://bucket?region=…`); Nix creates `nix-cache-info` when writing if missing. Clients often substitute via HTTPS over the same tree. Pass `secret-key` / `secret-keys` on the destination store URL (or sign beforehand) so uploaded `.narinfo` files carry signatures. Prefer real signatures in production over `require-sigs = false` or `trusted=true`—see [Signing and caches](../14-security-and-trust/signing-and-caches.md).

**Signing and client trust.** Generate an Ed25519 key pair with `nix-store --generate-binary-cache-key` (stable) or the experimental CLI (`nix key generate-secret --key-name …`, then `nix key convert-secret-to-public`). Keep the secret on the server or push path; distribute the public key. Clients must list the cache under `substituters` (and often `trusted-substituters` on multi-user systems) and add the public key to `trusted-public-keys`. Details for daemon trust boundaries: [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md).

**Pushing paths.** Common upload paths:

| Tool | Role |
|------|------|
| `nix copy --to <store-url>` | Copy closures into any writable store (`file://`, `s3://`, SSH, etc.). |
| `cachix push <cache>` | Upload to a Cachix cache (often pipe `nix-build` / `nix build` output). |
| `attic push <cache> <paths>` | Upload closures to an Attic cache after `attic login` (optional `attic use` configures the client). |

CI usually builds, then pushes; clients only need substituter config. Hydra can be wired to upload to a cache so evaluation products are available cluster-wide.

## Examples

**Generate a signing key pair** (stable CLI; preferred for nix-serve / Harmonia):

```bash
nix-store --generate-binary-cache-key \
  cache.example.org-1 \
  ./cache.secret \
  ./cache.pub
```

Equivalent experimental commands (Nix 2.x; interface may change):

```bash
nix key generate-secret --key-name cache.example.org-1 > ./cache.secret
nix key convert-secret-to-public < ./cache.secret > ./cache.pub
```

**Serve the local store with nix-serve** (sign with the secret key), then sanity-check:

```bash
NIX_SECRET_KEY_FILE=./cache.secret nix-serve -p 8080
curl http://builder:8080/nix-cache-info
```

**Client `nix.conf` fragment** (replace the public key with the contents of `cache.pub`):

```ini
substituters = https://cache.nixos.org/ http://builder:8080/
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= cache.example.org-1:BASE64KEY==
```

**Push with `nix copy`**, Cachix, or Attic (illustrative):

```bash
# Local directory cache, then optionally sync/serve that tree over HTTPS
nix copy --to 'file:///var/cache/nix?secret-key=/path/to/cache.secret' ./result

# S3-compatible bucket (region/endpoint/credentials via query params or AWS env)
nix copy --to 's3://my-org-nix-cache?region=eu-west-1&secret-key=/path/to/cache.secret' ./result

nix-build | cachix push mycache

attic login local http://attic.example:8080 "$TOKEN"
attic push my-cache ./result
```

## References

- [Nix reference manual — Serving a Nix store via HTTP](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) — `nix-serve`, client `substituters`
- [nix.dev — Setting up an HTTP binary cache](https://nix.dev/tutorials/nixos/binary-cache-setup) — NixOS `nix-serve`, signing, client trust
- [Nix reference manual — Store types](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) — HTTP / S3 / `file://` binary caches, `secret-key`
- [Nix reference manual — `nix-store --generate-binary-cache-key`](https://nix.dev/manual/nix/stable/command-ref/nix-store/generate-binary-cache-key.html) — Ed25519 key pair (stable)
- [Nix reference manual — `nix key generate-secret`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-key-generate-secret.html) — Ed25519 keys (experimental CLI)
- [Cachix documentation](https://docs.cachix.org/) — hosted caches, `cachix push` / `cachix use`
- [Attic](https://github.com/zhaofengli/attic) — self-hosted multi-tenant cache ([docs](https://docs.attic.rs/))
- [Harmonia](https://github.com/nix-community/harmonia) — Rust binary cache serving `/nix/store`

## See also

- [Binary caches](../04-store-and-build/binary-caches.md) — substitution model and `nix.conf` settings
- [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md) — `.narinfo` / NAR layout
- [Machine mesh](../02-concepts/machine-mesh.md) — private caches as mesh binary sharing
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — signatures and trust
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — binary authenticity axis
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — who may add caches
- [Hydra](hydra.md) — CI that often feeds a private cache
