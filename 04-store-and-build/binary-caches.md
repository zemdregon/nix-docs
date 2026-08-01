---
status: complete
last-checked: 2026-08
---

# Binary Caches

## Overview

A **binary cache** is a Nix store exposed so other machines can **substitute**—download a pre-built [store path](../02-concepts/store-path.md) instead of running the builder locally. Configured substitute sources are called **substituters**. The usual payload is a compressed **NAR** (Nix Archive) plus a `.narinfo` metadata file; wire format details live in [Substitutes and NAR info](substitutes-and-narinfo.md).

The public cache for Nixpkgs is [https://cache.nixos.org](https://cache.nixos.org/). It is the default substituter on most installs. Substitution speeds up installs and upgrades when someone else has already built the same path. A **cache miss** (no substitute found) leads to a local build. A **failed download** of a known substitute only falls back to building if `fallback` is enabled (default `false`).

This page is **client/operator** configuration: which substituters to query, trust boundaries, and common failure modes. It is not how to run a cache server—that is [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md)—and not the Ed25519 signing model—that is [Signing and caches](../14-security-and-trust/signing-and-caches.md). Protocol and `.narinfo` depth stay on the linked page.

## Details

**When to use this page vs related topics.**

| Goal | Page |
|------|------|
| Configure clients to *consume* caches (`substituters`, keys, trust, failures) | This page |
| Who may add substituters on a multi-user daemon | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| Generate keys, verify `Sig:`, keep the official key | [Signing and caches](../14-security-and-trust/signing-and-caches.md) |
| Serve, push, or host a cache (`nix-serve`, Harmonia, Attic, Cachix, S3) | [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) |

**Substituters are stores.** Each URL names a store implementation—commonly an HTTP binary cache (`https://…`), also S3 (`s3://…`), SSH, or a local path. See [store types](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) for schemes and per-store settings.

**When substitution runs.** With `substitute` enabled (default), Nix queries configured substituters for each missing path in the needed [closure](../02-concepts/closure.md). Substituters are tried by **priority** (lower number first). The default `https://cache.nixos.org/` has priority 40; override with `?priority=N` on a URL. Nix fetches NAR payloads and metadata, verifies hashes (and signatures when required), and registers the path locally—same end state as a local build, without running the builder.

**Configuration (`nix.conf`).** Key settings ([full reference](https://nix.dev/manual/nix/stable/command-ref/conf-file.html)):

| Setting | Role |
|---------|------|
| `substituters` | Whitespace-separated store URLs to query. Default: `https://cache.nixos.org/`. |
| `substitute` | Master switch; `false` forces building from source. Default: `true`. |
| `trusted-public-keys` | Public keys whose signatures Nix accepts when copying paths. Default includes `cache.nixos.org-1:…`. |
| `trusted-substituters` | URLs unprivileged users may enable via `substituters` / `--substituters`. Default: empty. |
| `trusted-users` | Users who may specify additional substituters or import unsigned paths via the daemon. Default: `root`. |
| `require-sigs` | When `true` (default), non-content-addressed paths from substituters need a trusted signature (unless the store URL sets `trusted=true`). |
| `fallback` | When `true`, build from source if a substitute download fails. Default: `false`. |
| `builders-use-substitutes` | When `true`, remote builders use their own substituters instead of waiting for uploads from the local machine. Default: `false`. |

Daemon setups often split trust: system `nix.conf` lists `trusted-substituters` and `trusted-public-keys`; users or CI add URLs to `substituters` (or pass `--substituters`). For Nix to use a substituter, the caller must be in `trusted-users` **or** the URL must be in `trusted-substituters`. Unprivileged users may only pass substituter URLs listed in `trusted-substituters`.

**Security.** Substituted paths must match expected store hashes; signatures bind metadata to keys in `trusted-public-keys`. Wrong keys or `require-sigs = false` can let a cache serve tampered binaries. See [Signing and caches](../14-security-and-trust/signing-and-caches.md).

**Local lookup cache.** Nix caches substituter query results on disk (`narinfo-cache-positive-ttl`, `narinfo-cache-negative-ttl`, and `/nix-cache-info` via `narinfo-cache-meta-ttl`). That is separate from `/nix/store`; [garbage collection](garbage-collection.md) only reclaims local store objects. Defaults (seconds): positive `2592000` (≈30 days), negative `3600`, meta `604800` (7 days). Negative TTL `0` forces refresh of negative lookups; wiping `$HOME/.cache/nix/binary-cache-v*.sqlite*` clears the lookup DB (see conf-file).

**Protocols.** HTTP/S3 caches speak the binary-cache protocol under [Store protocols](store-protocols.md). Serving your own cache (for example with `nix-serve`) publishes signed `.narinfo` files and NARs—see the substitutes deep dive and the [serving guide](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html).

### Common failure modes

| Symptom / misconfig | Cause | Fix |
|---------------------|--------|-----|
| Unprivileged user: substituter ignored / “untrusted substituter” | URL in user `substituters` or `--substituters` but not in daemon `trusted-substituters`, and caller not in `trusted-users` | Add the URL to system `trusted-substituters` (preferred) or run as a trusted user; see [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| Official cache paths rejected after adding a private key | Setting `trusted-public-keys = …` **replaces** the default list, dropping `cache.nixos.org-1:…` | Keep the official key in the list (or use `extra-trusted-public-keys`); see [Signing and caches](../14-security-and-trust/signing-and-caches.md) |
| Private cache rarely used; public cache tried first / slow path | Wrong **priority** (lower number wins; `cache.nixos.org` defaults to 40) | Set `?priority=N` on the preferred substituter URL (e.g. below 40), or rely on the cache’s advertised Priority in `nix-cache-info` |
| Known substitute fails to download; build does not start | `fallback` defaults to `false`—a failed substitute download is an error, not an automatic local build | Set `fallback = true` (or `--fallback`) if you want build-on-download-failure; fix network/cache otherwise |
| No substitution at all; everything builds from source | `substitute = false` (master switch) | Set `substitute = true` (default) unless you intentionally force source builds |
| Stale “not on cache” / “still on cache” after the remote changed | Local **narinfo** disk cache: negative TTL (default 3600s) or positive TTL (default ≈30 days); meta TTL for `/nix-cache-info` | Wait for TTL, set `narinfo-cache-negative-ttl = 0` to refresh misses, shorten positive TTL for GC-heavy caches, or remove `binary-cache-v*.sqlite*` under the Nix cache dir |

## Examples

**Minimal `nix.conf` for the public cache** (matches upstream defaults):

```ini
substituters = https://cache.nixos.org/
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=
```

**Add a second cache** (also trust its signing key; on multi-user systems, list the URL in `trusted-substituters` if unprivileged users need it):

```ini
substituters = https://cache.nixos.org/ https://my-org.example/cache
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= my-org.example-1:BASE64KEY==
```

**One-shot CLI** (in addition to defaults), as in the serving guide:

```bash
nix build nixpkgs#hello \
  --substituters http://avalon:8080/ \
  --extra-experimental-features 'nix-command flakes'
# Classic one-shot: nix-env -iA nixpkgs.hello --substituters http://avalon:8080/
```

**Query whether a path exists on a cache** (replace with a real store path):

```bash
nix path-info --store https://cache.nixos.org/ \
  /nix/store/…-hello-2.12
```

Success means the cache advertises that path. Failure means Nix will build locally (or try another substituter).

**Dry-run: substitute vs build:**

```bash
nix build --dry-run nixpkgs#hello
```

Output lists paths copied from substituters versus built locally.

## References

- [Nix reference manual — Serving a Nix store via HTTP](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) — binary caches, `nix-cache-info`, client `--substituters` / `substituters`
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `substituters`, `trusted-public-keys`, `trusted-substituters`, `fallback`, `substitute`, narinfo TTL options
- [Nix reference manual — store](https://nix.dev/manual/nix/stable/store/) — store model and substitution overview
- [Nix reference manual — store types](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) — HTTP, S3, SSH, and other substituter URL formats

## See also

- [Binary caches (cheatsheet)](../cheatsheets/binary-caches.md) — consume / host / sign chooser
- [Substitutes and NAR info](substitutes-and-narinfo.md) — `.narinfo` files, NAR payloads, and the substitution protocol
- [Store protocols](store-protocols.md) — binary cache and other store access protocols
- [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) — serving and pushing caches
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — trust, signatures, and operating private caches
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — daemon trust for enabling substituters
- [Store path](../02-concepts/store-path.md) — what gets substituted into the local store
- [Machine mesh](../02-concepts/machine-mesh.md)
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — binary-trust axis (signatures/keys ≠ VPN peers)
