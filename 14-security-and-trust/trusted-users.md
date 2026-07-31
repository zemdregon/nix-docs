---
status: complete
---

# Trusted Users

## Overview

In multi-user Nix, `trusted-users` names who may exercise elevated daemon privileges—adding substituters, importing unsigned store objects, and otherwise shaping how builds and substitutions run. That is a different axis from `allowed-users`, which only gates who may connect. The Nix manual treats membership as essentially root-equivalent for store integrity. Prefer least privilege: keep the list small rather than trusting every local account.

This setting is **local daemon privilege**, not fleet or mesh membership. Putting someone in `trusted-users` on one machine does not grant trust across a group of hosts; conversely, deploying or peering machines does not require (and should not imply) `trusted-users = *`. Operational wiring lives under [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) and [`nix.conf`](../05-cli-and-tooling/config/nix-conf.md).

## Details

**`allowed-users` vs `trusted-users`.** `allowed-users` is a whitespace-separated list of users (or `@group`, or `*`) permitted to talk to the Nix daemon. Default is `*`. Users in `trusted-users` can always connect even if omitted from `allowed-users`. `trusted-users` (default `root`) get additional rights when connecting to the daemon: specifying additional substituters, importing unsigned realisations or unsigned input-addressed store objects, and other privileged daemon operations that affect builds and substitution. Groups use the same `@wheel` style prefix.

**Substituters and signatures.** For Nix to use a substituter, either the URL is listed in `trusted-substituters`, or the calling user is in `trusted-users`. Unprivileged users may only enable URLs already in `trusted-substituters`. Trusted users can add caches more freely. Separately, they can import unsigned objects into the store—bypassing the usual signature gate that `require-sigs` (default `true`) enforces for ordinary substitution. Disabling signature checks system-wide (`require-sigs = false`) or marking a store `trusted=true` is a broader trust decision; see [Signing and caches](signing-and-caches.md).

**Why trust is root-like.** The manual warns that adding a user to `trusted-users` is essentially equivalent to giving that user root access to the system. A trusted client can influence which binary caches are accepted, import unsigned paths into the store, and access or replace store contents that matter for system security. Treat the list as a security boundary, not a convenience switch for everyday developer workflow.

**Not mesh membership.** `trusted-users` is per-daemon configuration on one install. It does not define who may SSH to builders, who may push to a shared cache, or who is “in” a multi-machine deploy graph. Those are separate trust axes (reachability, builders, substituter keys, deploy credentials). Anti-pattern: treating `trusted-users = *` (or every interactive account) as “everyone on this fleet is trusted.”

**Least privilege.** Prefer `allowed-users` plus `trusted-substituters` / `trusted-public-keys` so unprivileged accounts can build and use pre-approved caches without becoming trusted. Avoid patterns that put `*` or every interactive user into `trusted-users`. Grant trust only to operators who need to change substitution policy or import unsigned objects; revoke when that role ends. Related hardening: [Signing and caches](signing-and-caches.md), [Sandbox escape surface](sandbox-escape-surface.md).

**Where it is configured.** Settings belong in the system `nix.conf` the daemon reads—user conf alone cannot redefine daemon trust policy. On NixOS, set `nix.settings.trusted-users` (and usually `nix.settings.allowed-users`) in configuration; values are written into the generated Nix conf. List settings also support an `extra-` append form (e.g. `extra-trusted-users`).

## Examples

Minimal daemon policy (illustrative `nix.conf`): trust only root; allow everyone to connect:

```ini
allowed-users = *
trusted-users = root
```

NixOS equivalent—grant trust to `root` and the `wheel` group only when those accounts truly need elevated daemon rights:

```nix
{
  nix.settings = {
    allowed-users = [ "*" ];
    trusted-users = [ "root" "@wheel" ];
  };
}
```

Prefer enabling a specific cache for untrusted users instead of widening trust:

```ini
# Unprivileged users may enable only URLs listed here
trusted-substituters = https://cache.nixos.org/ https://example-cache.example/
# Matching public keys still required under require-sigs
```

## See also

- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — daemon trust vs substituter and key settings
- [nix.conf](../05-cli-and-tooling/config/nix-conf.md) — config file locations and option priority
- [Signing and caches](signing-and-caches.md) — signatures, keys, and cache trust
- [Sandbox escape surface](sandbox-escape-surface.md) — build sandbox and privilege boundaries
- [Remote builders](../04-store-and-build/remote-builders.md) — cross-machine builds (orthogonal to local `trusted-users`)
- [Machine mesh](../02-concepts/machine-mesh.md) — mesh ≠ trusted-users
- [Inter-machine trust](inter-machine-trust.md) — six axes; local trusted-users is only one local piece

## References

- [Nix manual — `trusted-users`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-trusted-users) — privileges, `@group` syntax, root-equivalence warning; default `root`
- [Nix manual — `allowed-users`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-allowed-users) — who may connect; trusted users always may
- [Nix manual — `trusted-substituters`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-trusted-substituters) — URLs unprivileged users may enable
- [Nix manual — `nix.conf` configuration settings](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — full settings reference (`substituters`, `require-sigs`, …)
