---
status: complete
---

# follows and Overrides

## Overview

Flake **inputs** can depend on other flakes, which in turn declare their own inputs. By default, Nix resolves those **transitive** inputs from each dependency's [lockfile](lockfile.md) when generating or updating the lock graph. That can pull in duplicate versions of `nixpkgs` or leave indirect pins stale.

Two mechanisms in `flake.nix` let the root flake control transitive inputs: **overrides** (replace a dependency's input with a new source) and **`follows`** (reuse an input already declared elsewhere in the graph). Together they deduplicate inputs and align versions with the top-level flake. Flakes and `nix flake` remain **experimental** (`flakes` + `nix-command`). See [Inputs and outputs](inputs-and-outputs.md) for how inputs are declared and passed to `outputs`.

## Details

**Default transitive resolution.** When Nix builds the dependency graph for [flake.lock](lockfile.md), it consults lock files of direct inputs unless you override or follow. Unchanged transitive pins can lag behind what those inputs would fetch today, and the same library (especially `nixpkgs`) may appear at more than one revision.

**Overrides.** Assign under the transitive path in `inputs`:

```nix
inputs.nixops.inputs.nixpkgs = {
  type = "github";
  owner = "my-org";
  repo = "nixpkgs";
};
```

URL-style assignments work the same way as for direct inputs (see [flake.nix schema](flake-nix-schema.md)). An override replaces that input for the named direct dependency only.

**`follows`.** Instead of a new fetch, inherit another input from the root flake's graph:

```nix
inputs.nixpkgs.follows = "dwarffs/nixpkgs";
```

The value is a `/`-separated path of input names starting from the root flake—not a URL. Overrides and `follows` combine: `inputs.nixops.inputs.nixpkgs.follows = "dwarffs/nixpkgs"` makes `nixops`'s `nixpkgs` the same node as `dwarffs`'s `nixpkgs`.

**When deduplicating `nixpkgs` matters.** Forcing every transitive `nixpkgs` to match the root is a common goal, but often low impact: many flakes expose [overlays](../../02-concepts/overlay.md) or NixOS modules composed into *your* `nixpkgs`, so their private `nixpkgs` input may never affect evaluation. Eliminating duplicates still shrinks the lock graph and avoids subtle version skew when a dependency does evaluate against its own pin.

**Circular flakes.** Two flakes that depend on each other need a single shared instance of each side. An empty `follows` path means "follow the root flake":

```nix
inputs.b.inputs.a.follows = "";
```

Each side points the other's input at itself so Nix does not fetch two copies.

**Downstream `follows`.** If a library flake does not expose `follows` hooks for all of its recursive inputs, consumers cannot redirect those transitive pins from their own `flake.nix`. Library authors who expect `follows` from downstream should document or declare the inputs that can be followed.

## Examples

**Home Manager uses top-level nixpkgs** (from [nix.dev — Flakes](https://nix.dev/concepts/flakes)):

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
}
```

After changing overrides or `follows`, run a flake command (e.g. `nix flake lock`) so [flake.lock](lockfile.md) reflects the new graph.

**Mutual dependency** (each flake is the other's input; simplified):

```nix
# flake A
{
  inputs.b.url = "...";
  inputs.b.inputs.a.follows = "";
  outputs = { self, b }: { /* ... */ };
}
```

```nix
# flake B
{
  inputs.a.url = "...";
  inputs.a.inputs.b.follows = "";
  outputs = { self, a }: { /* ... */ };
}
```

## References

- [Nix manual — flakes and `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — transitive overrides, `follows`, circular lock graphs (experimental; verified 2026-07)
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — dependency management and home-manager `follows` example

## See also

- [Flake (concept)](../../02-concepts/flake.md) — inputs, lockfile, and vocabulary
- [Inputs and outputs](inputs-and-outputs.md) — declaring direct inputs and `outputs`
- [Lockfile](lockfile.md) — how transitive nodes are recorded
- [flake.nix schema](flake-nix-schema.md) — input attribute shapes
- [Migration from channels](../migration-from-channels.md) — moving explicit pins off channels
