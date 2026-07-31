---
status: complete
---

# Binary Caches

## Overview

A **binary cache** is a Nix store exposed so other machines can **substitute**—download a pre-built [store path](../02-concepts/store-path.md) instead of running the builder locally. Configured substitute sources are called **substituters**. The usual payload is a compressed **NAR** (Nix Archive) plus a `.narinfo` metadata file; wire format details live in [Substitutes and NAR info](substitutes-and-narinfo.md).

The public cache for Nixpkgs is [https://cache.nixos.org](https://cache.nixos.org/). It is the default substituter on most installs. Substitution speeds up installs and upgrades when someone else has already built the same path. A **cache miss** (no substitute found) leads to a local build. A **failed download** of a known substitute only falls back to building if `fallback` is enabled (default `false`).

This page is operator-level: how to configure and use caches. Protocol and `.narinfo` depth stay on the linked page.

## Details

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

**Local lookup cache.** Nix caches substituter query results on disk (`narinfo-cache-positive-ttl`, `narinfo-cache-negative-ttl`). That is separate from `/nix/store`; [garbage collection](garbage-collection.md) only reclaims local store objects.

**Protocols.** HTTP/S3 caches speak the binary-cache protocol under [Store protocols](store-protocols.md). Serving your own cache (for example with `nix-serve`) publishes signed `.narinfo` files and NARs—see the substitutes deep dive and the [serving guide](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html).

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
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `substituters`, `trusted-public-keys`, `trusted-substituters`, and related options
- [Nix reference manual — store](https://nix.dev/manual/nix/stable/store/) — store model and substitution overview
- [Nix reference manual — store types](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) — HTTP, S3, SSH, and other substituter URL formats

## See also

- [Substitutes and NAR info](substitutes-and-narinfo.md) — `.narinfo` files, NAR payloads, and the substitution protocol
- [Store protocols](store-protocols.md) — binary cache and other store access protocols
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — trust, signatures, and operating private caches
- [Store path](../02-concepts/store-path.md) — what gets substituted into the local store
- [Machine mesh](../02-concepts/machine-mesh.md)
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — binary-trust axis (signatures/keys ≠ VPN peers)
