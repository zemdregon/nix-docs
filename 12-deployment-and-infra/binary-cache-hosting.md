---
status: complete
last-checked: 2026-08
---

# Binary Cache Hosting

## Overview

**Hosting a binary cache** means publishing signed store paths so other machines can [substitute](../04-store-and-build/binary-caches.md) them instead of building. The wire format is the same HTTP (or S3) layout that [cache.nixos.org](https://cache.nixos.org) uses: `.narinfo` metadata plus NAR payloads. This page covers **running or using** a cache—local daemons, self-hosted servers, SaaS, and object storage—not the substitution protocol itself (see [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md)).

Typical flow: generate a signing key, serve or upload signed paths, then tell clients the cache URL and corresponding `trusted-public-keys`. [CI with Nix](../11-development/ci-with-nix.md) and [Hydra](hydra.md) often push build products into a private cache so laptops and deploy hosts share the same prebuilts.

## Details

### When to use what

| Option | What it does | Prefer when… | Avoid / note when… |
|--------|--------------|--------------|--------------------|
| **nix-serve** | Serves the host’s `/nix/store` over HTTP (from Nixpkgs; not shipped with Nix) | Small LAN / builder sharing; NixOS module + nginx tutorial path on [nix.dev](https://nix.dev/tutorials/nixos/binary-cache-setup) | No IPv6 or TLS in the daemon itself—put nginx (or similar) in front for public HTTPS; only paths already on that machine are available |
| **Harmonia** | Rust server for `/nix/store` (HTTP ranges, transparent zstd option, optional builtin TLS; nixpkgs module) | Same “share this store” model as nix-serve, with more HTTP features / performance | Still not a durable remote store—GC on the host removes substitutable paths; configure `sign_key_paths` / `services.harmonia.signKeyPaths` for signed `.narinfo` |
| **Attic** | Self-hosted multi-tenant cache on S3-compatible (or local) storage; server-side signing on fetch; GC / dedup | Org cache with push tokens, durable object storage, pushers must not hold the signing key | Upstream still calls it an **early prototype**—expect breaking changes; ops burden of running the server |
| **Cachix** | Hosted binary-cache SaaS (`cachix push` / `cachix use`) | Managed HTTPS + signing; CI push without running a cache host | Third-party dependency and pricing; private caches need auth (`netrc` / token)—see [docs.cachix.org](https://docs.cachix.org/) |
| **`nix copy` → `file://` / `s3://`** | Writes a binary-cache tree (`.narinfo` + NAR) to a directory or S3-compatible bucket | Airgap media, DIY S3/CDN, or any writable store URL without a dedicated cache daemon | You own upload, TLS fronting, and signing (`secret-key` on the destination URL or sign beforehand); clients usually substitute via HTTPS over the same tree |

Live-store servers (nix-serve / Harmonia) and upload targets (Attic / Cachix / `nix copy`) solve different problems: the former expose whatever is already local; the latter persist closures independent of a single builder’s GC.

### Serving a live store

The classic tool is [`nix-serve`](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html): install from Nixpkgs, run it on a port, and point clients at `http://host:port/`. [Harmonia](https://github.com/nix-community/harmonia) is a Rust replacement that also serves `/nix/store` over HTTP. Both advertise `/nix-cache-info` and answer `.narinfo` / NAR requests for paths already on that machine. They do not upload to remote storage; builders must have built (or copied) the paths locally first. For signed `.narinfo` responses, configure a secret key (`NIX_SECRET_KEY_FILE` for nix-serve; Harmonia `sign_key_paths` / NixOS `services.harmonia.signKeyPaths`). Per nix.dev, `nix-serve` itself does not do SSL—use a reverse proxy for public HTTPS.

### Dedicated cache servers and SaaS

[Attic](https://github.com/zhaofengli/attic) is a self-hostable, multi-tenant cache with an S3-compatible (or local) backend, global deduplication, garbage collection, and **server-side signing** on fetch—pushers never hold the signing key ([docs](https://docs.attic.rs/); still described upstream as an early prototype). [Cachix](https://docs.cachix.org/) is a hosted binary-cache service: create a cache, push with the `cachix` CLI, and use `cachix use` (or manual `nix.conf`) on clients.

### Object storage and plain HTTP

Nix store backends include an [HTTP binary cache](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) and an [S3 binary cache](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) (`s3://bucket`). Populate writable caches with `nix copy --to` (for example `file:///path/to/cache` or `s3://bucket?region=…`); Nix creates `nix-cache-info` when writing if missing. Clients often substitute via HTTPS over the same tree. Pass `secret-key` / `secret-keys` on the destination store URL (or sign beforehand) so uploaded `.narinfo` files carry signatures. Prefer real signatures in production over `require-sigs = false` or `trusted=true`—see [Signing and caches](../14-security-and-trust/signing-and-caches.md).

### Signing and client trust

Generate an Ed25519 key pair with `nix-store --generate-binary-cache-key` (stable) or the experimental CLI (`nix key generate-secret --key-name …`, then `nix key convert-secret-to-public`). Keep the secret on the server or push path; distribute the public key. Clients must list the cache under `substituters` (and often `trusted-substituters` on multi-user systems) and add the public key to `trusted-public-keys`. Details for daemon trust boundaries: [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md).

### Pushing paths

| Tool | Role |
|------|------|
| `nix copy --to <store-url>` | Copy closures into any writable store (`file://`, `s3://`, SSH, etc.). |
| `cachix push <cache>` | Upload to a Cachix cache (often pipe `nix-build` / `nix build` output). |
| `attic push <cache> <paths>` | Upload closures to an Attic cache after `attic login` (optional `attic use` configures the client). |

CI usually builds, then pushes; clients only need substituter config. Hydra can be wired to upload to a cache so evaluation products are available cluster-wide.

### Failure modes

| Symptom / mistake | Likely cause | What to check |
|-------------------|--------------|---------------|
| Substitutes rejected / ignored with default trust | Unsigned `.narinfo` while `require-sigs` is `true` (default) | Serve or upload with a signing secret configured; confirm `Sig:` on a sample `.narinfo` (`curl …/hash.narinfo`). Prefer signing over `require-sigs = false` or `trusted=true` on the store URL |
| Paths exist on the cache but clients refuse them | Wrong or missing public key (name mismatch, typo, or `trusted-public-keys` replaced without keeping `cache.nixos.org-1`) | Client key line must match the key *name* and base64 from the signer’s `.pub`; keep the official cache key if you still use cache.nixos.org |
| Signing key leaked / clients can forge signatures | Secret key copied to client machines | Secret stays on the signer (nix-serve/Harmonia host, `nix copy` push host, or Attic server). Clients get **only** the public key in `trusted-public-keys` |
| Cache URL works (`nix-cache-info`) but needed paths 404 | Push never ran, incomplete push, or path never present on a live-store host | Confirm `.narinfo` for the exact store hash; re-run `cachix push` / `attic push` / `nix copy --to`; for nix-serve/Harmonia, build or copy onto that host first (GC can remove paths) |
| Works on LAN HTTP, fails or unsafe on the public internet | Plain HTTP to a public cache, or TLS misconfigured | nix-serve needs a TLS-terminating proxy for public use; Harmonia can use builtin TLS or nginx. Prefer HTTPS for anything beyond a trusted network; fix CA / `netrc` for private Cachix |
| Attic upgrades or ops surprises | Running a prototype as production without pinning / ops plan | [docs.attic.rs](https://docs.attic.rs/) still labels Attic an early prototype—pin versions, expect API/ops churn, or choose Cachix / `nix copy`+S3 / Harmonia until you accept that risk |

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
- [nix.dev — Setting up an HTTP binary cache](https://nix.dev/tutorials/nixos/binary-cache-setup) — NixOS `nix-serve`, signing, client trust, HTTPS via nginx
- [Nix reference manual — Store types](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) — HTTP / S3 / `file://` binary caches, `secret-key`
- [Nix reference manual — `nix-store --generate-binary-cache-key`](https://nix.dev/manual/nix/stable/command-ref/nix-store/generate-binary-cache-key.html) — Ed25519 key pair (stable)
- [Nix reference manual — `nix key generate-secret`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-key-generate-secret.html) — Ed25519 keys (experimental CLI)
- [Cachix documentation](https://docs.cachix.org/) — hosted caches, `cachix push` / `cachix use`
- [Attic](https://github.com/zhaofengli/attic) — self-hosted multi-tenant cache ([docs](https://docs.attic.rs/); early prototype)
- [Harmonia](https://github.com/nix-community/harmonia) — Rust binary cache serving `/nix/store`

## See also

- [Binary caches (cheatsheet)](../cheatsheets/binary-caches.md) — consume / host / sign chooser
- [Binary caches](../04-store-and-build/binary-caches.md) — substitution model and `nix.conf` settings
- [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md) — `.narinfo` / NAR layout
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — signatures, `require-sigs`, trust
- [CI with Nix](../11-development/ci-with-nix.md) — forge CI that often pushes to a project cache
- [Hydra](hydra.md) — CI that often feeds a private cache
- [Private cache mesh](private-cache-mesh.md) — multi-host substituter topology (hub + edge + builders)
- [Machine mesh](../02-concepts/machine-mesh.md) — private caches as mesh binary sharing
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — binary authenticity axis
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — who may add caches
- [nix copy and bundles](nix-copy-and-bundles.md) — `nix copy` into `file://` / remote stores
