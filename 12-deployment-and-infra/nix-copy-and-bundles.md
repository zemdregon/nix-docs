---
status: complete
---

# Nix Copy and Bundles

## Overview

`nix copy` and `nix bundle` are experimental new-CLI commands (Nix 2.34.x; need `nix-command`, and flakes when installables are flake refs). Interfaces may change.

**`nix copy`** ships store-path **closures** between Nix stores (`--from` / `--to`; omit either for the local store). Use it to fill a [binary cache](binary-cache-hosting.md), push a NixOS system over `ssh://`, or move paths into a chroot store.

**`nix bundle`** packs an installable’s closure for use outside `/nix/store`. The default result is a self-extracting executable (**Linux only**). Custom formats go through `--bundler` (default flake `github:NixOS/bundlers`).

## Details

### `nix copy`

Copies the closure of each installable from the source store to the destination. Store URIs follow the usual [store protocols](../04-store-and-build/store-protocols.md) (`file://…`, `ssh://…`, `s3://…`, bare paths, and so on).

**`file://` vs bare path.** `file:///tmp/cache` is a **local binary cache** (narinfo + NARs on disk). A bare path such as `/tmp/nix` is a **chroot store** (logical `/nix/store` under that root). Mixing them up is a common footgun; the manual calls this out explicitly.

**Same logical `store`.** Each store has a `store` setting (usually `/nix/store`). The manual states you can only copy paths between stores that share that setting (see local binary cache store docs under References).

**Useful flags (from the 2.34 manual):**

| Flag | Role |
|------|------|
| `--from` / `--to` | Source and destination store URIs |
| `--all` | Operate on every path in the source store |
| `--substitute-on-destination` / `-s` | Let the destination try substitutes (SSH stores) |
| `--no-check-sigs` | Skip signature checks (often needed for unsigned chroot copies) |
| `--profile` | Point a profile at a copied top-level path |
| `--out-link` / `-o` | Symlink prefix for fetched top-level paths |

The global `--offline` flag disables substituters during copy (pair with `--from`/`--to` stores when you want no network fetch; [Airgap and offline](airgap-and-offline.md) covers sneakernet).

S3 destinations need a Nix build with AWS support. Signing and trust for cache destinations belong under [Signing and caches](../14-security-and-trust/signing-and-caches.md). Higher-level remote NixOS updates often wrap copy under [Remote deploy](../09-nixos/operations/remote-deploy.md) rather than calling `nix copy` by hand.

### `nix bundle`

By default, packs the installable’s closure into one self-extracting executable (see the [bundlers](https://github.com/NixOS/bundlers) repo for format details). **Linux only.**

A **bundler** is a flake output under `bundlers.<system>.…`: a function from an arbitrary value (typically a derivation or app) to a derivation. Default bundler flake: `github:NixOS/bundlers`. Override with `--bundler` (for example `github:NixOS/bundlers#toDockerImage`). That Docker path is a cousin of [OCI / container packaging](../11-development/containers-oci.md), not a substitute for it.

Without an attribute name, Nix tries `bundlers.<system>.default`. With a name, it tries `bundlers.<system>.<name>`. `--out-link` / `-o` renames the result symlink (default: base name of the app).

The default `github:NixOS/bundlers` flake is community-maintained and may change without notice.

## Examples

Copy a path into a local binary cache (note `file://`):

```bash
nix copy --to file:///tmp/cache $(type -p firefox)
```

Pull everything from that cache into the local store:

```bash
nix copy --all --from file:///tmp/cache
```

Ship the current NixOS system over SSH; let the remote substitute when that is faster than the SSH link (`-s` is the short form):

```bash
nix copy --substitute-on-destination --to ssh://server /run/current-system
```

Copy into a chroot store (unsigned paths need `--no-check-sigs`):

```bash
nix copy --to /tmp/nix nixpkgs#hello --no-check-sigs
```

Default self-extracting bundle, then a Docker-image bundler:

```bash
nix bundle nixpkgs#hello
./hello

nix bundle --bundler github:NixOS/bundlers#toDockerImage nixpkgs#hello
docker load < hello-2.10.tar.gz
```

## See also

- [Binary cache hosting](binary-cache-hosting.md) — populating and serving caches (`nix copy --to`)
- [Airgap and offline](airgap-and-offline.md) — USB / sneakernet with `file://` caches
- [Store protocols](../04-store-and-build/store-protocols.md) — store URIs (`file://`, `ssh://`, chroot roots)
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — `nixos-rebuild` paths that use `nix copy`
- [Signing and caches](../14-security-and-trust/signing-and-caches.md) — signatures and substituter trust
- [Containers / OCI](../11-development/containers-oci.md) — container images vs Docker bundlers

## References

- [nix copy (Nix 2.34)](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-copy.html)
- [nix bundle (Nix 2.34)](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-bundle.html)
- [Local binary cache store (Nix 2.34)](https://nix.dev/manual/nix/2.34/store/types/local-binary-cache-store.html)
- [NixOS/bundlers](https://github.com/NixOS/bundlers)
