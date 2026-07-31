---
status: complete
---

# Substitutes and NAR info

## Overview

When Nix must **realize** a [store path](../02-concepts/store-path.md) that is not already local, it can **substitute**—fetch a bit-identical copy from a **substituter** instead of running the build. HTTP **binary caches** (for example [cache.nixos.org](https://cache.nixos.org/)) are the usual substituters: they serve compressed **NAR** (Nix Archive) payloads of store objects plus **`.narinfo`** metadata that tells the client where to download, how the archive is compressed, and how to verify it.

Substitution is an **operation** on the local store. A binary cache is a **remote store instance** that participates in that operation. NAR info is the **metadata format** (historically line-oriented `.narinfo` files; also described as JSON in the Store Object Info protocol) that bridges lookup, trust, and download. Operator configuration of cache URLs and keys lives on [Binary caches](binary-caches.md); hosting on [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md). This page covers the metadata and client fetch path.

## Details

**Three terms.**

| Term | Meaning |
|------|---------|
| Substitute | Realizing a path by copying from another store rather than building |
| Binary cache | A store exposed over HTTP (or similar) that can serve NARs for paths it holds |
| NAR info (`.narinfo`) | Per-path metadata describing the serialized object and how to fetch it |

**NAR serialization.** Binary caches transfer the filesystem-object part of a store object as a **Nix Archive**—a canonical binary serialization of files, directories, and symlinks. The digest of that serialization is **`NarHash`**; its byte length is **`NarSize`**. NAR format avoids timestamps and non-canonical archive ordering so the same tree always hashes the same way. See the manual section on [content-addressing file system objects](https://nix.dev/manual/nix/stable/store/file-system-object/content-address.html#serial-nix-archive).

**Classic `.narinfo` fields (wire format).** A binary cache serves `https://cache…/<hash>.narinfo` as line-oriented `Key: value` text. The fields you will see on public caches (do not invent others) include:

| Field | Role |
|-------|------|
| `StorePath` | Absolute store path for this object |
| `URL` | Relative (or absolute) location of the compressed NAR under the cache root |
| `Compression` | How the on-the-wire blob is compressed (e.g. `xz`, `zstd`) |
| `FileHash` | Digest of the **compressed** download bytes |
| `FileSize` | Size in bytes of the compressed download |
| `NarHash` | Digest of the **uncompressed** NAR serialization |
| `NarSize` | Size in bytes of the uncompressed NAR |
| `References` | Space-separated store path basenames this object refers to |
| `Deriver` | Basename of the `.drv` that produced the path (when known) |
| `Sig` | Signature line(s) binding the metadata for input-addressed paths |

Optional content-address markers (`CA: …`) can appear for content-addressed paths; treat anything beyond the table above as version- or cache-specific and confirm in the Store Object Info docs before documenting it.

**JSON / Store Object Info mapping (experimental).** `nix path-info --json` exposes the same facts under camelCase names documented as Store Object Info (JSON format experimental; schema version history in the manual). Rough map for the download-oriented fields:

| `.narinfo` | JSON (`path-info`) |
|------------|--------------------|
| `StorePath` | `path` (format depends on `--json-format`) |
| `URL` | `url` |
| `Compression` | `compression` |
| `FileHash` / `FileSize` | `downloadHash` / `downloadSize` |
| `NarHash` / `NarSize` | `narHash` / `narSize` |
| `References` | `references` |
| `Deriver` | `deriver` |
| `Sig` | `signatures` |

Schema lineage (manual): **0** = `.narinfo` lines; **1** / **2** = JSON variants. As of Nix **2.34**, `--json` without `--json-format` is deprecated; pass `--json-format 1` or `2`.

`References` lists other store paths the object depends on—substitution must eventually realize those members of the [closure](../02-concepts/closure.md) too. `Sig` / `signatures` are claims that an input-addressed path is authentic; whether they are required depends on `require-sigs`, `trusted-public-keys`, and store trust settings (see [Signing and caches](../14-security-and-trust/signing-and-caches.md)). Content-addressed paths are not gated on signatures.

**Cache-level metadata.** Each binary cache also publishes `/nix-cache-info` (fields such as `StoreDir`, `Priority`, `WantMassQuery`) so clients know the store directory prefix, substituter priority, and whether bulk path queries are supported. The default public cache uses priority **40**.

**Client lookup flow.** For a missing path `P`, Nix walks configured **substituters** (from `substituters` / `extra-substituters` in [`nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html), ordered by each cache's `Priority`) and roughly:

1. **Resolve metadata** — request `.narinfo` for `P` on the substituter (or use a cached prior lookup).
2. **Trust and sanity** — check signatures when required; confirm store directory matches expectations; read `References` for downstream fetches.
3. **Download** — fetch the compressed NAR at `URL`, verify `FileSize` / `FileHash` for the on-the-wire bytes.
4. **Unpack and register** — decompress per `Compression`, verify unpacked bytes against `NarHash` / `NarSize`, then register the path in the local store with the declared references.

If every substituter misses, Nix falls back to building. The same store path is the cache key whether the path was built locally or substituted.

**Lookup caching.** Nix caches substituter query results in a local SQLite database under `$XDG_CACHE_HOME/nix/` (commonly `~/.cache/nix/binary-cache-v*.sqlite*`). TTLs are controlled in `nix.conf` (defaults as of Nix **2.34** stable manual):

- `narinfo-cache-positive-ttl` — how long a successful path lookup (including some NAR metadata) is reused (default `2592000` s ≈ 30 days)
- `narinfo-cache-negative-ttl` — how long a "not found" result is reused (default `3600` s)
- `narinfo-cache-meta-ttl` — how long `/nix-cache-info` is reused (default `604800` s ≈ 7 days)

Shorter positive TTLs help when a cache garbage-collects frequently and stale metadata would cause hash mismatches on retry.

**Trust boundaries.** For Nix to use a given substituter URL, the caller must be in `trusted-users` **or** the URL must appear in `trusted-substituters`. Unprivileged users may only enable substituters listed in `trusted-substituters`. Paths copied from substituters generally need a signature from a key in `trusted-public-keys` unless `require-sigs` is false, the store URL is marked trusted, or the path is content-addressed. Policy details: [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md), [Signing and caches](../14-security-and-trust/signing-and-caches.md).

### Operator failure modes

**Signature / trust rejection.** When a substituter serves a path but Nix will not copy it, logs often include a warning like `ignoring substitute for '…' from 'https://…': not signed by any of the keys in trusted-public-keys`. The `.narinfo` may be valid; the client simply refuses the realisation. Fix by aligning trust with the cache: add the cache’s public key to `trusted-public-keys` (or `extra-trusted-public-keys`), ensure the substituter URL is permitted (`substituters` / `trusted-substituters`), and confirm `require-sigs` and store trust (`trusted=true` on the store URL) match your policy. Unprivileged callers cannot enable arbitrary caches—only URLs already in `trusted-substituters` (or a trusted-user session) count. Content-addressed paths skip signature checks; input-addressed paths from third-party caches usually need both key and URL trust configured.

**Stale narinfo cache.** Substituter lookups are cached locally in SQLite under `$XDG_CACHE_HOME/nix/` (files named like `binary-cache-v*.sqlite*`). A stale **positive** entry can keep skipping a cache you fixed (keys added, path re-published) because Nix reuses old metadata without re-fetching `.narinfo`. A stale **negative** entry can keep ignoring a substituter you removed or that briefly failed. Mitigations: lower the relevant TTL in `nix.conf`; for a one-off, pass `--option narinfo-cache-positive-ttl 0` (or the negative/meta TTL) so lookups refresh; or delete the `binary-cache-*.sqlite*` file for the affected user (when the **daemon** substitutes, that is often **root**—e.g. `/root/.cache/nix/`—not only the invoking user’s home cache).

**Hash / download failures.** After metadata is accepted, Nix verifies the compressed blob against `FileHash` / `FileSize`, then the decompressed NAR against `NarHash` / `NarSize`. Mismatch usually means wrong bytes (corrupt cache object, truncated download, MITM, or stale `.narinfo` pointing at an old `URL`). Do not disable hash or signature checks to “get unblocked”—that removes the substitute’s safety model. Retry another substituter, clear narinfo cache if metadata may be stale, or let Nix **build** when every substituter misses or fails verification.

**Multiple caches.** When several substituters expose the same path, each cache’s `Priority` from `/nix-cache-info` orders attempts (lower number wins; `cache.nixos.org` defaults to **40**). A higher-priority private cache can satisfy the path before the public cache is tried—useful when mirroring, but confusing if the “wrong” cache serves an older or unsigned build.

**Quick checks.** Reproduce metadata outside a full build with the [Examples](#examples) commands (`curl …/.narinfo`, `nix path-info --json --store …`). Compare `Sig` / `signatures` against `trusted-public-keys`; if trust was recently fixed, combine with `--option narinfo-cache-positive-ttl 0` once to bypass cached rejections.

## Examples

**Fetch `.narinfo` from the public cache** (hash part of the store path; values change with nixpkgs revisions). Verified live against `cache.nixos.org` (Nix 2.34-era):

```bash
curl -sL https://cache.nixos.org/c2h2f4cw9p8i8zcfy52fd1dd6g0yhnki.narinfo
```

Response shape (abbreviated):

```text
StorePath: /nix/store/c2h2f4cw9p8i8zcfy52fd1dd6g0yhnki-hello-2.12.3
URL: nar/0jvbywkmjaq0rxzvw9yi1rcpv4y57j23m7xhhhjd3isq93qldr6i.nar.zst
Compression: zstd
FileHash: sha256:0zbkbqr85p8dnarsfsksqiq3fhh75dig6lm4mkjak2kx06fvl7hd
FileSize: 75354
NarHash: sha256:0jvbywkmjaq0rxzvw9yi1rcpv4y57j23m7xhhhjd3isq93qldr6i
NarSize: 279624
References: c2h2f4cw9p8i8zcfy52fd1dd6g0yhnki-hello-2.12.3 l8si8gnvvq93yzms1jsgh5aixyf9rl5x-glibc-2.42-67
Deriver: 0nnrl637vw6ibnjym17l3s0yzj5zr77n-hello-2.12.3.drv
Sig: cache.nixos.org-1:2yH72VfOKVh05O+RaOhTYJJDduq1kyGDT+L6ykNp5gqdxOPOe7hWQgXzJLGhJ06pwq5hPxv5Os2RdpIFlFCpAQ==
```

Client steps for that path: verify `Sig` against `trusted-public-keys`, download the NAR at `URL`, check `FileHash`/`FileSize`, decompress (`zstd`), confirm `NarHash`/`NarSize`, register locally, then repeat for any missing `References`.

**Inspect the same metadata as JSON** (download fields included when querying a binary-cache store; JSON schema is experimental):

```bash
nix path-info --json --json-format 1 --store https://cache.nixos.org/ \
  /nix/store/c2h2f4cw9p8i8zcfy52fd1dd6g0yhnki-hello-2.12.3
```

## References

- [Nix reference manual — Store Object Info](https://nix.dev/manual/nix/stable/protocols/json/store-object-info.html) — JSON schema, NAR-info field mapping, and `.narinfo` as version 0 of that lineage (Nix 2.34; there is no separate `…/protocols/binary-cache-narinfo.html` page on stable)
- [Nix reference manual — Serving a store via HTTP](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) — substituters, `nix-cache-info`, and client configuration
- [Nix reference manual — `nix help-stores`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) — HTTP / file / S3 binary cache store types
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `substituters`, trust settings, and `narinfo-cache-*` TTLs
- [Nix reference manual — Nix Archive (NAR)](https://nix.dev/manual/nix/stable/store/file-system-object/content-address.html#serial-nix-archive) — canonical serialization used for `NarHash`
- [Nix documentation — Add a binary cache](https://nix.dev/guides/recipes/add-binary-cache) — operator recipe for serving and trusting a cache

## See also

- [Binary caches](binary-caches.md) — operating and configuring cache endpoints
- [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) — serving and pushing signed caches
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — signatures, keys, and trust policy
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — who may enable caches and how keys combine with `require-sigs`
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — signatures and `.narinfo` as binary trust across machines
- [Store protocols](store-protocols.md) — store URIs including HTTP / file / S3 caches
