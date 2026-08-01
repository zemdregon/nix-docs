---
status: complete
last-checked: 2026-08
---

# Multi-host config repo

## Overview

This walkthrough shows a **picture-perfect multi-host flake mono-repo**: one `flake.nix`, two `nixosConfigurations`, thin entries under `hosts/`, reusable **role** modules under `modules/`, optional `users/` for Home Manager, `specialArgs` threading flake `inputs`, ciphertext-only `secrets/`, and short deploy and CI hooks. It composes the teaching pages linked in [Domains composed](#domains-composed)—not a second copy of [config repo layout](../07-flakes/workflows/config-repo-layout.md).

Pins such as `nixos-26.05` and `x86_64-linux` are illustrative. Flake workflows need experimental [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md).

## Details

### What you get

One repository that evaluates two independent NixOS systems from the same locked inputs. Each host is a **thin entry module** that imports shared roles plus machine-specific `hardware-configuration.nix`. Deploy tools and CI address hosts by the `nixosConfigurations` key (`.#laptop`, `.#server`)—the folder names under `hosts/` are a convention, not a Nix requirement.

### Domains composed

| Domain | Pages this example uses |
|--------|-------------------------|
| Flake layout and outputs | [Config repo layout](../07-flakes/workflows/config-repo-layout.md), [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md), [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) |
| Module composition | [Imports and profiles](../09-nixos/configuration/imports-and-profiles.md) — static `imports`, role vs host split |
| Operations | [Remote deploy](../09-nixos/operations/remote-deploy.md), [rebuild actions](../09-nixos/operations/rebuild-switch-boot-test.md) |
| Fleet deploy | [Colmena](../12-deployment-and-infra/colmena.md), [deploy-rs](../12-deployment-and-infra/deploy-rs.md) — link when you outgrow one-off SSH rebuilds |
| CI | [CI with Nix](../11-development/ci-with-nix.md), [private flakes and CI](../11-development/private-flakes-and-ci.md) — gate and optional host matrix |
| Secrets and trust | [Secrets strategies](../09-nixos/configuration/secrets-strategies.md), [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md), [inter-machine trust](../14-security-and-trust/inter-machine-trust.md) (SSH deploy keys, cache ACLs) |

### Layout conventions

| Path | Role |
|------|------|
| `flake.nix` | Inputs, `nixosConfigurations.*`, optional exported `nixosModules` |
| `hosts/<name>/default.nix` | Per-machine entry: `imports` roles + `./hardware-configuration.nix`, hostname and host-only overrides |
| `modules/` | Shared **role** modules (`common.nix`, `server.nix`, `desktop.nix`) — capabilities reused across hosts |
| `users/<name>/home.nix` | Optional Home Manager module when dotfiles follow the person, not the box |
| `secrets/` | **Ciphertext only** — age/sops files and key lists; never plaintext tokens or private keys in git |

Rule of thumb from [imports and profiles](../09-nixos/configuration/imports-and-profiles.md): if two machines would copy-paste the same block, promote it to `modules/`; if it is disk, NIC, or bootloader facts, keep it in `hosts/<name>/`.

### Wiring `flake.nix`

Each machine gets its own `nixosConfigurations.<name>`. Pass flake inputs with `specialArgs` so host and role modules can reference `inputs` without importing the flake root:

```nix
nixosConfigurations.laptop = nixpkgs.lib.nixosSystem {
  modules = [ ./hosts/laptop/default.nix ];
  specialArgs = { inherit inputs; };
};
```

Do not pass inputs by reading merged `config` inside `imports`—import lists must be static. See [config repo layout](../07-flakes/workflows/config-repo-layout.md) for `specialArgs` vs `_module.args`.

Align downstream inputs with `inputs.home-manager.inputs.nixpkgs.follows = "nixpkgs"` so `flake.lock` does not pull a second Nixpkgs revision.

### Thin host entries

A host file typically:

1. `imports` shared role modules from `modules/`.
2. `imports` `./hardware-configuration.nix` (generated on install; disk and boot specifics stay here).
3. Sets `networking.hostName` and anything that differs on **this** machine only.

Role modules stay hostname-agnostic so the same `modules/server.nix` composes on any server-shaped host.

### Optional `users/`

Two patterns coexist in one mono-repo:

- **NixOS-embedded** — import `home-manager.nixosModules.home-manager` in the host module list and set `home-manager.users.<user>` to `../../users/<name>/home.nix`. Rebuild with `nixos-rebuild`, not `home-manager switch`.
- **Standalone** — add `homeConfigurations.<user>` in `flake.nix` for non-NixOS machines or a separate dotfiles cadence.

When embedded, set `home-manager.useGlobalPkgs = true` and `home-manager.useUserPackages = true` so user packages share the system `pkgs`.

### Secrets placement

Never commit forge tokens, `access-tokens` values, or age/sops **private** keys beside the flake. Encrypted material lives under `secrets/` (ciphertext files) and/or secret-consuming modules under `modules/`. Host entries only select **which** secrets apply on that machine. Tooling and activation wiring: [secrets strategies](../09-nixos/configuration/secrets-strategies.md), [agenix / sops-nix](../12-deployment-and-infra/agenix-sops-nix.md).

### Deploy hooks

The stable address for every host is the flake output name, regardless of folder layout.

**Single host, SSH from your laptop** — same CLI as a local rebuild, with remote activation flags documented on [remote deploy](../09-nixos/operations/remote-deploy.md):

```bash
nixos-rebuild switch --flake .#server --target-host user@server --elevate=sudo
```

Optional `--build-host` runs the build on a remote builder; `--no-reexec` helps when the deployer's architecture differs from the target. Prefer current `nixos-rebuild-ng` flag names from `man nixos-rebuild` over deprecated aliases.

**Many hosts** — fleet tools read your flake and push closures over SSH:

- [Colmena](../12-deployment-and-infra/colmena.md) — hive of nodes (`colmena apply`, tags, parallel apply); flake surface varies by Colmena version (`outputs.colmena` vs `colmenaHive`).
- [deploy-rs](../12-deployment-and-infra/deploy-rs.md) — `deploy.nodes` / profiles in the flake; `deploy` CLI with magic-rollback.

Both are hub → hosts orchestration, not a peer mesh. SSH trust and deploy keys: [inter-machine trust](../14-security-and-trust/inter-machine-trust.md).

### CI hooks

Gate every PR with evaluation of the flake:

```bash
nix flake check
```

That builds each `nixosConfigurations.<name>.config.system.build.toplevel` (and any `checks` you declare). For org fleets where a full check is too heavy, add a **host matrix**—parallel CI jobs that `nix build .#nixosConfigurations.<host>.config.system.build.toplevel` for selected hosts, optionally scoped by path filters. Runner setup, caches, and private inputs: [CI with Nix](../11-development/ci-with-nix.md), [private flakes and CI](../11-development/private-flakes-and-ci.md), [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md).

Illustrative matrix fragment (placeholders only; not run in this vault):

```yaml
# .github/workflows/nixos-hosts.yml (sketch)
strategy:
  matrix:
    host: [laptop, server]
steps:
  - run: nix build .#nixosConfigurations.${{ matrix.host }}.config.system.build.toplevel
```

### Failure modes

| Symptom | Likely cause |
|---------|----------------|
| Wrong system activated on remote host | Missing or wrong `--flake .#<name>`; remote deploy evaluates **your** flake, not the target's `/etc/nixos` — see [remote deploy](../09-nixos/operations/remote-deploy.md) |
| `imports` error or infinite recursion | Conditional `imports` from `config`; use static modules and `mkIf` on options instead — [imports and profiles](../09-nixos/configuration/imports-and-profiles.md) |
| HM and NixOS disagree on package versions | Embedded Home Manager without `useGlobalPkgs` |
| CI rebuilds every host on every doc edit | No path filters or host groups; document which `modules/` changes affect which hosts |
| Secret leaked in git history | Plaintext under `secrets/` or in `flake.nix`; use ciphertext and local/`nix.conf` auth only |

## Examples

### Directory tree

```
.
├── flake.nix
├── flake.lock
├── hosts/
│   ├── laptop/
│   │   ├── default.nix
│   │   └── hardware-configuration.nix
│   └── server/
│       ├── default.nix
│       └── hardware-configuration.nix
├── modules/
│   ├── common.nix          # baseline + overlays
│   ├── desktop.nix         # role: graphical workstation
│   └── server.nix          # role: headless services
├── users/
│   └── alice/
│       └── home.nix        # optional HM module
└── secrets/                # ciphertext only; optional
    └── …
```

### `flake.nix`

Two `nixosConfigurations`, shared inputs, exported role module, optional standalone Home Manager:

```nix
{
  description = "Multi-host NixOS mono-repo";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager.url = "github:nix-community/home-manager/release-26.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, home-manager, ... }@inputs: {
    nixosConfigurations.laptop = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [ ./hosts/laptop/default.nix ];
    };

    nixosConfigurations.server = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      modules = [ ./hosts/server/default.nix ];
    };

    nixosModules.desktop = ./modules/desktop.nix;
    nixosModules.server = ./modules/server.nix;

    homeConfigurations.alice = home-manager.lib.homeManagerConfiguration {
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      extraSpecialArgs = { inherit inputs; };
      modules = [ ./users/alice/home.nix ];
    };
  };
}
```

### Host entry (`hosts/server/default.nix`)

Thin composition: roles + hardware + hostname; no duplicated service policy:

```nix
{ inputs, ... }: {
  imports = [
    ../../modules/common.nix
    ../../modules/server.nix
    ./hardware-configuration.nix
  ];

  networking.hostName = "server";
}
```

Laptop with desktop role and embedded Home Manager:

```nix
# hosts/laptop/default.nix
{ inputs, ... }: {
  imports = [
    ../../modules/common.nix
    inputs.self.nixosModules.desktop
    ./hardware-configuration.nix
    inputs.home-manager.nixosModules.home-manager
  ];

  networking.hostName = "laptop";

  home-manager.useGlobalPkgs = true;
  home-manager.useUserPackages = true;
  home-manager.users.alice = ../../users/alice/home.nix;
}
```

### Role module (`modules/server.nix`)

Reusable capability—imported unchanged on every server-shaped host:

```nix
{ modulesPath, ... }: {
  imports = [ (modulesPath + "/profiles/headless.nix") ];

  services.openssh.enable = true;

  # Shared service policy for all hosts that import this role …
}
```

### Activate / verify / deploy

```bash
nix flake lock
nix flake check

# Build without switching
nix build .#nixosConfigurations.laptop.config.system.build.toplevel
nix build .#nixosConfigurations.server.config.system.build.toplevel

# Local switch (on each machine)
sudo nixos-rebuild switch --flake .#laptop
sudo nixos-rebuild switch --flake .#server

# Remote switch (from deployer)
nixos-rebuild switch --flake .#server --target-host user@server --elevate=sudo

# Fleet (when inventory grows) — see linked pages for version-specific flake output keys
# colmena apply
# deploy .
```

Match `networking.hostName`, the `nixosConfigurations` key, and the `#` suffix. On a machine whose hostname equals the key, `nixos-rebuild switch --flake .` omits `#`.

## References

- [nix.dev — Flakes](https://nix.dev/concepts/flakes) — inputs, outputs, and `nixosConfigurations`
- [NixOS manual (stable)](https://nixos.org/manual/nixos/stable/) — modularity, changing the configuration, remote rebuild
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — validates `nixosConfigurations.*.config.system.build.toplevel`
- [Colmena (GitHub)](https://github.com/nix-community/colmena) — fleet hive deploy tool (canonical upstream; `zhaofengli/colmena` redirects)

## See also

- [Config repo layout](../07-flakes/workflows/config-repo-layout.md) — folder conventions and org-scale topics
- [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md) — `nixosSystem` wiring and rebuild
- [Imports and profiles](../09-nixos/configuration/imports-and-profiles.md) — static `imports` and splitting configuration
- [Remote deploy](../09-nixos/operations/remote-deploy.md) — `--target-host`, `--build-host`, elevation
- [Colmena](../12-deployment-and-infra/colmena.md) — multi-host hive apply
- [deploy-rs](../12-deployment-and-infra/deploy-rs.md) — flake `deploy.nodes` profiles
- [deploy-rs fleet (worked example)](deploy-rs-fleet.md) — full `deploy.nodes` + `deployChecks` wiring
- [CI with Nix](../11-development/ci-with-nix.md) — runner install, caches, `nix flake check`
- [Flake CI with GitHub Actions (worked example)](flake-ci-github-actions.md) — host-matrix CI for this layout
- [Private flakes and CI](../11-development/private-flakes-and-ci.md) — private inputs on CI runners
- [Secrets strategies](../09-nixos/configuration/secrets-strategies.md) — how secrets enter the module graph
- [Minimal flake NixOS host](minimal-flake-nixos-host.md) — single-host version of this walkthrough
- [NixOS with Home Manager](nixos-with-home-manager.md) — embedded HM in one rebuild
