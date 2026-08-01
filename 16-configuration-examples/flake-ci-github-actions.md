---
status: complete
last-checked: 2026-08
---

# Flake CI with GitHub Actions

## Overview

This walkthrough is a **worked GitHub Actions CI config** for a Nix flake: checkout the repo (including `flake.lock`), install Nix on the runner, optionally wire a project binary cache, then run the same flake gates you use locally—typically `nix flake check` and/or targeted `nix build` paths. It composes the teaching pages in [Domains composed](#domains-composed); for runner install patterns and failure-mode theory, start with [CI with Nix](../11-development/ci-with-nix.md).

Action choices below ([cachix/install-nix-action](https://github.com/cachix/install-nix-action), [cachix/cachix-action](https://github.com/cachix/cachix-action), Determinate Systems installers, and others) are **common patterns, not endorsements**. Pin action majors yourself—examples use `checkout@v4` (still common; newer majors exist), `install-nix-action@v31`, and `cachix-action@v17` as of 2026-08; [nix.dev](https://nix.dev/guides/recipes/continuous-integration-github-actions) pasted pins may lag.

Flake workflows need experimental [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md). Nixpkgs-scale job graphs belong on [Hydra](../12-deployment-and-infra/hydra.md)—not this leaf.

## Details

### What you get

One `.github/workflows/ci.yml` (or split workflows) that:

1. Evaluates and builds the locked flake graph CI shares with developers.
2. Gates pull requests with `nix flake check` (builds `checks` and type-checks conventional outputs including `nixosConfigurations.*.config.system.build.toplevel`).
3. Optionally substitutes from and pushes to a project binary cache.
4. Optionally shards heavy config flakes with a **host matrix** instead of one monolithic check job.

### Domains composed

| Domain | Pages this example uses |
|--------|-------------------------|
| CI concepts | [CI with Nix](../11-development/ci-with-nix.md), [private flakes and CI](../11-development/private-flakes-and-ci.md) |
| Flake outputs and gates | [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md), [config repo layout](../07-flakes/workflows/config-repo-layout.md) |
| Caches | [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md), [binary caches (cheatsheet)](../cheatsheets/binary-caches.md) |
| Private inputs | [access-tokens](../05-cli-and-tooling/config/access-tokens.md) |
| Experimental CLI | [`nix-command`](../08-experimental-features/nix-command.md), [`flakes`](../08-experimental-features/flakes.md) |
| Fleet layout (optional) | [Multi-host config repo](multi-host-config-repo.md) — host matrix and mono-repo path filters |

### Typical pipeline

1. **Checkout** — include `flake.lock` so CI and laptops share the same input graph.
2. **Install Nix** — e.g. `cachix/install-nix-action` (enables `nix-command` + `flakes` by default) or another verified install action; see [CI with Nix](../11-development/ci-with-nix.md).
3. **Optional cache** — configure substituters and push credentials (`CACHIX_AUTH_TOKEN` and/or `CACHIX_SIGNING_KEY` as CI secrets—never commit). See [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md).
4. **Gate** — `nix flake check`, `nix build`, or a host matrix for config mono-repos.

Prefer **binary cache substitutes** over rebuilding everything on every clean runner. Without a project cache, wall time grows and jobs hit timeouts.

### Flake `checks` and `nix flake check`

Expose gate derivations under `checks.<system>.<name>` in `flake.nix`. `nix flake check` evaluates the flake, **builds** each check derivation (unless `--no-build`), and type-checks other conventional outputs—including each `nixosConfigurations.<host>.config.system.build.toplevel`. Useful flags: `--no-build` (evaluate only), `--all-systems` (every system key). Full output semantics: [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md). This walkthrough does not cover Hydra jobset operations.

For config mono-repos where a single `nix flake check` is too heavy, parallel jobs can `nix build .#nixosConfigurations.<host>.config.system.build.toplevel` per host—see [config repo layout](../07-flakes/workflows/config-repo-layout.md) and [Multi-host config repo](multi-host-config-repo.md).

### Job shapes

| Shape | When | Typical wiring |
|-------|------|----------------|
| Single flake check | App/library flake; cheap `checks` | One job: `nix flake check` (optional `nix build .#…`) |
| Host matrix | Many `nixosConfigurations` | Matrix over host names; build each toplevel in parallel |
| Path filters | Large mono-repo | Forge path filters skip unrelated host jobs; keep a cheap lint/`checks` job when filters would skip everything |

### Secrets and private inputs

Do not commit Cachix tokens, signing keys, or forge `access-tokens` values. Store them in the CI secret store. For private flake inputs (`github:`, `gitlab:`, …), inject Nix [`access-tokens`](../05-cli-and-tooling/config/access-tokens.md) via `extra_nix_config` on the install action. Details and failure table: [private flakes and CI](../11-development/private-flakes-and-ci.md).

### Failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Very slow CI or timeouts | No project cache; clean runner rebuilds from source | Wire substituter + optional push ([binary caches](../cheatsheets/binary-caches.md), [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md)) |
| `experimental feature 'nix-command' is disabled` | Install step did not enable features | Confirm install action settings or pass `extra_nix_config`; needs [`nix-command`](../08-experimental-features/nix-command.md) + [`flakes`](../08-experimental-features/flakes.md) |
| Private input 401 / 404 | Locked private fetch without CI token | Set `access-tokens` from secrets ([access-tokens](../05-cli-and-tooling/config/access-tokens.md), [private flakes and CI](../11-development/private-flakes-and-ci.md)) |
| Check fails only in CI | IFD or expensive eval in a `checks` derivation | Keep checks cheap; see [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) |
| Host matrix job fails for one host | Host-specific module or hardware import | Build that host locally; fix imports under `hosts/` ([Multi-host config repo](multi-host-config-repo.md)) |

## Examples

All YAML below is **illustrative**—not evaluated in this vault. Requires a runner with network and your own secrets.

### Minimal flake check

Aligned with the [nix.dev GitHub Actions recipe](https://nix.dev/guides/recipes/continuous-integration-github-actions):

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
  push:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cachix/install-nix-action@v31
      - run: nix flake check
```

### With optional Cachix

Omit the cache steps if you only substitute from `cache.nixos.org`:

```yaml
# .github/workflows/ci.yml (fragment)
      - uses: actions/checkout@v4
      - uses: cachix/install-nix-action@v31
      - uses: cachix/cachix-action@v17
        with:
          name: YOUR_CACHE_NAME
          authToken: ${{ secrets.CACHIX_AUTH_TOKEN }}
          # or signingKey: ${{ secrets.CACHIX_SIGNING_KEY }}
      - run: nix flake check
```

### Host matrix (config mono-repo)

For fleets with many `nixosConfigurations`, shard builds across parallel jobs:

```yaml
# .github/workflows/nixos-hosts.yml (sketch)
name: NixOS hosts
on:
  pull_request:
  push:
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        host: [laptop, server]
    steps:
      - uses: actions/checkout@v4
      - uses: cachix/install-nix-action@v31
      - run: nix build .#nixosConfigurations.${{ matrix.host }}.config.system.build.toplevel
```

Adjust `matrix.host` to your `nixosConfigurations` keys. Optional path filters (forge-native) can skip host jobs when only unrelated paths change—see [Multi-host config repo](multi-host-config-repo.md).

### Private flake inputs (`access-tokens`)

Pass a forge token from CI secrets; do not hardcode:

```yaml
      - uses: cachix/install-nix-action@v31
        with:
          extra_nix_config: |
            access-tokens = github.com=${{ secrets.GH_TOKEN_FOR_NIX }}
```

Host-specific token maps and org matrices: [private flakes and CI](../11-development/private-flakes-and-ci.md).

## References

- [nix.dev — Continuous integration with GitHub Actions](https://nix.dev/guides/recipes/continuous-integration-github-actions) — checkout, install Nix, cache, build
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — experimental flake evaluation and `checks` builds
- [cachix/install-nix-action](https://github.com/cachix/install-nix-action) — install Nix on GitHub Actions (example pattern)
- [cachix/cachix-action](https://github.com/cachix/cachix-action) — wire Cachix pull/push in Actions (example pattern)
- [Cachix documentation](https://docs.cachix.org/) — hosted binary cache push/pull (optional)

## See also

- [CI with Nix](../11-development/ci-with-nix.md) — runner install, job shapes, caching theory
- [Private flakes and CI](../11-development/private-flakes-and-ci.md) — private-input auth and org CI matrices
- [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) — `checks` output and `nix flake check` semantics
- [Binary caches (cheatsheet)](../cheatsheets/binary-caches.md) — consume / host / sign chooser
- [Hydra](../12-deployment-and-infra/hydra.md) — large scheduled job graphs (not forge CI)
- [Multi-host config repo](multi-host-config-repo.md) — fleet flake with host-matrix CI hooks
