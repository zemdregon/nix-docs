---
status: complete
---

# Registries and Refs

## Overview

A **flake reference** (flakeref) tells Nix which flake to fetch and, optionally, which output to use. References can be written as URL-like strings (`github:NixOS/nixpkgs`, `path:./.`, `git+https://…`) or as attribute sets with a `type` field. **Indirect** references such as `nixpkgs` or `nixpkgs/nixos-unstable` do not name a fetch URL directly—they are resolved through a **flake registry**, a JSON map from symbolic ids to concrete flake locations.

Registries make CLI workflows ergonomic (`nix run nixpkgs#hello`) without hard-coding GitHub URLs everywhere. They are separate from [inputs and lockfile](anatomy/inputs-and-outputs.md) resolution inside your own `flake.nix`: understanding that split is central to using flakes correctly.

Flake references and `nix registry` require the experimental **`flakes`** (and usually **`nix-command`**) features. As of the Nix **2.34.x** stable manual, both remain experimental—syntax and subcommands can change.

## Details

**Flakeref forms.** Most CLI and `flake.nix` input URLs use the string form. Supported **types** include `indirect`, `path`, `git`, `mercurial`, `tarball`, `file`, `github`, `gitlab`, and `sourcehut`. A GitHub shorthand looks like `github:NixOS/nixpkgs/nixos-26.05`; a local tree is `path:./my-flake` or `./relative` (relative paths must start with `./` to avoid registry lookup). The attribute-set form mirrors the same fields (`type`, `owner`, `repo`, `ref`, `rev`, …) and is what Nix stores internally after parsing.

**Output selection.** Append `#attrPath` to choose an output without opening the flake: `nix build nixpkgs#hello` builds the `hello` package from the registry-resolved Nixpkgs flake. The part before `#` is the flakeref; the part after is a dotted attribute path inside that flake's outputs.

**Indirect refs and registries.** Strings like `nixpkgs` or `nixpkgs/nixos-unstable` have type `indirect`. Nix looks them up in registries to obtain a concrete ref (usually a `github:` URL). If no registry entry matches, resolution fails unless you pass a full URL.

**Registry layers and precedence.** Registries stack; later layers override earlier ones (low → high):

1. **Global** — from the `flake-registry` setting (default `https://channels.nixos.org/flake-registry.json`). Downloaded and cached; refresh interval follows `tarball-ttl`.
2. **System** — `/etc/nix/registry.json`, or on NixOS `nix.registry` in configuration.
3. **User** — `~/.config/nix/registry.json`.
4. **CLI** — `nix --override-flake id=url …` for one-shot overrides.

**CLI vs in-flake resolution.** System and user registries apply when you pass a flakeref on the **command line** only. References inside `flake.nix` inputs do **not** use system or user registries—they resolve via the global registry (and then the [lockfile](anatomy/lockfile.md) once locked). Pin dependencies explicitly in `flake.nix` URLs or `flake.lock`; do not assume a `nix registry pin` on your laptop affects collaborators' builds.

**Registry file format.** Registry JSON is **version 2**. The `flakes` array lists `{ "from": …, "to": … }` pairs, each side a flakeref. A registry entry matches when its `from` attributes equal those of the request. Unification then takes `to` and applies any `rev` / `ref` from the request—so `nixpkgs/nixos-26.05` against a `github:NixOS/nixpkgs` `to` becomes `github:NixOS/nixpkgs/nixos-26.05`. If the request has no `ref`/`rev`, a pinned `to` (as after `nix registry pin`) supplies the concrete revision.

**Managing registries.** The `nix registry` subcommands cover day-to-day use:

- `nix registry list` — show effective entries after merging layers.
- `nix registry add <id> <url>` — add a user-registry mapping.
- `nix registry pin <id>` — record the currently resolved flake ref for `<id>` in the user registry (useful after `nix flake update`-style bumps for CLI convenience).
- `nix registry remove <id>` — drop a user entry.
- `nix registry resolve <ref>` — print the concrete ref after registry lookup.

**Path refs.** Directory paths must be relative (`./foo`) or absolute. A path inside a Git work tree is fetched with **git+file** semantics; uncommitted changes may produce warnings because the tree is not a fixed revision. Prefer locked Git inputs in `flake.nix` when reproducibility matters.

## Examples

**Registry id vs explicit URL** — both reach Nixpkgs, but only the id goes through your registry stack:

```bash
nix run nixpkgs#hello
nix run github:NixOS/nixpkgs/nixos-26.05#hello
```

**Pin a CLI alias** — after resolving `nixpkgs` to a concrete Git revision, store it in the user registry so later commands stay on that pin (local CLI only; commit [lockfile](anatomy/lockfile.md) pins for project reproducibility):

```bash
nix registry pin nixpkgs
nix registry list
```

**Inspect resolution:**

```bash
nix registry resolve nixpkgs
```

**Minimal user registry entry** (`~/.config/nix/registry.json`):

```json
{
  "version": 2,
  "flakes": [
    {
      "from": { "id": "my-org", "type": "indirect" },
      "to": { "owner": "my-org", "repo": "flakes", "type": "github" }
    }
  ]
}
```

## References

- [Nix manual — flakes and flake references](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — flakeref syntax, types, and `#output` selection (Nix 2.34.x; experimental)
- [Nix manual — `nix registry`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-registry.html) — registry format, precedence, and subcommands (experimental)
- [nix.conf — `flake-registry`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-flake-registry) — default global registry URL
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — how registries fit into the flake model

## See also

- [Flake (concept)](../02-concepts/flake.md) — entry point, inputs, outputs, and registry vocabulary
- [Inputs and outputs](anatomy/inputs-and-outputs.md) — declaring dependencies in `flake.nix`
- [Lockfile](anatomy/lockfile.md) — pinning inputs for reproducible evaluation
- [Channel](../02-concepts/channel.md) — classic nixpkgs distribution; global registry partly mirrors channel URLs
- [Migration from channels](migration-from-channels.md) — moving from `nix-channel` to flakes and registries
- [Pure eval and impure](pure-eval-and-impure.md) — evaluation restrictions for flake commands
