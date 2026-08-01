---
status: index
---

# Deployment and Infra

Deploy tools, disk, secrets, Hydra, and caches. Tool pick: [Fleet deploy](../cheatsheets/fleet-deploy.md).

## Contents

- [Colmena](colmena.md) — Hub→hosts NixOS deploy (Colmena “hive” attrset; ≠ Digga/Hive / mesh)
- [deploy-rs](deploy-rs.md) — Rust-based flake deploy
- [Morph / Nixinate](morph-nixinate.md) — Other deploy tools
- [Terraform + NixOS](terraform-nixos.md) — IaC pairing
- [disko](disko.md) — Declarative disk partitioning
- [agenix / sops-nix](agenix-sops-nix.md) — Secrets deployment
- [Hydra](hydra.md) — CI/CD for Nix
- [Binary Cache Hosting](binary-cache-hosting.md) — Hosting substituters
- [Clan and mesh](clan-and-mesh.md) — Clan multi-machine / mesh-oriented management (vs hub deploy)
- [Nix copy and bundles](nix-copy-and-bundles.md) — Closure shipping (`nix copy`) and `nix bundle`
- [Airgap and offline](airgap-and-offline.md) — Offline install/update; USB / file:// substituters
- [Self-healing config mesh](self-healing-config-mesh.md) — Intentional design draft (not a shipped tool; out of v1 complete set)
