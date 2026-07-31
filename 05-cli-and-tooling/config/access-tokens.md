---
status: complete
---

# Access Tokens

## Overview

**`access-tokens`** is a [`nix.conf`](nix-conf.md) setting that maps hosts to credentials so Nix can fetch **private** GitHub, GitLab, or similar HTTPS sources—flake inputs, `fetchGit`, and related downloads that need token-based auth.

Tokens are secrets. Put them only in a user-local or machine-local config (or a file referenced by config), never in a flake, lockfile, or committed repository. Prefer [`netrc-file`](#netrc-file) or host credential helpers when that fits your workflow; use `access-tokens` when you need the host→token map Nix documents for Git forges.

## Details

### Format

The value is a space-separated list of `host=token` pairs. Nix picks a token by matching the `host` part against the input's host. The host may include a path prefix so one org or group can use a different token than the rest of the forge (e.g. `github.com/my-org=…`).

Example shape (placeholders only):

```text
access-tokens = github.com=ghp_REDACTED gitlab.com=PAT:glpat-REDACTED
```

**GitHub.** The token is a personal access token (OAuth-token string) from the GitHub account or org that can read the private repo.

**GitLab.** The value is `type:tokenstring`, where `type` is `OAuth2` or `PAT` (personal access token). Those are different GitLab credential kinds; use the prefix that matches what you created.

Self-hosted forges work the same way: use the hostname Nix will see in the flakeref or fetch URL (e.g. `gitlab.mycompany.com=PAT:…`).

### When it applies

Authenticated HTTPS is needed when evaluating or locking flakes whose [inputs](../../07-flakes/anatomy/inputs-and-outputs.md) point at private repos, or when other fetchers hit those hosts. Public inputs do not need this setting. Pure evaluation still forbids impure network access unless the fetch is already locked or allowed by the evaluation mode; see [pure eval and impure](../../07-flakes/pure-eval-and-impure.md). Tokens only authorize the download—they do not relax purity rules.

### netrc-file

**`netrc-file`** points at an absolute path to a [netrc](https://curl.se/docs/manpage.html)-format file. Nix uses those HTTP(S) credentials when downloading from matching hosts. Default is under the Nix config directory; `~` is **not** expanded—use a full path such as `/home/you/.config/nix/netrc`.

Prefer netrc (or OS/git credential helpers outside Nix) when you already manage forge login that way. Use `access-tokens` when you want the forge-specific `host=token` / `PAT:` / `OAuth2:` forms documented for Nix.

### Security

- Never commit real tokens in wiki examples, flakes, CI logs, or shared `nix.conf` in git.
- Restrict file permissions on `nix.conf` / netrc that contain tokens (`chmod 600`).
- Rotate tokens if they leak; scope PATs to the minimum repo/org access required.

## Examples

User config (`~/.config/nix/nix.conf`) with placeholders—replace with real tokens locally, do not commit:

```ini
# WARNING: secrets — keep this file out of version control
access-tokens = github.com=ghp_YOUR_TOKEN_HERE gitlab.com=PAT:glpat_YOUR_TOKEN_HERE
```

Org-scoped GitHub token plus a self-hosted GitLab PAT:

```ini
access-tokens = github.com/my-org=ghp_YOUR_TOKEN_HERE gitlab.example.com=PAT:glpat_YOUR_TOKEN_HERE
```

Optional netrc instead of (or alongside) forge token maps—path must be absolute:

```ini
netrc-file = /home/you/.config/nix/netrc
```

```text
# /home/you/.config/nix/netrc
machine github.com
login YOUR_GITHUB_USERNAME
password ghp_YOUR_TOKEN_HERE
```

With tokens configured, private flake inputs resolve like public ones (illustrative `flake.nix` fragment):

```nix
{
  inputs.private = {
    url = "github:my-org/private-repo";
  };
  # …
}
```

## See also

- [`nix.conf`](nix-conf.md) — configuration file and related settings
- [Flake inputs and outputs](../../07-flakes/anatomy/inputs-and-outputs.md) — declaring and locking inputs (including private remotes)
- [Pure eval and impure](../../07-flakes/pure-eval-and-impure.md) — evaluation purity vs network fetches
- [`nix flake`](../modern-cli/nix-flake.md) — CLI for locking and fetching flakes

## References

- [Nix manual — `nix.conf` (`access-tokens`, `netrc-file`)](https://nix.dev/manual/nix/stable/command-ref/conf-file.html)
- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html)
- [GitHub — authorizing OAuth apps / PATs](https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps)
- [GitLab — API authentication](https://docs.gitlab.com/ee/api/rest/authentication.html)
