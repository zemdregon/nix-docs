---
status: complete
---

# Trusted Users and Substituters

## Overview

In multi-user Nix, the daemon decides **who may talk to it** and **who may change substitution trust**. [`allowed-users`](../../14-security-and-trust/trusted-users.md) gates daemon connections; [`trusted-users`](../../14-security-and-trust/trusted-users.md) get elevated rights—notably adding substituters, and importing unsigned realisations or unsigned input-addressed store objects. **Substituters** are Nix store URLs queried for pre-built paths instead of building; non-content-addressed paths from them must usually be signed with a key in `trusted-public-keys`. Settings live in [`nix.conf`](nix-conf.md).

`trusted-users` is **local daemon privilege on one install**. It is not multi-machine inter-trust, mesh membership, or deploy authority—putting someone in `trusted-users` here does not grant trust across a fleet, and peering machines does not require `trusted-users = *`. Contrast [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md) (reachability, build, binary, deploy, secret, supply-chain axes).

For cache workflow end-to-end, see [Binary caches](../../04-store-and-build/binary-caches.md). Security model: [Trusted users](../../14-security-and-trust/trusted-users.md).

## Details

Defaults below match the Nix **stable** [`nix.conf` manual](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) (~**Nix 2.34** as of 2026-07). Knob cheat sheet: [nix.conf knobs](../../cheatsheets/nix-conf-knobs.md).

**`allowed-users` vs `trusted-users`.** `allowed-users` is a whitespace-separated list of users (or `@group` names, or `*`) permitted to connect to the Nix daemon. Default is `*`. Users listed in `trusted-users` can always connect, even if omitted from `allowed-users`. `trusted-users` (default `root`) may specify additional substituters, import unsigned realisations or unsigned input-addressed store objects, and otherwise act with elevated daemon privileges. Groups use the same `@wheel` prefix. On NixOS, configurations commonly include `@wheel` alongside `root`. The manual warns that membership is essentially equivalent to root on the system—a trusted user can replace store path contents that matter for security.

**Not inter-machine trust.** Daemon `trusted-users` answers “may this local account drive privileged store operations on **this** daemon?” Separate questions—SSH reachability to a builder, whose NAR signatures you accept, who may activate a generation, who may decrypt secrets—are different axes. Remote-builder setups often list a **remote** SSH identity in that host’s `trusted-users`; that is still per-daemon privilege on the builder, not fleet-wide mesh membership. See [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md) and [Trusted users](../../14-security-and-trust/trusted-users.md).

**Substituters and keys.** `substituters` lists store URLs to query (default `https://cache.nixos.org/`). Substituters are tried by priority (lower number wins; cache.nixos.org defaults to 40). URL schemes and per-store settings: [`nix help-stores`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html). `trusted-public-keys` lists public keys whose signatures Nix accepts when copying non-content-addressed paths from other stores (default includes the official `cache.nixos.org-1:…` key). Under default `require-sigs = true`, accepting a substituted non-content-addressed path needs a matching trusted signature (or a store URL with `trusted=true`, or content-addressedness). A public substituter without a corresponding trusted key will not yield usable non-CA paths under normal signature checking.

**Who may enable a cache.** For Nix to use a substituter, either the URL is in `trusted-substituters`, or the calling user is in `trusted-users` ([conf-file `substituters`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-substituters)). Unprivileged users (in `allowed-users` but not `trusted-users`) may pass `--substituters` / user config only for URLs already listed in `trusted-substituters`. That blocks arbitrary third-party caches from being enabled by untrusted accounts. Trusted users can add caches more freely.

**`extra-` list prefixes.** List settings support an `extra-` form that appends rather than replaces: e.g. `extra-substituters` and `extra-trusted-public-keys` (also via `--extra-substituters` / `--option`). Operators often keep the system `substituters` / `trusted-public-keys` minimal and allow users to request additional caches only when those URLs and keys are permitted by trust policy (`trusted-substituters` + matching keys, or a trusted user).

**Related flags.** `require-sigs` (default `true`) requires a trusted signature before accepting substituted non-content-addressed paths, unless the store URL is `trusted=true` or the path is content-addressed; set `false` only with clear security awareness. `always-allow-substitutes` (default `false`) ignores derivation `allowSubstitutes` and always attempts substitution when substituters are available. Deprecated aliases still documented in the conf-file manual include `binary-caches` → `substituters`, `binary-cache-public-keys` → `trusted-public-keys`, `trusted-binary-caches` → `trusted-substituters`. Signing models and operational hardening: [Signing and caches](../../14-security-and-trust/signing-and-caches.md).

## Examples

Config fragments match conf-file option names and defaults (~Nix 2.34). Keys and third-party URLs are **illustrative**—replace with keys you actually trust. Runtime checks that do not need a private cache: `nix config show trusted-users` / `substituters` / `require-sigs` (needs `experimental-features = nix-command`; verified on Nix 2.34.8).

Typical multi-user `nix.conf` fragment:

```ini
# Who may use the daemon vs who may change trust
allowed-users = *
trusted-users = root @wheel

# Default public cache (often already the built-in defaults)
substituters = https://cache.nixos.org/
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=

# Caches unprivileged users are allowed to enable
trusted-substituters = https://cache.nixos.org/ https://example-cache.example/
extra-trusted-public-keys = example-cache.example-1:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
```

NixOS equivalent (daemon policy belongs in system config the daemon reads):

```nix
{
  nix.settings = {
    trusted-users = [ "root" "@wheel" ];
    # Prefer allow-listed caches over trusting every interactive user:
    # trusted-substituters = [ "https://example-cache.example/" ];
    # extra-trusted-public-keys = [ "example-cache.example-1:…" ];
  };
}
```

Untrusted user requesting only a pre-approved cache:

```bash
# Succeeds only if the URL is in trusted-substituters (and the key is trusted)
nix build --substituters 'https://example-cache.example/' nixpkgs#hello
```

Force source builds or relax signature checks (use carefully):

```bash
nix build --option substitute false nixpkgs#hello
# require-sigs = false  # nix.conf — disables signature checking; security-sensitive
```

Inspect effective trust-related settings:

```bash
nix config show trusted-users
nix config show substituters
nix config show trusted-public-keys
nix config show require-sigs
```

## See also

- [nix.conf](nix-conf.md) — configuration file locations and option syntax
- [nix.conf knobs](../../cheatsheets/nix-conf-knobs.md) — dense trust/cache knob table
- [Binary caches](../../04-store-and-build/binary-caches.md) — substituters, priorities, and operator workflow
- [Trusted users](../../14-security-and-trust/trusted-users.md) — trust model and privilege implications
- [Signing and caches](../../14-security-and-trust/signing-and-caches.md) — signatures, keys, and cache trust
- [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md) — binary / build trust vs daemon `trusted-users`

## References

- [Nix manual — `nix.conf` configuration settings](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) (`allowed-users`, `trusted-users`, `substituters`, `trusted-public-keys`, `trusted-substituters`, `require-sigs`, `always-allow-substitutes`; stable → Nix **2.34** as of 2026-07)
- [Nix manual — Store types (`nix help-stores`)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) (substituter URL schemes; experimental interface)
- [Nix manual — Serving a Nix store via HTTP](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) (client `--substituters` / `substituters` usage)
