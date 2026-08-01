---
status: complete
last-checked: 2026-07
---

# Colmena

## Overview

**Colmena** is a simple, **stateless** [NixOS](../09-nixos/README.md) fleet deploy tool (Rust). Canonical upstream: [nix-community/colmena](https://github.com/nix-community/colmena) (docs at [colmena.cli.rs](https://colmena.cli.rs/); `zhaofengli/colmena` redirects). It is a thin wrapper over Nix (`nix-instantiate` / `nix eval`, `nix-copy-closure`, and related): evaluate a multi-host **hive**, build system closures, copy them over **SSH**, and activate.

Topology is **hub → hosts**: the machine running `colmena` pushes to each target. It is **not** a host-to-host network mesh, overlay, or cluster fabric—only deploy orchestration from a deployer to SSH-reachable NixOS machines (same spirit as remote [`nixos-rebuild`](../09-nixos/operations/remote-deploy.md), for many nodes).

Configs live in classic `hive.nix` or a flake output. Parallel apply, node tags, local apply, and build-on-target are supported. Available in Nixpkgs from 21.11 (`nix-shell -p colmena` / `nix shell nixpkgs#colmena`; nixpkgs packages **0.4.0** as of mid-2026). Flake surface is high-churn: **0.4 stable** vs **main / toward 0.5**—see the table under Hive layout before copying flake examples.

**Name clash:** Colmena’s “hive” is an attrset of deployable NixOS nodes. It is unrelated to [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) (divnix flake layout / std collectors)—even when Hive collectors feed Colmena. Hive membership is deploy catalog only—not [machine mesh](../02-concepts/machine-mesh.md) interconnect.

Peers in this domain: [deploy-rs](deploy-rs.md), [Morph / Nixinate](morph-nixinate.md).

## Details

### Hub → hosts (not a mesh)

1. You run Colmena on a **deployer** (laptop, CI, bastion) that can evaluate the hive and reach targets over SSH with key auth (interactive login is not supported; optional `SSH_CONFIG_FILE`).
2. Colmena builds (locally, via Nix builders, or on the target), copies closures, and activates on each selected host.
3. Hosts do not form a Colmena control plane among themselves. Tags and `--on` only filter which nodes that hub deploys to.

Colmena does not provision VMs/cloud lifecycle (unlike stateful NixOps backends); targets are assumed to exist.

### Hive layout

A hive is an attribute set of NixOS nodes plus optional `meta` and `defaults`:

- **`meta`** — shared settings: `nixpkgs` (path, lambda, or attrset), per-node `nodeNixpkgs`, optional `machinesFile` for Nix distributed builders.
- **`defaults`** — a module imported by every node.
- **Node attributes** — each key is a host; by default Colmena SSHes to that name. Override with `deployment.targetHost`, `deployment.targetPort`, `deployment.targetUser`. Modules may take `name` and `nodes` to cross-reference other hosts’ evaluated config.

Classic: `hive.nix` in the working directory. Flakes (version-stamp):

| Colmena | Flake surface |
|---------|----------------|
| **0.4 stable** (nixpkgs `colmena`) | `outputs.colmena = { meta = …; host = …; }` — see [stable flakes tutorial](https://colmena.cli.rs/stable/tutorial/flakes.html) |
| **Unstable / main** (toward 0.5) | `outputs.colmenaHive = colmena.lib.makeHive { … }` via `nix eval`; migrate with `makeHive` wrapping an old `colmena` attrset. Legacy: `--legacy-flake-eval` (uses `colmena` output; not pure on Nix 2.21+) — see [unstable flakes tutorial](https://colmena.cli.rs/unstable/tutorial/flakes.html) |

Node bodies are ordinary NixOS modules—same composition habits as [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md), but Colmena owns `deployment.*` rather than `nixos-rebuild --target-host`.

### Apply, tags, and local deploy

- **`colmena build`** — evaluate and build selected nodes without activating.
- **`colmena apply`** — build, push, activate (default goal comparable to switch-style activation). Evaluation/build/deploy can overlap; **`--limit`** caps concurrent host activations (default 10).
- **Tags** — `deployment.tags = [ "web" … ]`, select with **`--on`**: comma-separated names or `@tag` filters, globs quoted — e.g. `colmena apply --on @web`, `colmena apply --on '@infra-*'`.
- **`colmena apply-local`** — activate on the machine running Colmena when the node attribute name matches `hostname`, `deployment.allowLocalDeployment = true`, and the host is NixOS. **`--sudo`** elevates when not root. Set `deployment.targetHost = null` to skip the node on remote `apply`.

### Where builds run

| Approach | Behavior |
|----------|----------|
| Default | Build on the Colmena host (or Nix remote builders), then copy closures to targets. |
| `deployment.buildOnTarget = true` | Evaluate locally, copy derivations to the target, build there. CLI: `--build-on-target` / `--no-build-on-target`. Results are not shared back across nodes. |
| Nix distributed builds | Builders globally or via `meta.machinesFile`; Nix forwards builds and copies results back. |

## Examples

Minimal classic hive (illustrative; fill boot/filesystems for real machines):

```nix
# hive.nix
{
  meta = {
    nixpkgs = <nixpkgs>;
  };

  defaults = { pkgs, ... }: {
    environment.systemPackages = with pkgs; [ vim ];
  };

  web-1 = {
    deployment = {
      targetHost = "web-1.example.com";
      tags = [ "web" ];
    };
    # ... NixOS modules ...
  };

  laptop = { name, ... }: {
    networking.hostName = name;
    deployment = {
      allowLocalDeployment = true;
      targetHost = null; # skip on remote apply
    };
    # ... NixOS modules ...
  };
}
```

Flake sketch for **unstable** Colmena (`colmenaHive`; require Colmena as an input):

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    colmena.url = "github:nix-community/colmena";
  };
  outputs = { nixpkgs, colmena, ... }: {
    colmenaHive = colmena.lib.makeHive {
      meta = {
        nixpkgs = import nixpkgs {
          system = "x86_64-linux";
          overlays = [];
        };
      };
      host-a = {
        deployment.targetHost = "host-a.example.com";
        # ... NixOS modules ...
      };
    };
  };
}
```

With **nixpkgs Colmena 0.4**, use `outputs.colmena = { meta = …; host-a = …; };` instead (no `makeHive` / Colmena flake input required for evaluation).

Typical commands (from the hive/flake directory):

```bash
nix shell nixpkgs#colmena   # 0.4.x from nixpkgs
# or: nix shell github:nix-community/colmena   # main / unstable docs

colmena build
colmena apply
colmena apply --on @web
colmena apply-local --sudo   # local node only
```

## See also

- [Machine mesh](../02-concepts/machine-mesh.md) — interconnect mental model (hub deploy vs peer)
- [Clan and mesh](clan-and-mesh.md) — peer/no-central-controller contrast to Colmena hub→hosts
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — single-host `nixos-rebuild --target-host` vs fleet hub push
- [Inter-machine trust](../14-security-and-trust/inter-machine-trust.md) — deploy trust axis among six axes
- [deploy-rs](deploy-rs.md) — flake-oriented multi-host deploy
- [Digga / Hive](../13-implementations/community-frameworks/digga-hive.md) — different “Hive”; not Colmena

## References

- [Colmena Manual](https://colmena.cli.rs/) ([stable 0.4](https://colmena.cli.rs/stable/) · [unstable](https://colmena.cli.rs/unstable/))
- [GitHub — nix-community/colmena](https://github.com/nix-community/colmena)
- [Tutorial (classic hive)](https://colmena.cli.rs/stable/tutorial/index.html)
- [Tutorial with Flakes (stable 0.4 / `colmena` output)](https://colmena.cli.rs/stable/tutorial/flakes.html)
- [Tutorial with Flakes (unstable / `colmenaHive`)](https://colmena.cli.rs/unstable/tutorial/flakes.html)
- [Local deployment (`apply-local`)](https://colmena.cli.rs/stable/features/apply-local.html)
- [Node tagging](https://colmena.cli.rs/stable/features/tags.html)
- [Remote builds](https://colmena.cli.rs/stable/features/remote-builds.html)
