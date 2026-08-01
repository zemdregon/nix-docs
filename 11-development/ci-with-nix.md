---
status: complete
---

# CI with Nix

## Overview

Continuous integration with Nix means **install Nix on the runner**, then **evaluate and build** the same flake (or expression) developers use locally. Pin inputs with `flake.lock` so CI and laptops share the same dependency graph. Prefer **substituting from binary caches** over rebuilding on every clean runner; push newly built paths back to a project cache when write access is available.

[nix.dev](https://nix.dev/guides/recipes/continuous-integration-github-actions) documents one GitHub Actions path: install Nix, optionally wire a project cache (often [Cachix](https://docs.cachix.org/)), then run builds. Action choices below (Cachix, Determinate Systems, and others) are **examples of common patterns, not endorsements**. Flake-oriented jobs typically use experimental `nix flake check` / `nix build` (`nix-command` and `flakes`). Nixpkgs-scale job graphs belong on [Hydra](../12-deployment-and-infra/hydra.md). Cache hosting options are covered under [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md).

## Details

### Typical pipeline

1. Checkout the repo (including `flake.lock`).
2. Install Nix on the runner. Common GitHub Actions patterns: [cachix/install-nix-action](https://github.com/cachix/install-nix-action) (nix.dev recipe; enables `nix-command` and `flakes` by default) or Determinate Systems’ installer actions (e.g. [`nix-installer-action`](https://github.com/DeterminateSystems/nix-installer-action) / [`determinate-nix-action`](https://github.com/DeterminateSystems/determinate-nix-action)—check each action’s README for which Nix distribution it installs and how to pin versions).
3. Configure substituters / push credentials for a binary cache when used.
4. Run builds. Classic expressions: `nix-build` (and optionally `nix-shell`) as in the nix.dev recipe. Flakes: `nix flake check` (evaluates flake outputs and builds `checks`) and/or `nix build` for packages you care about. Wire `checks` and optional `hydraJobs` as in [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md).

`nix flake check` is experimental (`nix-command` / `flakes`; see the [Nix manual](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html)). Useful flags: `--no-build` (evaluate only), `--all-systems` (check every system key).

### Caching

Without a project cache, every clean runner rebuilds from scratch. A **binary cache** lets CI and developers substitute shared store paths:

- **Cachix** — hosted cache paired with `cachix-action` in the nix.dev recipe (auth via CI secrets: `CACHIX_AUTH_TOKEN` and/or `CACHIX_SIGNING_KEY`; never commit tokens). See [Cachix docs](https://docs.cachix.org/).
- **Attic** / self-hosted — same idea: substituter URL + signing or auth; see [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md).

Hydra also acts as a large-scale cache producer for nixpkgs-style jobsets; most application repos do not need Hydra.

### Secrets and private inputs

Do not commit forge tokens, signing keys, or Cachix write credentials. Store them in the CI secret store and inject at runtime. For private flake inputs, set Nix [`access-tokens`](../05-cli-and-tooling/config/access-tokens.md) from CI secrets (e.g. via `extra_nix_config` on `install-nix-action`) so evaluation can fetch locked private sources. If evaluation fails mysteriously in CI, compare purity and fetch errors with [debugging evaluation](debugging-evaluation.md).

### Scale choice

| Context | Usual CI |
|---------|----------|
| Single project / flake | GitHub Actions (nix.dev recipe), GitLab CI, etc. |
| Massive job graph (e.g. nixpkgs) | [Hydra](../12-deployment-and-infra/hydra.md) |

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
- [cachix/install-nix-action](https://github.com/cachix/install-nix-action) — install Nix on GitHub Actions (cited by nix.dev; example pattern)
- [Cachix documentation](https://docs.cachix.org/) — hosted binary cache push/pull (example pattern)
- [DeterminateSystems/nix-installer-action](https://github.com/DeterminateSystems/nix-installer-action) — alternate GitHub Actions install pattern (example, not endorsement)

## See also

- [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) — flake CI outputs and `nix flake check`
- [Hydra](../12-deployment-and-infra/hydra.md) — large-scale Nix CI
- [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) — Cachix, Attic, and self-hosted caches
- [Access tokens](../05-cli-and-tooling/config/access-tokens.md) — private flake inputs in CI
- [Private flakes and CI](private-flakes-and-ci.md) — private-input failure modes and org CI matrices
- [Debugging evaluation](debugging-evaluation.md) — evaluating flakes when CI fails early
