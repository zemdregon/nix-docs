---
status: complete
last-checked: 2026-08
---

# deploy-rs fleet

## Overview

This walkthrough adds **[deploy-rs](../12-deployment-and-infra/deploy-rs.md)** fleet wiring on top of a multi-host flake that already defines `nixosConfigurations`. It is the day-2 push path: build profile closures on the hub, copy over SSH, activate on each target. It assumes the repo layout from [multi-host config repo](multi-host-config-repo.md)—`hosts/`, `modules/`, thin entries—not a second lesson on folder conventions.

deploy-rs is **hub → hosts** orchestration (like [Colmena](../12-deployment-and-infra/colmena.md)), not a peer mesh. Its distinctive value here is **multi-profile** deploy (system + optional Home Manager or custom profiles per node) and **magic-rollback** after activation. For tool choice, see [fleet deploy (cheatsheet)](../cheatsheets/fleet-deploy.md).

Pins such as `nixos-26.05` and `x86_64-linux` are illustrative. Flake workflows need experimental [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md).

## Details

### Domains composed

| Domain | Pages this example uses |
|--------|-------------------------|
| Multi-host flake shape | [Multi-host config repo](multi-host-config-repo.md), [config repo layout](../07-flakes/workflows/config-repo-layout.md), [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md) |
| deploy-rs surface | [deploy-rs](../12-deployment-and-infra/deploy-rs.md) — `deploy.nodes`, activate helpers, `deployChecks`, magic-rollback |
| Alternatives | [Remote deploy](../09-nixos/operations/remote-deploy.md) (1–few hosts), [Colmena](../12-deployment-and-infra/colmena.md) (tags/parallel hive), [fleet deploy](../cheatsheets/fleet-deploy.md) (chooser) |
| Trust | [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — SSH keys, deploy user, sudo |
| Install-time (not this page) | [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) · [nixos-anywhere bootstrap](nixos-anywhere-bootstrap.md) — wipe/install when the target is not NixOS yet |
| CI gates (optional) | [Flake CI with GitHub Actions](flake-ci-github-actions.md) — `nix flake check` / host matrix before deploy |

### Prerequisites

**Targets must already run NixOS** (or nix-darwin for darwin profiles) with SSH reachable from the deployer. First install is out of band: use [nixos-anywhere bootstrap](nixos-anywhere-bootstrap.md) / [nixos-anywhere](../09-nixos/installation/nixos-anywhere.md) or a local install, then adopt this flake and `deploy.nodes`. Do not re-run install-time tools for ordinary config updates—see [fleet deploy](../cheatsheets/fleet-deploy.md).

Start from a working [multi-host config repo](multi-host-config-repo.md): `nixosConfigurations.laptop` and `nixosConfigurations.server` (or your names), host modules under `hosts/`, shared roles under `modules/`. The only structural addition for deploy-rs is an `inputs.deploy-rs` pin and a `deploy.nodes` attrset that points each node’s profiles at the right flake outputs.

### What changes in `flake.nix`

1. **Input** — `deploy-rs.url = "github:serokell/deploy-rs";`
2. **`deploy.nodes.<name>`** — mirrors a host key; each node needs `hostname` (SSH target) and `profiles.<id>`.
3. **Profile `path`** — must be a derivation with a `deploy-rs-activate` script. Use helpers from `deploy-rs.lib.<system>.activate`:
   - `nixos` — NixOS system profile (`switch-to-configuration`)
   - `home-manager` — Home Manager generation (standalone `homeConfigurations`, not embedded NixOS HM)
   - `darwin`, `custom`, `profile`, `noop` — see [deploy-rs](../12-deployment-and-infra/deploy-rs.md)
4. **`checks`** — wire `deploy-rs.lib.<system>.deployChecks self.deploy` so `nix flake check` validates the deploy schema.

Each profile sets `user` (who activates; may use sudo when different from `sshUser`). Generic options (`sshUser`, `sshOpts`, `fastConnection`, `remoteBuild`, magic-rollback flags) may live on `deploy`, a node, or a profile; priority is **profile > node > deploy**.

### Multi-profile and rollback

A node can expose several profiles—for example `profiles.system` plus `profiles.home` on a laptop. Optional `profilesOrder` on the node sets deploy order when you run without selecting a single profile; **unlisted profiles still deploy afterward** (arbitrary order). List dependencies explicitly (typically **system before home-manager**), or deploy one profile at a time (`deploy .#laptop.home`).

With `magicRollback` default `true`, deploy-rs reconnects after activation; if the host is unreachable within `confirmTimeout` (default 30s), the target rolls back. `autoRollback` (default `true`) re-activates the previous generation if activation fails. `activationTimeout` defaults to 240s. Disable magic-rollback (flake option or CLI; see `deploy --help`) only when you intentionally change SSH port, bind address, firewall, or IP mid-deploy.

### When to use something else

| Need | Prefer |
|------|--------|
| One or two hosts, no fleet schema | [Remote deploy](../09-nixos/operations/remote-deploy.md) — `nixos-rebuild switch --flake .#host --target-host …` |
| NixOS-only hive, tags, parallel apply | [Colmena](../12-deployment-and-infra/colmena.md) |
| Peer mesh / inventory control plane | Clan — [fleet deploy](../cheatsheets/fleet-deploy.md) |
| Multi-profile + magic-rollback from one flake | deploy-rs (this walkthrough) |

### Failure modes

| Symptom | Likely cause | What to check |
|---------|--------------|---------------|
| Deploy “succeeds” then rolls back after net/SSH change | Magic-rollback false positive | Default `magicRollback = true` while changing SSH port, IP, or firewall; disable for that deploy ([deploy-rs](../12-deployment-and-infra/deploy-rs.md)) |
| Wrong generation or activation error | Wrong activate helper | `activate.nixos` only for NixOS `nixosConfigurations`; `activate.home-manager` only for `homeConfigurations` paths |
| Home profile runs before system / broken HM | `profilesOrder` | Set `profilesOrder = [ "system" "home" ];` on the node, or deploy one profile: `deploy .#laptop.home` |
| Permission denied or sudo loop | `sshUser` vs `user` | `sshUser` is the SSH login; `user` is who runs activation (sudo when ≠ `sshUser`); [inter-machine trust](../14-security-and-trust/inter-machine-trust.md) |
| `nix flake check` fails on deploy | Schema mismatch | Required `hostname` and per-profile `path`; fix attrset or read `deployChecks` errors ([interface.json](https://github.com/serokell/deploy-rs/blob/master/interface.json)) |
| SSH fails before copy | Auth or reachability | `hostname`, `sshUser`, `sshOpts`; key login for deploy user |

## Examples

Assume the same tree as [multi-host config repo](multi-host-config-repo.md): `hosts/laptop`, `hosts/server`, `modules/`, optional `users/alice/home.nix`.

### `flake.nix` — configurations + deploy.nodes + checks

```nix
{
  description = "Multi-host NixOS mono-repo with deploy-rs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager.url = "github:nix-community/home-manager/release-26.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
    deploy-rs.url = "github:serokell/deploy-rs";
  };

  outputs = { self, nixpkgs, home-manager, deploy-rs, ... }@inputs: {
    nixosConfigurations.laptop = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit inputs; };
      modules = [ ./hosts/laptop/default.nix ];
    };

    nixosConfigurations.server = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit inputs; };
      modules = [ ./hosts/server/default.nix ];
    };

    homeConfigurations.alice = home-manager.lib.homeManagerConfiguration {
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      extraSpecialArgs = { inherit inputs; };
      modules = [ ./users/alice/home.nix ];
    };

    deploy.nodes.laptop = {
      hostname = "laptop.example.com";
      profilesOrder = [ "system" "home" ];
      profiles.system = {
        user = "root";
        path = deploy-rs.lib.x86_64-linux.activate.nixos self.nixosConfigurations.laptop;
      };
      profiles.home = {
        user = "alice";
        path = deploy-rs.lib.x86_64-linux.activate.home-manager self.homeConfigurations.alice;
      };
    };

    deploy.nodes.server = {
      hostname = "server.example.com";
      profiles.system = {
        user = "root";
        path = deploy-rs.lib.x86_64-linux.activate.nixos self.nixosConfigurations.server;
      };
    };

    checks = builtins.mapAttrs
      (system: deployLib: deployLib.deployChecks self.deploy)
      deploy-rs.lib;
  };
}
```

Host modules stay unchanged from [multi-host config repo](multi-host-config-repo.md). These snippets assume that tree (illustrative; not a runnable fixture in this vault). Embedded Home Manager inside `nixosConfigurations` is a separate pattern ([NixOS with Home Manager](nixos-with-home-manager.md)); deploy-rs’s `activate.home-manager` helper targets standalone [`homeConfigurations`](../07-flakes/workflows/home-configurations.md) as shown above—not the embedded NixOS HM module.

Optional `sshUser` on a node (defaults to the local username if unset anywhere):

```nix
deploy.nodes.server = {
  hostname = "server.example.com";
  sshUser = "deploy";
  profiles.system = {
    user = "root";
    path = deploy-rs.lib.x86_64-linux.activate.nixos self.nixosConfigurations.server;
  };
};
```

### Check and deploy

```bash
nix flake lock
nix flake check                    # nixosConfigurations toplevels + deployChecks

# Full fleet (all nodes, all profiles)
deploy .
# or: nix run github:serokell/deploy-rs -- .

# One node or one profile
deploy .#server
deploy .#server.system
deploy .#laptop.home

# Build without deploying
nix build .#nixosConfigurations.server.config.system.build.toplevel
```

Match `deploy.nodes.<name>` keys to `nixosConfigurations` names and DNS/`hostname` to what SSH resolves. SSH trust and deploy keys: [inter-machine trust](../14-security-and-trust/inter-machine-trust.md).

## References

- [serokell/deploy-rs](https://github.com/serokell/deploy-rs) — README, magic-rollback, CLI, option defaults
- [deploy-rs examples](https://github.com/serokell/deploy-rs/tree/master/examples) — full working flake expressions
- [interface.json](https://github.com/serokell/deploy-rs/blob/master/interface.json) — schema for `deployChecks`

## See also

- [Multi-host config repo](multi-host-config-repo.md) — hosts/modules layout this walkthrough extends
- [deploy-rs](../12-deployment-and-infra/deploy-rs.md) — activate helpers, options hierarchy, failure modes
- [Fleet deploy (cheatsheet)](../cheatsheets/fleet-deploy.md) — hub vs bare rebuild vs Clan
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — single-host `nixos-rebuild --target-host`
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — SSH deploy authority
- [nixos-anywhere bootstrap](nixos-anywhere-bootstrap.md) — install-time wipe-and-install (not day-2)
