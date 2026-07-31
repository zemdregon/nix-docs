---
status: complete
---

# flake.nix Schema

## Overview

Every [flake](../../02-concepts/flake.md) is a filesystem tree whose root contains **`flake.nix`**: a Nix attribute set declaring metadata, **inputs** (dependencies on other flakes or sources), and **outputs** (what this flake provides). The file is the contract Nix reads when you run `nix build .`, `nix flake show`, or similar commands.

This page documents the **top-level attributes** of `flake.nix`. Input wiring, output conventions, and lockfile interaction are expanded in sibling pages; the high-level concept stays in [Flake (concept)](../../02-concepts/flake.md).

## Details

**Supported top-level attributes.** Nix recognizes four keys in `flake.nix`:

| Attribute | Typical | Role |
|-----------|---------|------|
| `description` | optional | Short one-line summary (shown by `nix flake metadata` and registries). |
| `inputs` | optional | Attrset of named dependencies; each value is a flake reference or nested override. Names listed only as `outputs` arguments become indirect (registry) inputs. |
| `outputs` | required | Function from realized inputs → attrset of values this flake exports. |
| `nixConfig` | optional | Subset of `nix.conf` options applied while evaluating the flake. |

Flakes require the experimental `flakes` feature (Nix ≥ 2.4); see [flakes (experimental feature)](../../08-experimental-features/flakes.md).

**`outputs` arguments.** The function receives one argument per entry in `inputs`, keyed by name. Each argument is that input's **outputs** plus fetch metadata:

- `outPath` — store path of the input's source tree (usable with `import`, as in `import nixpkgs { … }`)
- `rev`, `revCount` — Git commit and ancestor count when applicable (`revCount` is absent for `github:` tarball fetches)
- `lastModifiedDate`, `lastModified` — commit timestamp as `%Y%m%d%H%M%S` string or Unix seconds
- `narHash` — SRI hash of the input's NAR serialization

The special input **`self`** refers to this flake's own outputs and source tree. A typical signature is `outputs = { self, nixpkgs }: { … };`.

**Return shape.** `outputs` must return an attribute set. Attribute names are otherwise free, but Nix CLI commands expect **conventional** layouts — for example `packages.<system>.<name>` as derivations, or `devShells.<system>.default` for shells. See [Packages, apps, and devShells](../workflows/packages-apps-devShells.md) for those patterns.

**`nixConfig`.** When present, listed options are set during flake evaluation. For security, options outside a small allowlist require user confirmation unless `accept-flake-config` is enabled globally. Without confirmation, only these may be set: `bash-prompt`, `bash-prompt-prefix`, `bash-prompt-suffix`, `flake-registry`, and `commit-lock-file-summary`.

**Self-attributes (`inputs.self`).** A flake can declare how *it* is fetched when used as someone else's input:

- `inputs.self.submodules = true` — fetch Git submodules automatically
- `inputs.self.lfs = true` — fetch Git LFS objects automatically

Defaults for both are `false`. Consumers need not add `?submodules=1` or LFS flags to flake references when these are set.

Input syntax, transitive overrides, and `follows` are not repeated here; see [Inputs and outputs](inputs-and-outputs.md), [Follow and overrides](follow-and-overrides.md), and [Lockfile](lockfile.md).

## Examples

Minimal flake: one `nixpkgs` input and a default package built from `legacyPackages`:

```nix
{
  description = "Hello from a minimal flake";

  # Use a current nixos-YY.MM release branch (example: 26.05 as of mid-2026).
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default =
      nixpkgs.legacyPackages.x86_64-linux.hello;
  };
}
```

After the first evaluation, Nix writes [flake.lock](lockfile.md) pinning `nixpkgs` to an exact revision. The `outputs` function can read `nixpkgs.rev` or `nixpkgs.lastModified` when generating version strings.

Optional `nixConfig` for dev-shell UX (allowed without `accept-flake-config`):

```nix
{
  nixConfig.bash-prompt = "[myflake] \\u@\\h:\\w\\$ ";
  # … description, inputs, outputs …
}
```

## References

- [Nix manual — `nix flake` (Flake format)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — top-level attributes, inputs, outputs, `nixConfig`, self-attributes
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — overview and motivation
- [RFC 49 — Flakes](https://github.com/NixOS/rfcs/pull/49) — original design specification

## See also

- [Flake (concept)](../../02-concepts/flake.md) — vocabulary and reproducibility model
- [Inputs and outputs](inputs-and-outputs.md) — wiring dependencies and export shapes
- [Lockfile](lockfile.md) — pins produced from `inputs`
- [Follow and overrides](follow-and-overrides.md) — deduplicating and overriding transitive inputs
- [Packages, apps, and devShells](../workflows/packages-apps-devShells.md) — conventional `outputs` layouts
- [flakes (experimental feature)](../../08-experimental-features/flakes.md) — enabling flakes in `nix.conf`
