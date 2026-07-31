---
status: complete
---

# Lockfile

## Overview

**`flake.lock`** is a UTF-8 JSON file Nix generates beside [flake.nix](flake-nix-schema.md) to pin [inputs](inputs-and-outputs.md) to exact revisions. Declarations in `flake.nix` are often unlocked—branch names, tags, or indirect references—so without a lockfile two checkouts can resolve different commits. With a committed lockfile, every machine evaluates against the same `rev` / `narHash` graph: that is the main reproducibility win over [channels](../../02-concepts/channel.md).

Flake lock commands require the experimental `flakes` (and usually `nix-command`) features; interfaces may still change.

## Details

**Graph shape.** The lockfile mirrors the flake dependency graph. Top-level fields are `version` (lock format version), `root` (label of the root node), and `nodes` (a map from labels to node records). Labels are arbitrary (e.g. `n1`); `root` names which node is the current flake.

**Non-root nodes.** Each dependency node typically contains:

- **`inputs`** — maps input names to other node labels (the edges of the graph).
- **`original`** — the fetch arguments as written in the upstream `flake.nix` (e.g. a Git URL and ref), as `builtins.fetchTree` arguments.
- **`locked`** — the resolved fetch arguments Nix actually uses: concrete `rev`, `narHash`, `lastModified`, and related metadata for Git, tarballs, or other fetchers.
- **`flake`** (optional) — whether the source is treated as a flake (corresponds to `flake = false` in inputs).

The **`locked`** attributes are final: they are what Nix passes into `outputs` when evaluating the flake. **`narHash`** (SRI SHA-256 of the NAR serialization of the tree) lets Nix compute the store path and substitute from a binary cache without re-fetching.

**Root node.** The root entry lists its `inputs` but omits `original` and `locked`. Locking the root flake would change whenever the lockfile is written, so the root is not pinned against itself.

**Eval vs lock generation.** Once `flake.lock` exists and matches `flake.nix`, Nix does not consult dependency lockfiles at evaluation time—it uses only this flake’s lock (transitively pinning direct and indirect inputs). When *generating* or updating the lockfile, Nix does consult those dependency locks by default to pick compatible revisions.

**Updating pins.** `nix flake lock` creates missing lock entries without bumping existing pins. `nix flake update` (optionally with input names, e.g. `nix flake update nixpkgs`) refreshes selected inputs to newer revisions and rewrites the lockfile; with no names it updates all inputs. After intentional bumps, commit the updated lock so everyone stays aligned. Both commands accept `--commit-lock-file` to commit the change automatically.

**Circular dependencies.** Cycles in the input graph are possible when inputs use `follows` to alias another input; see [Follow and overrides](follow-and-overrides.md) for how that appears in the lock.

## Examples

**Create missing pins (does not bump existing ones):**

```bash
nix flake lock
git add flake.lock
git commit -m "Add flake.lock"
```

**Single locked node (illustrative shape):**

```json
"nodes": {
  "nixpkgs": {
    "locked": {
      "owner": "NixOS",
      "repo": "nixpkgs",
      "rev": "abc123def456",
      "type": "github",
      "lastModified": 1700000000,
      "narHash": "sha256-…"
    },
    "original": {
      "owner": "NixOS",
      "repo": "nixpkgs",
      "ref": "nixos-26.05",
      "type": "github"
    }
  }
}
```

**Bump one input and share the pin:**

```bash
nix flake update nixpkgs
git add flake.lock
git commit -m "Bump nixpkgs pin"
```

Team members and CI then evaluate against the same `nixpkgs` revision and `narHash` without re-resolving branches.

## References

- [Nix manual — `nix flake` (lock files)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — lockfile format and semantics
- [Nix manual — `nix flake lock`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-lock.html) — create missing lock entries
- [Nix manual — `nix flake update`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-update.html) — updating input pins
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — high-level introduction

## See also

- [Flake (concept)](../../02-concepts/flake.md) — what flakes are and why locking matters
- [Flake.nix schema](flake-nix-schema.md) — input declarations that the lock resolves
- [Inputs and outputs](inputs-and-outputs.md) — how realized inputs reach `outputs`
- [Follow and overrides](follow-and-overrides.md) — `follows`, overrides, and lock graph cycles
- [Migration from channels](../migration-from-channels.md) — replacing channel pins with a committed lockfile
