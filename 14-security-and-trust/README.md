---
status: index
---

# Security and Trust

Trust boundaries, sandboxes, secrets, and signing.

## Contents

- [Supply Chain](supply-chain.md) — Dependency and build trust
- [Trusted Users](trusted-users.md) — Trust model for the daemon
- [Sandbox Escape Surface](sandbox-escape-surface.md) — Build sandbox boundaries
- [Secrets Management](secrets-management.md) — Keeping secrets out of the store
- [SSH and age plugins](ssh-and-age-plugins.md) — Host keys, age plugins, YubiKey patterns
- [Signing and Caches](signing-and-caches.md) — Signed binary caches
- [AppArmor and SELinux](apparmor-selinux.md) — MAC frameworks on NixOS (maturity-stamped)
- [Reproducible builds audit](reproducible-builds-audit.md) — `--check` / `--rebuild`, diffoscope, what “reproducible” means
- [Inter-machine trust](inter-machine-trust.md) — Fleet/mesh trust axes (reachability, build, binary, deploy, secrets, supply chain)
