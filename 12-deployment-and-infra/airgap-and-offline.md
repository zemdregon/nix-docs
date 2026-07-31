---
status: complete
---

# Airgap and Offline

## Overview

An **airgapped** or otherwise offline Nix host still needs store paths realised locally. The practical pattern is: build or substitute a closure on a networked machine, write it to removable media (or another sneakernet path) as a [local binary cache](../04-store-and-build/binary-caches.md) (`file://…`), then copy or substitute from that cache on the isolated machine.

Prefer experimental [`nix copy`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-copy.html) (Nix **2.34.x**) with a `file://` destination over ad-hoc NAR pipes. Airgap does not remove the need for installer media, a matching architecture, enough disk, and—when you evaluate or rebuild configs offline—the flake (or channel) sources and lock file on the stick as well. For NixOS install without network, see [Manual install](../09-nixos/installation/manual-install.md).

## Details

**Online → media.** On a machine that can build or substitute, realise the closure you need, then copy it into a filesystem binary cache:

```bash
nix copy --to file:///mnt/usb/cache <installable-or-store-path>
```

The `file://` prefix matters: without it, Nix treats the destination as a chroot store, not a binary-cache layout. The local binary cache store (`file://` *path*) creates *path* if missing and stores NAR + `.narinfo` content there. Both ends must share the same logical `store` setting (default `/nix/store`); mismatched store roots cannot share paths.

**Media → offline.** On the airgapped host, pull specific paths or everything present in the cache:

```bash
nix copy --from file:///mnt/usb/cache /nix/store/…-pkg
nix copy --all --from file:///mnt/usb/cache
```

Alternatively, list `file:///mnt/usb/cache` under `substituters` (and, on multi-user installs, ensure it is allowed via `trusted-substituters` or a trusted user) so ordinary builds can substitute from the stick. Hosting and client config patterns overlap with [Binary cache hosting](binary-cache-hosting.md); store URI schemes are summarised in [Store protocols](../04-store-and-build/store-protocols.md). Sibling detail on `nix copy` and related transfer shapes: [nix copy and bundles](nix-copy-and-bundles.md).

**`--offline`.** On Nix commands that expose it (including `nix copy`), `--offline` disables substituters and treats previously downloaded files as up-to-date. Use it when you must not reach the network, not as a substitute for provisioning the needed closure onto media first.

**Signing and trust.** Prefer a [signed](../14-security-and-trust/signing-and-caches.md) cache (`secret-key` / `secret-keys` on the write side; matching `trusted-public-keys` on the read side). Escape hatches such as store URL `trusted=true` or `--no-check-sigs` avoid signature checks at a real trust cost—only for media you fully control.

**What the stick must also carry.** Binary paths alone are not enough for many workflows: bring the Nix/NixOS installer (or a working Nix already on the machine), match `system` / architecture, leave room on disk for the closure, and copy evaluation inputs (flake source + `flake.lock`, or channel snapshots) if the offline machine will evaluate or rebuild rather than only realise precomputed store paths.

**Classic export/import.** Stable `nix-store --export` writes store objects to stdout; `--import` reads that stream. Export does **not** auto-include the closure—collect paths with `nix-store --query --requisites` first, or imports fail on missing references. Prefer `nix copy` + `file://` for day-to-day sneakernet; keep export/import for scripts or opaque streams. The Nix 2.34 export manual illustrates a hello closure via `nix-store --query --requisites` piped to a USB block device with `dd`—a low-level pattern, not the usual file-cache workflow.

## Examples

**Seed a USB binary cache from a built system closure** (online builder; experimental `nix copy`, Nix 2.34.x):

```bash
# After realising the path (build or substitute):
nix copy --to file:///mnt/usb/cache /run/current-system
# Or a flake output:
# nix copy --to file:///mnt/usb/cache .#nixosConfigurations.host.config.system.build.toplevel
```

**Import on the airgapped machine:**

```bash
nix copy --from file:///mnt/usb/cache /nix/store/…-nixos-system-…
# or every path written to the cache:
nix copy --all --from file:///mnt/usb/cache
```

**Use the stick as a substituter** (trusted-user / daemon config as appropriate). Prefer signing over `trusted=true` (see [Signing and caches](../14-security-and-trust/signing-and-caches.md)):

```bash
# Illustrative nix.conf: only the local cache (no https:// substituters)
# substituters = file:///mnt/usb/cache
# trusted-public-keys = …   # keys that signed the cache
nix build .#packages.x86_64-linux.default
```

Do not combine that with `--offline` if you still need substitution: `--offline` disables substituters. Use `--offline` when the required paths are already in the local store (for example after `nix copy --from file://…`) and you must not query the network.

**Classic closure export to a file** (stable `nix-store`; not auto-closure—query requisites first):

```bash
storePath=$(nix-build '<nixpkgs>' -A hello --no-out-link)
nix-store --export $(nix-store --query --requisites "$storePath") > /mnt/usb/hello.closure
# Offline host:
# nix-store --import < /mnt/usb/hello.closure
```

The export manual’s USB/`dd` variant writes the same stream to a block device instead of a file; prefer `nix copy --to file://…` when you want a reusable binary-cache layout.

## See also

- [nix copy and bundles](nix-copy-and-bundles.md)
- [Binary cache hosting](binary-cache-hosting.md)
- [Binary caches](../04-store-and-build/binary-caches.md)
- [Store protocols](../04-store-and-build/store-protocols.md)
- [Signing and caches](../14-security-and-trust/signing-and-caches.md)
- [Manual install](../09-nixos/installation/manual-install.md)

## References

- [nix copy (Nix 2.34)](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-copy.html) — `--to` / `--from`, `file://` binary-cache note, `--all`, `--offline`, `--no-check-sigs`
- [Local binary cache store (`file://`)](https://nix.dev/manual/nix/2.34/store/types/local-binary-cache-store.html) — layout, `store` matching, `trusted`, `secret-key(s)`
- [nix-store --export (Nix 2.34)](https://nix.dev/manual/nix/2.34/command-ref/nix-store/export.html) — serialise paths (not auto-closure)
- [nix-store --import (Nix 2.34)](https://nix.dev/manual/nix/2.34/command-ref/nix-store/import.html) — restore exported streams
