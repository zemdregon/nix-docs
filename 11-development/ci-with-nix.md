---
status: complete
last-checked: 2026-08
---

# CI with Nix

## Overview

Continuous integration with Nix means **install Nix on the runner**, then **evaluate and build** the same flake (or expression) developers use locally. Pin inputs with `flake.lock` so CI and laptops share the same dependency graph. Prefer **substituting from binary caches** over rebuilding on every clean runner; push newly built paths back to a project cache when write access is available.

[nix.dev](https://nix.dev/guides/recipes/continuous-integration-github-actions) documents one GitHub Actions path: install Nix, optionally wire a project cache (often [Cachix](https://docs.cachix.org/)), then run builds. Action choices below (Cachix, Determinate Systems, and others) are **examples of common patterns, not endorsements**. Flake-oriented jobs typically use experimental `nix flake check` / `nix build` (`nix-command` and `flakes`). Nixpkgs-scale job graphs belong on [Hydra](../12-deployment-and-infra/hydra.md). Cache hosting options are covered under [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md).

## Boundaries

- **This page:** runner install → cache → job shape → common CI failure modes for a single project or config flake.
- **Not here:** private-input auth deep dive ([private flakes and CI](private-flakes-and-ci.md)); which flake outputs to expose ([checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md)); mono-repo folder conventions ([config repo layout](../07-flakes/workflows/config-repo-layout.md)); which Nix distribution to install on a laptop ([installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md)); Hydra jobset ops ([Hydra](../12-deployment-and-infra/hydra.md)).

## Details

### Typical pipeline

1. Checkout the repo (including `flake.lock`).
2. Install Nix on the runner. Common GitHub Actions patterns: [cachix/install-nix-action](https://github.com/cachix/install-nix-action) (nix.dev recipe; enables `nix-command` and `flakes` by default) or Determinate Systems’ installer actions (e.g. [`nix-installer-action`](https://github.com/DeterminateSystems/nix-installer-action) / [`determinate-nix-action`](https://github.com/DeterminateSystems/determinate-nix-action)—check each action’s README for which Nix distribution it installs and how to pin versions). Compare distributions under [installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md); pin the action (and thus the Nix) your team verified.
3. Configure substituters / push credentials for a binary cache when used.
4. Run builds. Classic expressions: `nix-build` (and optionally `nix-shell`) as in the nix.dev recipe. Flakes: `nix flake check` (evaluates flake outputs and builds `checks`) and/or `nix build` for packages you care about. Wire `checks` and optional `hydraJobs` as in [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md).

`nix flake check` is experimental (`nix-command` / `flakes`; see the [Nix manual](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html)). Useful flags: `--no-build` (evaluate only), `--all-systems` (check every system key).

### Job shapes

Pick a gate that matches repo size. Config mono-repos often need more than one `nix flake check`—see [config repo layout](../07-flakes/workflows/config-repo-layout.md) and [private flakes and CI](private-flakes-and-ci.md).

| Shape | When | Typical command / wiring |
|-------|------|--------------------------|
| Single flake check | Small app / library flake; cheap `checks` | One job: `nix flake check` (optional `nix build`). Expose gates via [`checks`](../07-flakes/workflows/checks-and-hydraJobs.md). |
| Host matrix | Config flake with many `nixosConfigurations` / hosts | Parallel jobs per host (or shard); build `.#nixosConfigurations.<host>.config.system.build.toplevel` (or equivalent). Tree layout: [config repo layout](../07-flakes/workflows/config-repo-layout.md). |
| Path filters | Large mono-repo; docs-only or single-host PRs | Forge-native path filters skip unrelated host jobs; still keep a cheap lint/`checks` job when filters would skip everything. Auth for private inputs: [private flakes and CI](private-flakes-and-ci.md). |

| Context | Usual CI |
|---------|----------|
| Single project / flake | GitHub Actions (nix.dev recipe), GitLab CI, Forgejo Actions, etc. |
| Massive job graph (e.g. nixpkgs) | [Hydra](../12-deployment-and-infra/hydra.md) |

### Caching

Without a project cache, every clean runner rebuilds from scratch. A **binary cache** lets CI and developers substitute shared store paths:

- **Cachix** — hosted cache paired with `cachix-action` in the nix.dev recipe (auth via CI secrets: `CACHIX_AUTH_TOKEN` and/or `CACHIX_SIGNING_KEY`; never commit tokens). See [Cachix docs](https://docs.cachix.org/).
- **Attic** / self-hosted — same idea: substituter URL + signing or auth; see [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md).

Hydra also acts as a large-scale cache producer for nixpkgs-style jobsets; most application repos do not need Hydra.

### Secrets and private inputs

Do not commit forge tokens, signing keys, or Cachix write credentials. Store them in the CI secret store and inject at runtime. For private flake inputs, set Nix [`access-tokens`](../05-cli-and-tooling/config/access-tokens.md) from CI secrets (e.g. via `extra_nix_config` on `install-nix-action`) so evaluation can fetch locked private sources. Full private-input failure table: [private flakes and CI](private-flakes-and-ci.md). If evaluation fails mysteriously in CI, compare purity and fetch errors with [debugging evaluation](debugging-evaluation.md).

### Failure modes

| Failure | What goes wrong |
|---------|-----------------|
| No project cache | Clean runners rebuild from source → long wall time and flaky timeouts. Wire a substituter (and push on success) as under [Caching](#caching) / [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md). |
| Missing `nix-command` / `flakes` | `nix flake check` / `nix build` unknown or disabled. Enable experimental features in the install action / `nix.conf`, or use an installer that sets them—confirm with `nix config show` after install ([installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md)). |
| Private input 401 / 404 | Locked private `github:` / `gitlab:` fetch without CI `access-tokens` (or wrong host/scope). Inject forge secrets as in [Secrets and private inputs](#secrets-and-private-inputs); details in [private flakes and CI](private-flakes-and-ci.md). |
| IFD inside a check | A `checks` derivation (or eval path) [imports from derivation](../02-concepts/import-from-derivation.md) → realise-during-eval, slow gates, or failure when `allow-import-from-derivation = false`. Keep checks cheap; see [lazy trees and eval perf](lazy-trees-and-eval-perf.md) and [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md). |

## Examples

Minimal GitHub Actions sketch aligned with the [nix.dev CI recipe](https://nix.dev/guides/recipes/continuous-integration-github-actions), adapted for a flake gate. **Illustrative**—not run in this vault; requires a runner with network and your own secrets. Action major tags below match current `install-nix-action` / `cachix-action` majors as of 2026-07 (nix.dev’s pasted pins may lag—pin majors or full tags yourself). Same job shape works with other install actions; swap the install step only. Placeholders only; keep secrets out of git:

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
      # Optional: project binary cache (omit if you only use cache.nixos.org)
      # - uses: cachix/cachix-action@v17
      #   with:
      #     name: YOUR_CACHE_NAME
      #     authToken: ${{ secrets.CACHIX_AUTH_TOKEN }}
      #     # or signingKey: ${{ secrets.CACHIX_SIGNING_KEY }}
      - run: nix flake check
      - run: nix build
```

Classic (non-flake) jobs from the same recipe use `nix-build` / `nix-shell` instead of `nix flake check` / `nix build`, and may set `nix_path` (e.g. `nixpkgs=channel:nixos-unstable`) on `install-nix-action`.

For private GitHub flake inputs, pass a token into Nix config from a secret (do not hardcode):

```yaml
- uses: cachix/install-nix-action@v31
  with:
    extra_nix_config: |
      access-tokens = github.com=${{ secrets.GH_TOKEN_FOR_NIX }}
```

## References

- [nix.dev — Continuous integration with GitHub Actions](https://nix.dev/guides/recipes/continuous-integration-github-actions) — install Nix, Cachix secrets/actions, basic workflow
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — experimental flake evaluation and `checks` builds
- [Nix manual — `access-tokens`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-access-tokens) — forge tokens for private fetches
- [Nix manual — Import from derivation](https://nix.dev/manual/nix/stable/language/import-from-derivation.html) — realise-during-eval cost in checks
- [cachix/install-nix-action](https://github.com/cachix/install-nix-action) — install Nix on GitHub Actions (cited by nix.dev; example pattern)
- [Cachix documentation](https://docs.cachix.org/) — hosted binary cache push/pull (example pattern)
- [DeterminateSystems/nix-installer-action](https://github.com/DeterminateSystems/nix-installer-action) — alternate GitHub Actions install pattern (example, not endorsement)

## See also

- [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) — flake CI outputs and `nix flake check`
- [config repo layout](../07-flakes/workflows/config-repo-layout.md) — mono-repo hosts/modules and CI matrix fit
- [Private flakes and CI](private-flakes-and-ci.md) — private-input failure modes and org CI matrices
- [Installers and Nix variants](../13-implementations/frontends-and-ux/installers-and-nix-variants.md) — which Nix distribution the runner action installs
- [Hydra](../12-deployment-and-infra/hydra.md) — large-scale Nix CI
- [Binary caches (cheatsheet)](../cheatsheets/binary-caches.md) — consume / host / sign chooser
- [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) — Cachix, Attic, and self-hosted caches
- [Access tokens](../05-cli-and-tooling/config/access-tokens.md) — private flake inputs in CI
- [Import from derivation](../02-concepts/import-from-derivation.md) — IFD cost in eval/check gates
- [Lazy trees and eval perf](lazy-trees-and-eval-perf.md) — IFD policy and eval latency in CI
- [Debugging evaluation](debugging-evaluation.md) — evaluating flakes when CI fails early
- [Flake CI with GitHub Actions (worked example)](../16-configuration-examples/flake-ci-github-actions.md)
- [Experimental: flakes](../08-experimental-features/flakes.md) / [nix-command](../08-experimental-features/nix-command.md) — features `nix flake check` needs
