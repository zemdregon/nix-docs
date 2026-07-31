---
status: complete
---

# Hydra

## Overview

[Hydra](https://github.com/NixOS/hydra) is the Nix-based continuous integration and release system. It polls project inputs, **evaluates** Nix expressions into job graphs, and **builds** the resulting derivations on a farm of builders. Successful builds become substitutable store paths—Hydra is how [hydra.nixos.org](https://hydra.nixos.org/) produces the binary packages behind Nixpkgs channels.

Hydra organizes work as **projects**, **jobsets**, **evaluations**, and **builds**. Flake-based projects typically expose a top-level [`hydraJobs`](../07-flakes/workflows/checks-and-hydraJobs.md) output that Hydra imports as the job tree. Self-hosting Hydra is the heavyweight path when you need a large, scheduled job graph and a project [binary cache](binary-cache-hosting.md); most application repos are better served by lightweight forge CI such as [GitHub Actions with Nix](../11-development/ci-with-nix.md).

## Details

### Model

| Term | Role |
|------|------|
| **Project** | Grouping of related jobsets (often one git repo, e.g. nixpkgs). |
| **Jobset** | Inputs plus a Nix expression (or flake URI); re-evaluates when inputs change. |
| **Evaluation** | Instantiates the job expression into `.drv` files—the scheduled job list. |
| **Build** | One derivation from an evaluation, run on a configured build machine. |

Jobsets traditionally point at a `release.nix`-style expression. For flakes, configure the jobset with a flake URI; Hydra expects the flake’s `hydraJobs` attribute—an arbitrarily nested attrset whose leaves are derivations. See [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) for the output shape versus local `checks`.

### Official vs self-hosted

- **hydra.nixos.org** — builds Nixpkgs/NixOS and related projects; feeds caches and [channels](https://channels.nixos.org). On Nixpkgs PRs, [OfBorg](../06-nixpkgs/contribution/ofborg-and-ci.md) covers pre-merge checks; Hydra covers post-merge trunk evaluation and bulk builds.
- **Self-hosted** — NixOS exposes `services.hydra` for a local instance. Useful when you want scheduled multi-system jobsets and to push build products into your own substituter. Requires PostgreSQL state, build machines (or localhost), admin users (`hydra-create-user`), and typically `nix.settings.allowed-uris` so flake evaluation in restricted mode can fetch inputs.

### When not to use Hydra

For a single flake, prefer `nix flake check` / `nix build` on GitHub Actions (or similar): install Nix, pin with `flake.lock`, substitute from a cache. Hydra’s strength is continuous evaluation of large, changing job graphs—not replacing a ten-line CI workflow.

## Examples

Minimal flake `hydraJobs` (what a flake jobset consumes):

```nix
{
  outputs = { self, nixpkgs }: let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  in {
    packages.x86_64-linux.default = pkgs.hello;

    hydraJobs = {
      inherit (self) packages;
    };
  };
}
```

Sketch of a NixOS Hydra service (from the [Hydra README](https://github.com/NixOS/hydra); full options: [services.hydra](https://search.nixos.org/options?channel=26.05&query=services.hydra); adjust URL, mail, and builders for your host):

```nix
{
  services.hydra = {
    enable = true;
    hydraURL = "http://localhost:3000";
    notificationSender = "hydra@localhost";
    buildMachinesFiles = [];
    useSubstitutes = true;
  };

  # Flake jobsets need allowed URI prefixes under restricted eval:
  nix.settings.allowed-uris = [
    "github:"
    "git+https://github.com/"
  ];
}
```

Create an admin user after enable (as the `hydra` system user):

```bash
hydra-create-user alice --full-name 'Alice' \
  --email-address 'alice@example.org' --password-prompt --role admin
```

## References

- [NixOS/hydra](https://github.com/NixOS/hydra) — source, README (install, admin user, jobsets)
- [hydra.nixos.org](https://hydra.nixos.org/) — official Hydra for Nixpkgs/NixOS
- [NixOS options — `services.hydra`](https://search.nixos.org/options?channel=26.05&query=services.hydra) — self-hosted service module

## See also

- [CI with Nix](../11-development/ci-with-nix.md) — lightweight forge CI vs Hydra scale
- [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) — flake outputs for checks and Hydra jobs
- [Binary cache hosting](binary-cache-hosting.md) — serving build products as substituters
- [OfBorg and CI](../06-nixpkgs/contribution/ofborg-and-ci.md) — Nixpkgs PR CI before Hydra trunk builds
