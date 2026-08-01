---
status: complete
---

# Private flakes and CI

## Overview

Private flake inputs (`github:Org/private`, GitLab, self-hosted forges) need **credentials whenever Nix evaluates, locks, or fetches** those sources. Configure Nix [`access-tokens`](../05-cli-and-tooling/config/access-tokens.md) or [`netrc-file`](../05-cli-and-tooling/config/access-tokens.md#netrc-file)—not flake registries, and not by baking secrets into the repo.

In CI, inject forge tokens from the runner’s secret store into `nix.conf` (or the installer’s `extra_nix_config`). That is the same pattern sketched under [CI with Nix](ci-with-nix.md); this page covers **private-input failure modes**, org mono-repo job shape, and how auth interacts with [pure eval](../07-flakes/pure-eval-and-impure.md) and [binary caches](../12-deployment-and-infra/binary-cache-hosting.md).

## Details

### What needs auth

Any flakeref that hits a private HTTPS host—`github:…`, `gitlab:…`, `git+https://…`—requires a token (or netrc) on the machine that runs `nix flake lock`, `nix flake update`, `nix flake check`, or `nix build`. Public inputs do not. Tokens authorize the **download of locked inputs**; they do not relax purity rules—see [pure eval and impure](../07-flakes/pure-eval-and-impure.md).

Credential setup (host→token maps, GitLab `PAT:` / `OAuth2:` prefixes, netrc paths) lives on [access tokens](../05-cli-and-tooling/config/access-tokens.md). Never commit real tokens in flakes, lockfiles, wiki examples, or shared config in git.

### Registries are not auth

[Flake registries](../07-flakes/registries-and-refs.md) remap symbolic flakerefs to concrete URLs. They do **not** supply credentials. A registry entry that points at a private repo still fails at fetch time without `access-tokens` / `netrc-file` on that host.

### CI failure modes

Typical private-input failures in CI (symptoms vary by Nix version and forge):

| Symptom (class) | Likely cause |
|-----------------|--------------|
| 401 / 404 on a private `github:` / `gitlab:` input | Token missing, wrong host key, or insufficient scope |
| Eval works locally, fails on the runner | Laptop has `~/.config/nix/nix.conf` tokens; CI does not |
| Lock / update fails; check of an already-locked flake fails the same way | Fetch of locked NAR/tarball still needs auth |
| “Forbidden in pure evaluation mode” / absolute path errors | Unrelated to tokens—impure paths or unlocked fetches; see [pure eval](../07-flakes/pure-eval-and-impure.md) |
| Builds miss cache / rebuild everything | Cache auth missing (Cachix/Attic/substituter)—separate from forge tokens; see [CI with Nix](ci-with-nix.md) and [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) |

Inject tokens at install time so every later Nix step sees them. Prefer a **fine-scoped** PAT (read-only on the private input repos) stored as a CI secret. Do not echo secrets into logs.

### Org mono-repo CI

Fleet / config repos often declare private shared modules or internal flakes as inputs—see [config repo layout](../07-flakes/workflows/config-repo-layout.md) for where those sit in the tree.

Common job shapes (compare; pick for your scale):

- **Single gate:** one `nix flake check` (optionally `nix build` for packages you care about). Wire `checks` / optional `hydraJobs` as in [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md).
- **Host matrix:** parallel jobs that build or check one `nixosConfigurations.<host>` (or a path filter of hosts) when full-flake check is too heavy.
- **Path filters:** skip host rebuilds when only docs or unrelated trees change—forge-native path filters, not Nix-specific.

Caching private builds still needs **cache** credentials (substituter pull, and push if you upload). That is independent of forge `access-tokens`; patterns stay on [binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) and [CI with Nix](ci-with-nix.md).

### Pure eval reminder

Flake evaluation is pure by default. A correctly configured token lets Nix fetch a **locked** private input; it does not make `--impure` unnecessary for host paths, `getEnv`, or unlocked fetches. Fix purity separately from auth.

## Examples

Minimal GitHub Actions sketch: install Nix, inject a forge token from a secret, then check the flake. Placeholders only; action majors illustrative (align with [CI with Nix](ci-with-nix.md) / nix.dev). Not run in this vault.

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
        with:
          extra_nix_config: |
            access-tokens = github.com=${{ secrets.GH_TOKEN_FOR_NIX }}
      # Optional: project binary cache — separate secret from forge token
      # - uses: cachix/cachix-action@v17
      #   with:
      #     name: YOUR_CACHE_NAME
      #     authToken: ${{ secrets.CACHIX_AUTH_TOKEN }}
      - run: nix flake check
```

GitLab CI shape (same idea—write `access-tokens` before any Nix fetch; secret name is yours):

```yaml
# .gitlab-ci.yml (fragment)
variables:
  # Prefer CI/CD variables marked masked/protected — not inline tokens
flake-check:
  image: ...
  before_script:
    - mkdir -p ~/.config/nix
    - echo "access-tokens = gitlab.com=PAT:${NIX_GITLAB_PAT}" >> ~/.config/nix/nix.conf
  script:
    - nix flake check
```

Illustrative private input in `flake.nix` (no secrets here—auth is only in nix.conf / CI):

```nix
{
  inputs.internal = {
    url = "github:YOUR_ORG/private-modules";
  };
  # …
}
```

## References

- [Nix manual — `nix.conf` (`access-tokens`, `netrc-file`)](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) — forge token maps and netrc
- [nix.dev — Continuous integration with GitHub Actions](https://nix.dev/guides/recipes/continuous-integration-github-actions) — install Nix, cache secrets, basic workflow
- [Nix manual — `nix registry`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-registry.html) — registry remapping (not credentials)

## See also

- [Access tokens](../05-cli-and-tooling/config/access-tokens.md) — `access-tokens` / `netrc-file` format and security
- [CI with Nix](ci-with-nix.md) — install, caches, general pipeline
- [Config repo layout](../07-flakes/workflows/config-repo-layout.md) — private inputs in a fleet mono-repo
- [Registries and refs](../07-flakes/registries-and-refs.md) — flakeref remapping vs auth
- [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) — purity vs authorized fetches
- [Binary cache hosting](../12-deployment-and-infra/binary-cache-hosting.md) — Cachix / Attic / self-hosted (cache auth)
- [checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) — flake CI outputs
