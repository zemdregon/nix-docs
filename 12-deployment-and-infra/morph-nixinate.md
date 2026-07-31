---
status: complete
---

# Morph / Nixinate

## Overview

**Morph** ([DBCDK/morph](https://github.com/DBCDK/morph)) and **nixinate** ([MatthewCroughan/nixinate](https://github.com/MatthewCroughan/nixinate)) are lighter NixOS remote-deploy options beside [Colmena](colmena.md) and [deploy-rs](deploy-rs.md). Morph is a Go CLI that evaluates a multi-host Nix deployment file, then builds, copies, and activates over SSH (optional health checks and scp secrets). Nixinate is a flake library that turns each `nixosConfigurations.*` into a `nix run` deploy app.

Neither replaces bare [remote `nixos-rebuild`](../09-nixos/operations/remote-deploy.md). Both follow the same **hub→hosts** SSH deploy pattern as Colmena and deploy-rs—not peer mesh fleets. Prefer Colmena/deploy-rs for a currently popular multi-host flake workflow; use these when an existing Morph fleet or a minimal flake-app deploy fits better.

## Details

### Morph

Canonical repo is **[DBCDK/morph](https://github.com/DBCDK/morph)** (Danish Broadcasting Corporation). Pointers to `NixOS/morph`, `nix-community/morph`, or `DBSynchro/morph` are wrong or dead. Listed in [nix-community/awesome-nix](https://github.com/nix-community/awesome-nix) under Deployment Tools; ownership stays with DBCDK.

Morph wraps `nix-build` / `nix copy` / `nix-env` / SSH / `switch-to-configuration` / `scp`. It does **not** provision machines—only update existing NixOS hosts. Deployment is a Nix file with a `network` attrset and named host modules (NixOps-inspired), not a flake-first `deploy` schema.

CLI (from upstream `--help`): `build`, `push`, `deploy`, `check-health`, `upload-secrets`, `exec`. `morph deploy` needs a switch action: `dry-activate`, `test`, `switch`, or `boot` (same names as `nixos-rebuild`). Host selection: `--on` globs, `--limit` / `--skip` / `--every`, and `--tagged` against `deployment.tags`. Features called out upstream: multi-host deploy, HTTP and command health checks, scp secrets kept out of the store, optional `deployment.preDeployChecks` (marked experimental).

**Status (as of 2026-07):** not archived. Last push 2026-07-20 was dependency/CI maintenance (e.g. Go crypto bumps, `flake.lock`). Latest release tag is `v1.8.0` (2024-10-23)—tagged releases are infrequent. Upstream recommends pinning a tag or git revision; the README notes the CLI may change and discusses a possible rewrite. Flakes appear mainly for building Morph itself; day-to-day configs remain classic deployment expressions.

### Nixinate

Nixinate generates a deployment script per configured `nixosConfiguration` and exposes it under flake `apps` so you run `nix run .#apps.nixinate.<name>`. Wire it with `apps = nixinate.nixinate.<system> self;` and per-host `_module.args.nixinate`:

| Arg | Role (per upstream README) |
|-----|----------------------------|
| `host` | SSH hostname or IP |
| `sshUser` | SSH user |
| `buildOn` | `"local"` or `"remote"` |
| `substituteOnTarget` | Prefer substitutes on the target when building locally |
| `hermetic` | Copy Nix to the remote instead of using the remote’s Nix |

It is flake-native but thinner than Colmena/deploy-rs: no separate deploy schema or rich multi-host orchestration—each machine is one `nix run` app. Upstream calls it a **proof of concept**.

**Status (as of 2026-07):** not archived, but quieter than Morph. Last push 2025-03-23 (`NIX_SSHOPTS` on SSH invocations). No GitHub release tags. Pin the flake input; treat it as lightly maintained PoC rather than a primary fleet tool.

### Compared to Colmena / deploy-rs

| Tool | Shape | Flake role |
|------|--------|------------|
| Morph | Standalone Go binary + Nix deployment file | Optional for the tool; configs historically non-flake |
| Nixinate | Flake `apps` over existing `nixosConfigurations` | Required |
| [Colmena](colmena.md) / [deploy-rs](deploy-rs.md) | Dedicated multi-host deploy tools | Primary workflow for many new fleets |

## Examples

Morph (illustrative; see upstream `examples/simple.nix` for a fuller network):

```nix
# deployment.nix — sketch; set real targetHost / disks before deploy
{
  network = {
    pkgs = import <nixpkgs> { };
    description = "example";
  };

  "web01" = { ... }: {
    deployment.tags = [ "web" ];
    # ... normal NixOS module options ...
  };
}
```

```bash
morph build deployment.nix
morph deploy deployment.nix switch
# morph deploy deployment.nix switch --on 'web*' --upload-secrets
```

Nixinate (minimal sketch aligned with upstream README; pin nixpkgs/nixinate yourself):

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixinate.url = "github:matthewcroughan/nixinate";
  };

  outputs = { self, nixpkgs, nixinate }: {
    apps = nixinate.nixinate.x86_64-linux self;
    nixosConfigurations.myMachine = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./my-configuration.nix
        {
          _module.args.nixinate = {
            host = "example.invalid";
            sshUser = "deploy";
            buildOn = "remote"; # or "local"
            substituteOnTarget = true;
            hermetic = false;
          };
        }
      ];
    };
  };
}
```

```bash
nix run .#apps.nixinate.myMachine
```

## References

- [DBCDK/morph](https://github.com/DBCDK/morph) — Morph source, README, `examples/`, health checks and secrets
- [MatthewCroughan/nixinate](https://github.com/MatthewCroughan/nixinate) — nixinate flake apps and `_module.args.nixinate`
- [NixOS Wiki — Morph](https://wiki.nixos.org/wiki/Morph) — short community summary (prefer the GitHub README for commands)
- [nix-community/awesome-nix — Deployment Tools](https://github.com/nix-community/awesome-nix) — lists Morph and Nixinate among deploy tools

## See also

- [Colmena](colmena.md) — multi-host NixOS deploy tool
- [deploy-rs](deploy-rs.md) — flake-oriented multi-profile deploy
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — `nixos-rebuild --target-host` / `--build-host`
- [Machine mesh](../02-concepts/machine-mesh.md) — hub vs peer fleet topology
- [Clan and mesh](clan-and-mesh.md) — peer tooling contrast to Morph/Nixinate hub patterns
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — SSH deploy authority and related trust axes
