---
status: complete
---

# Inputs and Outputs

## Overview

A flake's **`inputs`** block names the dependencies this flake needs—other flakes, Git repos, or tarballs. The **`outputs`** function receives those dependencies (plus metadata) and returns what the flake provides: packages, apps, dev shells, NixOS configurations, modules, and arbitrary Nix values. Together they are the wiring layer between `flake.nix` and everything the Nix CLI can build, run, or develop against.

Inputs are declared in `flake.nix` and pinned in [lockfile.md](lockfile.md); outputs are evaluated only after inputs are fetched and locked. For the full top-level schema, see [flake-nix-schema.md](flake-nix-schema.md).

Flakes require the experimental `flakes` feature (Nix ≥ 2.4), typically alongside `nix-command`. Enable for one command with `--experimental-features 'nix-command flakes'`, or permanently via `nix.settings.experimental-features` (NixOS / Home Manager). See [flakes (experimental feature)](../../08-experimental-features/flakes.md).

## Details

### Declaring inputs

The `inputs` attribute maps **names** to **flake references**. Common forms:

- **URL-like:** `inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";`
- **Structured:** an attrset with `type`, `owner`, `repo`, and optionally `ref` or `rev` (equivalent to the URL forms the CLI accepts).

Each name becomes an argument to `outputs`. Input references resolve through [../registries-and-refs.md](../registries-and-refs.md) and are recorded in the lockfile on first evaluation.

### `follows` (composition)

An input can reuse another input already in the graph instead of fetching its own copy:

```nix
inputs.home-manager.inputs.nixpkgs.follows = "nixpkgs";
```

That deduplicates transitive dependencies (especially `nixpkgs`). Overrides and deeper `follows` paths are covered in [follow-and-overrides.md](follow-and-overrides.md).

### Indirect inputs

If a name appears in the `outputs` function arguments but **not** in `inputs`, Nix treats it as an **indirect** input: `type = "indirect"; id = "<name>"`, looked up in the flake registry. A bare `nixpkgs` parameter with no matching `inputs.nixpkgs` entry behaves like registry `nixpkgs`. Prefer explicit `inputs` for reproducibility; indirect inputs are convenient for quick experiments but depend on registry defaults.

### The `self` input

**`self`** is a special input: the current flake's own outputs plus its source tree. Use it when outputs need to refer to other outputs from the same flake (for example, a check that builds `self.packages.${system}.default`) or when passing this flake's path into a downstream function.

### Non-flake inputs (`flake = false`)

Some dependencies are source trees, not flakes. Set `flake = false` on an input so Nix fetches the repo or archive but does **not** expect flake outputs. The value passed to `outputs` is then a store path / source tree (usable as `src` in a derivation), not an attrset of flake outputs. Typical for vendored application source, firmware blobs, or legacy repos without `flake.nix`.

### What `outputs` receives

For each declared input name, Nix passes an **attrset** containing that input's flake outputs (when `flake = true`) **plus metadata**: `outPath`, `rev`, `narHash`, `lastModified`, `lastModifiedDate`, and related fields (`revCount` when available; absent for `github:` tarball fetches). Your `outputs` function can destructure `{ self, nixpkgs, ... }` and use both `nixpkgs.legacyPackages.${system}` and `nixpkgs.rev` in the same body.

### Conventional output attributes

`outputs` is a function of the realized inputs and must return an attribute set. The Nix CLI recognizes several top-level keys:

| Output key | Typical CLI use |
|------------|-----------------|
| `packages.<system>.<name>` | `nix build`, `nix build .#name` |
| `apps.<system>.<name>` | `nix run` |
| `devShells.<system>.<name>` | `nix develop` |
| `checks.<system>.<name>` | `nix flake check` |
| `nixosConfigurations.<name>` | `nixos-rebuild`; or `nix build .#nixosConfigurations.<name>.config.system.build.toplevel` |
| `overlays`, `nixosModules`, `templates` | consumed by other flakes or modules |

Additional top-level attributes are allowed; the CLI simply will not special-case them. You might expose `formatter`, `legacyPackages`, or domain-specific attrsets for other flakes to import.

By convention, **`packages.<system>.default`** is the implicit target of `nix build` and `nix build .#default` when no output name is given. Other systems and names are addressed explicitly: `.#packages.x86_64-linux.hello`. Deep workflows for packages, apps, and shells live under [../workflows/packages-apps-devShells.md](../workflows/packages-apps-devShells.md).

## Examples

Minimal flake: one GitHub flake input, a default package, and a non-flake source used as `src`:

```nix
{
  description = "Example wiring inputs to outputs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    my-app = {
      url = "github:owner/my-app";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, my-app }: {
    packages.x86_64-linux.default =
      nixpkgs.legacyPackages.x86_64-linux.stdenv.mkDerivation {
        pname = "my-app";
        version = "0.1.0";
        src = my-app; # flake = false → store path, not flake outputs
      };
  };
}
```

Here `nixpkgs` is a full flake input (`legacyPackages` and other outputs on the attrset), while `my-app` is only a pinned source tree. After the first evaluation, [flake.lock](lockfile.md) pins both revisions.

## References

- [Nix manual — flakes and `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — input types, output schema, lock file interaction
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — inputs, outputs, reproducibility; experimental since Nix 2.4

## See also

- [flake.nix Schema](flake-nix-schema.md) — required top-level attributes
- [Lockfile](lockfile.md) — how inputs are pinned
- [follows and Overrides](follow-and-overrides.md) — deduplicating and overriding inputs
- [Flake (concept)](../../02-concepts/flake.md) — vocabulary and motivation
- [flakes (experimental feature)](../../08-experimental-features/flakes.md) — enabling `flakes` / `nix-command`
- [Packages, Apps, devShells](../workflows/packages-apps-devShells.md) — defining CLI-facing outputs
- [Registries and References](../registries-and-refs.md) — indirect inputs and flake refs
