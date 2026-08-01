---
status: complete
last-checked: 2026-08
---

# Fleet deploy

Day-2 hub deploy (evaluate → copy over SSH → activate) vs install-time wipe/install vs peer/mesh fleets. Fresh install ≠ ongoing update. Colmena, deploy-rs, Morph, Nixinate, and bare `nixos-rebuild --target-host` are **hub → hosts** SSH push; Clan adds inventory + declared networking/mesh, not a Colmena-style hive.

## Decision table

| Situation | Prefer | Leaf | Avoid if… |
|-----------|--------|------|-----------|
| 1–few already-NixOS hosts; same CLI as local rebuild | `nixos-rebuild --target-host` / `--build-host` | [Remote deploy](../09-nixos/operations/remote-deploy.md) | Need tags, parallel fleets, multi-profile, or magic-rollback |
| Many hosts; tags / parallel apply; classic or flake hive | **Colmena** (`colmena apply --on @tag`) | [Colmena](../12-deployment-and-infra/colmena.md) | Expecting peer mesh / no-central-controller ops (use Clan) |
| Multi-profile (system + Home Manager / darwin) on flakes | **deploy-rs** (`deploy.nodes` / profiles) | [deploy-rs](../12-deployment-and-infra/deploy-rs.md) | Non-flake Morph-style network file only |
| Need post-activate SSH confirm + auto rollback | **deploy-rs** magic-rollback (default on) | [deploy-rs](../12-deployment-and-infra/deploy-rs.md) | You intentionally change SSH port/IP mid-deploy (disable carefully) |
| Existing Morph `network` deployment file | **Morph** (`morph deploy … switch`) | [Morph / Nixinate](../12-deployment-and-infra/morph-nixinate.md) | Greenfield flake fleet (prefer Colmena / deploy-rs) |
| Minimal flake `apps` per `nixosConfigurations.*` | **Nixinate** (`nix run .#apps.nixinate.<name>`) | [Morph / Nixinate](../12-deployment-and-infra/morph-nixinate.md) | Need rich multi-host orchestration (PoC / lightly maintained) |
| Peer/inventory fleet; mesh VPN + networking fallback | **Clan** (`clan machines update`) | [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md) | You only want hub→SSH push with no inventory/mesh story |
| Still installing (no NixOS yet); remote wipe + flake | **nixos-anywhere** | [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) | Day-2 config pushes on a running NixOS host |

Bootstrap chooser (ISO / disko / anywhere / non-NixOS): [Install and bootstrap](install-and-bootstrap.md). Deploy authority / SSH keys: [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md).

## Failure callouts

| Symptom / mistake | Fix |
|-------------------|-----|
| Re-running nixos-anywhere for ordinary updates | Day-2: [remote deploy](../09-nixos/operations/remote-deploy.md) or Colmena / deploy-rs—not install-time wipe |
| Deploy “succeeds” then rolls back after intentional net/SSH change | deploy-rs magic-rollback (default on) reconnects to confirm; disable for that change — [deploy-rs](../12-deployment-and-infra/deploy-rs.md) |
| Treating Colmena “hive” as a host mesh / overlay | Colmena is hub→hosts SSH push only; peer fabric → [Clan and mesh](../12-deployment-and-infra/clan-and-mesh.md) |
| Digga / Hive collectors confused with Colmena hive | Different “Hive”—see [Colmena](../12-deployment-and-infra/colmena.md) name-clash note → [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) |

## See also

- [Install and bootstrap](install-and-bootstrap.md)
- [Remote deploy](../09-nixos/operations/remote-deploy.md)
- [Deployment and infra](../12-deployment-and-infra/README.md)
- [Machine mesh](../02-concepts/machine-mesh.md)
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md)
- [deploy-rs fleet (worked example)](../16-configuration-examples/deploy-rs-fleet.md)
- [nixos-anywhere bootstrap (worked example)](../16-configuration-examples/nixos-anywhere-bootstrap.md) — install-time, not day-2

## References

- [Colmena Manual](https://colmena.cli.rs/)
- [serokell/deploy-rs](https://github.com/serokell/deploy-rs)
- [DBCDK/morph](https://github.com/DBCDK/morph)
- [MatthewCroughan/nixinate](https://github.com/MatthewCroughan/nixinate)
- [Clan documentation (26.05)](https://clan.lol/docs/26.05)
- [nixos-anywhere documentation](https://nix-community.github.io/nixos-anywhere/)
