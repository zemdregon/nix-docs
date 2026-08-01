---
status: complete
last-checked: 2026-08
---

# Binary caches

Chooser for three roles: **substitute** (client pulls prebuilts via `substituters` / keys), **host** (serve or publish a store: nix-serve, Harmonia, Attic, Cachix, S3/`file://`), **sign** (Ed25519 secret on the write path; clients list the public half in `trusted-public-keys`). Not a full client/hosting/signing tutorial—use the linked leaves. Client knobs: [nix.conf knobs](nix-conf-knobs.md). Wire format: [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md).

## Decision table

| Situation | Prefer | Leaf | Avoid if… |
|-----------|--------|------|-----------|
| Only need public Nixpkgs / NixOS prebuilts | Default `https://cache.nixos.org/` + its key | [Binary caches](../04-store-and-build/binary-caches.md) | You also need private/org paths that are never on that cache |
| Add a private / third-party cache on clients | `extra-substituters` + matching `extra-trusted-public-keys`; allow-list in `trusted-substituters` for unprivileged users | [Binary caches](../04-store-and-build/binary-caches.md) · [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) | Replacing `trusted-public-keys` and dropping `cache.nixos.org-1` |
| Share one builder’s live `/nix/store` over HTTP | **nix-serve** or **Harmonia** (+ sign key on server) | [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) | Need durable multi-tenant storage; GC on the host removes substitutable paths |
| Durable self-hosted multi-tenant cache | **Attic** (S3-compatible backend; server-side signing) | [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) | You only want “HTTP from this builder’s store”; upstream still labels Attic an early prototype |
| Managed SaaS; minimal ops | **Cachix** (`cachix use` / `cachix push`) | [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) · [CI with Nix](../11-development/ci-with-nix.md) | Must keep paths on your own infra only |
| Populate object storage or a directory tree | `nix copy --to 's3://…?secret-key=…'` or `file:///…?secret-key=…` | [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) | Expecting a live builder store without an upload/serve step |
| Create / place signing keys | `nix-store --generate-binary-cache-key`; secret only on signer/host | [Signing and caches](../14-security-and-trust/signing-and-caches.md) | Distributing the secret to every client |
| CI / Hydra should feed a project cache | Build → push (`cachix` / `attic` / `nix copy`); clients only substitute | [CI with Nix](../11-development/ci-with-nix.md) · [Hydra](../12-deployment-and-infra/hydra.md) | Committing write tokens or signing secrets |
| Untrusted user / “just turn off sigs” | Keep `require-sigs = true`; use `trusted-substituters` + keys (or a trusted user) | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) · [Signing and caches](../14-security-and-trust/signing-and-caches.md) | `require-sigs = false` / store `trusted=true` without understanding binary authenticity |

Remote builders pulling their own caches: `builders-use-substitutes` — [Remote builders](../04-store-and-build/remote-builders.md). Binary authenticity vs daemon privilege: [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md).

## Failure callouts

| Symptom / mistake | Fix |
|-------------------|-----|
| Unprivileged user: substituter ignored / “untrusted substituter” | URL must be in daemon `trusted-substituters`, or the caller in `trusted-users` ([Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md)) |
| Substituter URL set but no matching `trusted-public-keys` | Add the cache’s public key (`extra-trusted-public-keys`); with `require-sigs` on, unsigned/non-matching sigs reject non-CA paths ([Signing and caches](../14-security-and-trust/signing-and-caches.md)) |
| Set `trusted-public-keys = my-cache-1:…` and lost `cache.nixos.org` | That setting **replaces** the default list—keep `cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=` (or use `extra-trusted-public-keys`) |
| Confusing `trusted-users` with signatures | `trusted-users` = who may *configure* substituters / import unsigned; `trusted-public-keys` = which NAR signatures count—orthogonal ([Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md)) |
| `require-sigs = false` (or store `trusted=true`) to “make the cache work” | Prefer signing + client keys; disabling checks trusts whoever can write that cache ([Signing and caches](../14-security-and-trust/signing-and-caches.md)) |
| Cache miss vs download failure | Miss → local build. Failed fetch of a known substitute only falls back if `fallback` is true (default `false`)—[Binary caches](../04-store-and-build/binary-caches.md) · [nix.conf knobs](nix-conf-knobs.md) |

## See also

- [Binary caches](../04-store-and-build/binary-caches.md)
- [Substitutes and NAR info](../04-store-and-build/substitutes-and-narinfo.md)
- [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md)
- [Signing and caches](../14-security-and-trust/signing-and-caches.md)
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md)
- [nix.conf knobs](nix-conf-knobs.md)
- [CI with Nix](../11-development/ci-with-nix.md)
- [Flake CI with GitHub Actions (worked example)](../16-configuration-examples/flake-ci-github-actions.md)
- [Hydra](../12-deployment-and-infra/hydra.md)
- [Remote builders](../04-store-and-build/remote-builders.md)
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md)

## References

- [cache.nixos.org](https://cache.nixos.org/) — default public binary cache
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — `substituters`, `trusted-public-keys`, `trusted-substituters`, `require-sigs`, `fallback`, `builders-use-substitutes`
- [Nix reference manual — Serving a Nix store via HTTP](https://nix.dev/manual/nix/stable/package-management/binary-cache-substituter.html) — `nix-serve`, client substituters
- [Nix reference manual — `nix-store --generate-binary-cache-key`](https://nix.dev/manual/nix/stable/command-ref/nix-store/generate-binary-cache-key.html) — Ed25519 key pair (stable)
- [Cachix documentation](https://docs.cachix.org/) — hosted push/pull
- [Attic](https://github.com/zhaofengli/attic) — self-hosted multi-tenant cache ([docs](https://docs.attic.rs/); early prototype)
- [Harmonia](https://github.com/nix-community/harmonia) — Rust binary cache serving `/nix/store`
