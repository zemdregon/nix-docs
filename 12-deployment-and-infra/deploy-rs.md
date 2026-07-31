---
status: complete
---

# deploy-rs

## Overview

[deploy-rs](https://github.com/serokell/deploy-rs) (Serokell) is a multi-profile Nix flake deploy tool. You declare `deploy.nodes` in the flake; the `deploy` CLI builds profile closures, copies them over SSH, and runs activation on the target.

Compared to other fleet tools here: [Colmena](colmena.md) is hive-oriented; [Morph / Nixinate](morph-nixinate.md) are older or thinner wrappers. Like Colmena, deploy-rs is **hub → hosts** SSH push—not a peer mesh control plane. Its distinctive pieces are **multi-profile** deploys (not only root `system`) and **magic-rollback** after activation.

**Maturity:** flake-first community tool; option defaults and CLI flags evolve with the README / `deploy --help` (no Colmena-style stable/unstable doc split). Prefer the upstream README and `interface.json` over stale blog snippets when wiring nodes.

For plain `nixos-rebuild --target-host`, see [remote deploy](../09-nixos/operations/remote-deploy.md). Wiring systems into flakes: [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md). Also supports [nix-darwin](../10-home-and-user/nix-darwin.md) and home-manager profiles via activate helpers.

## Details

### Flake surface

- Top-level `deploy.nodes.<name>` — one machine; required `hostname`, plus `profiles`.
- Optional `profilesOrder` on a node — deploy order when you run without selecting a single profile; unlisted profiles still deploy afterward.
- Each profile needs a `path`: a derivation with a `deploy-rs-activate` script. Optional `profilePath` overrides where the Nix profile is installed on the target.
- Helpers under `deploy-rs.lib.<system>.activate`:
  - `nixos` — NixOS (`switch-to-configuration`)
  - `darwin` — nix-darwin
  - `home-manager` — home-manager generation
  - `custom` — wrap any derivation with a custom activation command
  - `profile` — install into the user’s nix3 `nix profile`
  - `noop` — copy the closure with no activation
- `deploy-rs.lib.<system>.deployChecks` — feed into `checks` so `nix flake check` validates the deploy attrset (JSON schema in upstream `interface.json`).

CLI: `deploy [flake]` deploys all profiles on all nodes in that flake; `deploy .#node` or `deploy .#node.profile` narrows the target. Also `nix run github:serokell/deploy-rs -- …`. Extra args after `--` go to Nix (e.g. `--impure`). Multi-flake / subset: `deploy --targets …`.

### SSH activate and users

Generic options include `sshUser` (who SSH connects as; defaults to your local username if unset) and `user` (who the profile activates as; may use sudo when different from `sshUser`). Optional `sshOpts`, `sudo` / `interactiveSudo`, `fastConnection` (push full closure instead of remote substitute), and `remoteBuild` (build on the target).

### Magic rollback

With `magicRollback` enabled (default `true`), deploy-rs reconnects after activation to confirm the machine is still reachable and rolls back on the target if confirmation fails. Disable it (config or CLI) only when you intentionally change connectivity (SSH port, IP, etc.). Related: `autoRollback` (default `true`) re-activates the previous profile if activation itself fails. Timeouts: `activationTimeout` (default 240s), `confirmTimeout` (default 30s).

### Options hierarchy

Generic options may appear on `deploy`, a node, or a profile, with priority **profile > node > deploy**. CLI flags can override flake values; see `deploy --help`.

## Examples

Minimal flake deploying one NixOS system profile (adapted from upstream README):

```nix
{
  inputs.deploy-rs.url = "github:serokell/deploy-rs";

  outputs = { self, nixpkgs, deploy-rs }: {
    nixosConfigurations.web = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [ ./web/configuration.nix ];
    };

    deploy.nodes.web = {
      hostname = "web.example.com";
      profiles.system = {
        user = "root";
        path = deploy-rs.lib.x86_64-linux.activate.nixos self.nixosConfigurations.web;
      };
    };

    checks = builtins.mapAttrs
      (system: deployLib: deployLib.deployChecks self.deploy)
      deploy-rs.lib;
  };
}
```

Then: `nix run github:serokell/deploy-rs -- .#web` (or install `deploy` and run `deploy .#web`).

## References

- [serokell/deploy-rs](https://github.com/serokell/deploy-rs) — README (API, magic-rollback, CLI)
- [examples/](https://github.com/serokell/deploy-rs/tree/master/examples) — full working flake expressions
- [interface.json](https://github.com/serokell/deploy-rs/blob/master/interface.json) — schema used by `deployChecks`

## See also

- [Machine mesh](../02-concepts/machine-mesh.md) — interconnect / hub vs peer
- [Clan and mesh](clan-and-mesh.md) — peer-oriented contrast to hub deploy-rs
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — single-host rebuild vs multi-profile hub push
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — deploy trust axis among six axes
- [Colmena](colmena.md) — hive-oriented hub deploy peer
- [nixosConfigurations (flakes)](../07-flakes/workflows/nixos-configurations.md) — systems wired for profiles
