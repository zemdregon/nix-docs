---
status: complete
last-checked: 2026-07
---

# fetchTree and Git

## Overview

The **`fetch-tree`** experimental feature enables `builtins.fetchTree` — a generic interface for fetching remote filesystem trees (Git repos, tarballs, plain files, and other backends) into the Nix store. It is the fetch layer flakes use to resolve and pin inputs.

**Version stamp:** As of the Nix **2.34.x** stable reference manual (`nix.dev/manual/nix/stable/` → 2.34; title 2.34.9), `fetch-tree`, `git-hashing`, and `verified-fetches` remain experimental and must be enabled explicitly (verified on Nix **2.34.8**). The **`flakes`** flag always enables `fetch-tree`; you do not need both. Enabling **`fetch-tree` alone** is the supported way to try the fetcher in isolation without the full flake format and CLI — the manual describes this as a release candidate for eventual stabilization.

Two related Git-oriented flags live alongside it: **`git-hashing`** (content-addressed store objects hashed with Git's algorithm, unreadable by older Nix) and **`verified-fetches`** (signature verification for Git commits via `fetchGit`). See [Feature Flags Overview](feature-flags-overview.md) for how to enable flags.

## Details

**`fetch-tree` and `builtins.fetchTree`.** With the flag on, Nix exposes `builtins.fetchTree`, which fetches a tree or file through a backend selected by a required `type` attribute (for example `git`, `tarball`, `file`). The function returns an attribute set including `outPath`, `narHash`, and backend-specific metadata. A subset of those output attributes can be passed back into a later `fetchTree` call to reproduce the same result — the builtin is idempotent in that sense.

Do not treat this page as a schema reference: per-type input attributes, URL-like syntax, and output fields are documented in the [Nix manual — Built-ins](https://nix.dev/manual/nix/2.34/language/builtins.html#builtins-fetchTree). For a wiki-oriented summary of fetch builtins and flag requirements, see [Import and Fetch](../03-language/builtins/import-and-fetch.md).

**Relationship to flakes.** Flake input locking resolves unlocked references in `flake.nix` to concrete fetch arguments stored under each node's **`locked`** field in [flake.lock](../07-flakes/anatomy/lockfile.md). Those `locked` attributes are **`builtins.fetchTree` arguments** — what Nix actually passes when evaluating the flake. Enabling `flakes` therefore implies `fetch-tree`; flake workflows depend on this fetcher even if you never call `fetchTree` yourself.

**What still needs `flakes`.** Attribute-set forms with backends such as `git`, `tarball`, and `file` work with **`fetch-tree` alone**. Flake-oriented input types (for example `github`, `gitlab`, `path`) and URL-like references (for example `github:owner/repo/rev`) still require the **`flakes`** feature in addition to `fetch-tree`. Verified on Nix 2.34.8: `type = "github"` fails with `flakes` disabled even when `fetch-tree` is on.

**`git-hashing`.** When enabled, Nix may create content-addressed store objects using Git's hashing algorithm. Those objects are not understandable by older Nix versions. This is separate from choosing the `git` backend in `fetchTree` or `fetchGit`; it affects how certain store paths are named and verified. Stabilisation: [git-hashing tracking issue](https://github.com/NixOS/nix/milestone/41).

**`verified-fetches`.** Enables Git commit signature verification through `builtins.fetchGit` via `verifyCommit` and `publicKey` / `publicKeys`. Requires explicit opt-in; without the flag, those attributes are unavailable. Verification constraints (for example, no uncommitted local changes when `verifyCommit` is set) are described in the manual's `fetchGit` entry. Stabilisation: [verified-fetches tracking issue](https://github.com/NixOS/nix/milestone/48).

**Stabilization.** `fetch-tree` was split out from the `flakes` flag so the fetch interface could be exercised independently. Track broader experimental status in [Tracking Stabilization](tracking-stabilization.md); per-flag: [fetch-tree tracking issue](https://github.com/NixOS/nix/milestone/31).

## Examples

**Try `fetchTree` without full flakes** — enable only the fetcher (Nix 2.34.x):

```ini
extra-experimental-features = fetch-tree
```

**Flakes implies `fetch-tree`** — no need to list both:

```ini
experimental-features = nix-command flakes
```

**`fetchTree` with an explicit type** (requires `fetch-tree` only; `tarball` / `git` / `file` backends):

```nix
# Verified shape: type + url; network fetch on first eval
builtins.fetchTree {
  type = "tarball";
  url = "https://github.com/NixOS/patchelf/archive/0.18.0.tar.gz";
}
```

On Nix 2.34.8 with only `fetch-tree`, that evaluates to an attrset with `outPath` and `narHash`. A `git` form needs `url` (and usually `rev`); see the builtins manual for the full schema.

**Flake-style types need `flakes`** (Nix 2.34.8):

```text
error: experimental Nix feature 'flakes' is disabled; add '--extra-experimental-features flakes' to enable it
```

**Locked flake input as fetch args** — after `nix flake lock`, a node's `locked` block in `flake.lock` is what Nix feeds to `fetchTree` at evaluation time; see [Lockfile](../07-flakes/anatomy/lockfile.md).

## References

- [Nix manual — Experimental features (`fetch-tree`, 2.34)](https://nix.dev/manual/nix/2.34/development/experimental-features.html#xp-feature-fetch-tree) — version-stamped flag entry
- [Nix manual — Experimental features](https://nix.dev/manual/nix/stable/development/experimental-features.html) — `fetch-tree`, `git-hashing`, `verified-fetches`, and flakes overlap
- [Nix manual — Built-ins (`fetchTree`, `fetchGit`)](https://nix.dev/manual/nix/2.34/language/builtins.html) — argument shapes and source types
- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — `locked` inputs as `fetchTree` arguments
- [fetch-tree tracking issue](https://github.com/NixOS/nix/milestone/31) — stabilisation milestone
- [git-hashing tracking issue](https://github.com/NixOS/nix/milestone/41)
- [verified-fetches tracking issue](https://github.com/NixOS/nix/milestone/48)

## See also

- [Feature Flags Overview](feature-flags-overview.md) — enabling experimental features
- [flakes](flakes.md) — flake format flag (always enables `fetch-tree`)
- [Flake](../02-concepts/flake.md) — flake concept and lockfile role
- [Lockfile](../07-flakes/anatomy/lockfile.md) — `locked` fetch arguments
- [Import and Fetch](../03-language/builtins/import-and-fetch.md) — `fetchGit`, `fetchTree`, and related builtins
- [Tracking Stabilization](tracking-stabilization.md) — stabilization status in this wiki
