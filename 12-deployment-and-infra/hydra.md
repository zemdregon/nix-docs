---
status: complete
last-checked: 2026-08
---

# Hydra

## Overview

[Hydra](https://github.com/NixOS/hydra) is the Nix-based continuous integration and release system. It polls project inputs, **evaluates** Nix expressions into job graphs, and **builds** the resulting derivations on a farm of builders. Successful builds become substitutable store paths—Hydra is how [hydra.nixos.org](https://hydra.nixos.org/) produces the binary packages behind Nixpkgs channels.

Hydra organizes work as **projects**, **jobsets**, **evaluations**, and **builds**. Flake-based projects typically expose a top-level [`hydraJobs`](../07-flakes/workflows/checks-and-hydraJobs.md) output that Hydra imports as the job tree. Self-hosting Hydra is the heavyweight path when you need a large, scheduled job graph and a project [binary cache](binary-cache-hosting.md); most application repos are better served by lightweight forge CI such as [GitHub Actions with Nix](../11-development/ci-with-nix.md).

## Details

### Boundaries

- **This page:** what Hydra is, how flake jobsets relate to `hydraJobs` / `checks`, a high-level NixOS self-host sketch, common failure modes, and when to pick Hydra vs forge CI vs OfBorg.
- **Not here:** full Hydra admin (declarative projects, mail, GC roots, queue tuning)—use the [Hydra README](https://github.com/NixOS/hydra) and [Hydra manual](https://nixos.org/hydra/manual/).
- **Not here:** forge CI install/cache recipes—see [CI with Nix](../11-development/ci-with-nix.md) and [private flakes and CI](../11-development/private-flakes-and-ci.md).

### Model

| Term | Role |
|------|------|
| **Project** | Grouping of related jobsets (often one git repo, e.g. nixpkgs). |
| **Jobset** | Inputs plus a Nix expression (or flake URI); re-evaluates when inputs change. |
| **Evaluation** | Instantiates the job expression into `.drv` files—the scheduled job list. |
| **Build** | One derivation from an evaluation, run on a configured build machine. |

Jobsets traditionally point at a `release.nix`-style expression. For flakes, configure the jobset with a flake URI; Hydra expects the flake’s `hydraJobs` attribute—an arbitrarily nested attrset whose leaves are derivations.

### Flake jobsets: `hydraJobs` vs `checks`

| Output | Role for Hydra / CI |
|--------|---------------------|
| **`hydraJobs.…`** | Nested attrset of derivation leaves. A **flake jobset** evaluates this tree (same shape `hydra-eval-jobs` / `nix flake check` walk). Nested names become job groups; leaves become builds. |
| **`checks.<system>.<name>`** | Local / forge gate derivations. `nix flake check` **builds** them by default. Hydra flake jobsets do **not** import `checks` as the job tree. |

Practical split (details and recipes: [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md)):

- Keep merge gates under `checks` so contributors and GHA/Forgejo run `nix flake check` without Hydra.
- Put what the farm should schedule under `hydraJobs` (often `inherit (self) packages;` plus nested tests). Reuse the same derivation in both when both paths should build it.
- `nix flake check` **evaluates** `hydraJobs` but does not schedule Hydra builds.

Hydra evaluates flakes in **restricted mode**. Flake inputs must come from URI prefixes listed in `nix.settings.allowed-uris` on the Hydra host (common prefixes: `github:`, `git+https://github.com/`).

### Official vs self-hosted

- **hydra.nixos.org** — builds Nixpkgs/NixOS and related projects; feeds caches and [channels](https://channels.nixos.org). On Nixpkgs PRs, [OfBorg](../06-nixpkgs/contribution/ofborg-and-ci.md) covers pre-merge checks; Hydra covers post-merge trunk evaluation and bulk builds.
- **Self-hosted** — NixOS module [`services.hydra`](https://search.nixos.org/options?channel=26.05&query=services.hydra) (options search; package/module live in nixpkgs). Useful when you want scheduled multi-system jobsets and to push products into your own substituter.

### Self-host sketch (`services.hydra`)

High-level pieces only—confirm names and defaults in [NixOS options — `services.hydra`](https://search.nixos.org/options?channel=26.05&query=services.hydra) and the [Hydra README](https://github.com/NixOS/hydra):

| Piece | Role |
|-------|------|
| **PostgreSQL** | With the default `services.hydra.dbi`, the module enables local `services.postgresql` and creates the `hydra` DB/user. State lives in Postgres—back it up; the module is not fully stateless. |
| **Web / queue** | `hydraURL`, `notificationSender`, and related options; UI typically on port `3000` unless you change `port` / `listenHost`. |
| **Builders** | `buildMachinesFiles` points at machines files (default includes `/etc/nix/machines` when `nix.buildMachines` is set). Empty list avoids a missing machines file on a standalone host; then configure [remote builders](../04-store-and-build/remote-builders.md) / `nix.buildMachines` as needed. |
| **Substitutes** | `useSubstitutes` (default `false` in the module)—lets the queue pull from binary caches; see the option description for trust/signature caveats. |
| **Disk thresholds** | `minimumDiskFree` / `minimumDiskFreeEvaluator` (GiB) pause queue runner / evaluator when free space is too low. |
| **allowed-uris** | Not a `services.hydra.*` option: set `nix.settings.allowed-uris` on the host so restricted flake eval can fetch inputs. |

Create an admin with `hydra-create-user` as the `hydra` system user after enable (README). Production hardening (TLS, SMTP, declarative projects) is out of scope here.

### Decision: Hydra vs forge CI vs OfBorg

| Need | Prefer |
|------|--------|
| Single app/flake PR gate (`nix flake check` / `nix build`) | [CI with Nix](../11-development/ci-with-nix.md) (GHA, Forgejo, etc.) |
| Large scheduled job graph, multi-system farm, org binary cache producer | **Hydra** (self-hosted or hydra.nixos.org for NixOS projects) |
| Nixpkgs **PR** eval/build feedback before merge | [OfBorg](../06-nixpkgs/contribution/ofborg-and-ci.md)—not a substitute for running your own Hydra |

Hydra’s strength is continuous evaluation of large, changing job graphs—not replacing a ten-line forge workflow.

### Failure modes

| Symptom | Likely cause |
|---------|----------------|
| Flake eval fails fetching inputs / restricted-mode errors | Missing URI prefixes in `nix.settings.allowed-uris` for those flake inputs. |
| Evaluation succeeds with **no jobs** | Flake has no (or empty) `hydraJobs`; only `checks` / `packages` without mirroring into `hydraJobs`. |
| Builds stuck queued; SSH works | Builder not trusted for the Hydra/`nix` SSH identity, or machines file not listed in `buildMachinesFiles`—see [remote builders](../04-store-and-build/remote-builders.md). |
| Evaluator / queue runner idle despite free CPU | Free disk below `minimumDiskFree` / `minimumDiskFreeEvaluator`, or store/volume full—free space or raise thresholds deliberately. |

## Examples

Minimal flake `hydraJobs` (what a flake jobset consumes); keep gates in `checks` for forge CI:

```nix
{
  outputs = { self, nixpkgs }: let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
    hello = pkgs.hello;
  in {
    packages.x86_64-linux.default = hello;

    checks.x86_64-linux.hello = hello;

    hydraJobs = {
      inherit (self) packages;
    };
  };
}
```

Sketch of a NixOS Hydra service (from the [Hydra README](https://github.com/NixOS/hydra) / wiki patterns; full options: [services.hydra](https://search.nixos.org/options?channel=26.05&query=services.hydra); adjust URL, mail, and builders for your host):

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
- [Hydra manual](https://nixos.org/hydra/manual/) — admin and jobset reference
- [NixOS Wiki — Hydra](https://wiki.nixos.org/wiki/Hydra) — secondary; flake jobset and restricted-mode notes

## See also

- [CI with Nix](../11-development/ci-with-nix.md) — lightweight forge CI vs Hydra scale
- [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) — flake outputs for checks and Hydra jobs
- [Binary cache hosting](binary-cache-hosting.md) — serving build products as substituters
- [OfBorg and CI](../06-nixpkgs/contribution/ofborg-and-ci.md) — Nixpkgs PR CI before Hydra trunk builds
- [Remote builders](../04-store-and-build/remote-builders.md) — machines Hydra’s queue can schedule onto
- [Private flakes and CI](../11-development/private-flakes-and-ci.md) — private inputs and forge secrets (not Hydra admin)
