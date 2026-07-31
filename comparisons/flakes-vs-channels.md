---
status: complete
---

# Flakes vs Channels

## Overview

[Channels](../02-concepts/channel.md) and [flakes](../02-concepts/flake.md) are two ways to supply Nixpkgs (and other expression trees) to evaluation. Channels are the classic model: subscribe with [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md), resolve packages through `NIX_PATH` / `<nixpkgs>`, and advance with `nix-channel --update`. Flakes declare dependencies as **inputs** in `flake.nix`, pin them in [`flake.lock`](../07-flakes/anatomy/lockfile.md), and address projects with **flake references** (`github:…`, `.`, registry names). Flake evaluation defaults to **pure** mode.

Neither has fully replaced the other. Channels remain common for ad hoc shells and older NixOS installs; flakes are the usual choice for new reproducible projects. See [Migration from Channels](../07-flakes/migration-from-channels.md) for the practical switch.

## Details

| Concern | Channels | Flakes |
| --- | --- | --- |
| How you point at nixpkgs | Named subscription + URL (`nix-channel --add`) | Input URL / flakeref in `flake.nix` |
| Where the pin lives | External: channel profile generations, `NIX_PATH` | In-repo: `flake.lock` (commit with the project) |
| Update command | `nix-channel --update` | `nix flake update` (or targeted input update) |
| Lookup style | `<nixpkgs>`, `-I`, env / config search path | Explicit inputs; CLI flakerefs (`nixpkgs#hello`, `.#pkg`) |
| Evaluation | Impure by default (paths, env, channel state) | Pure by default (declared inputs only) |
| Feature status | Stable classic CLI | Experimental (`flakes` + usually `nix-command`) |

**Channels: moving snapshots outside the expression.** A channel URL identifies a release *line* (for example `https://channels.nixos.org/nixpkgs-unstable`), not a single Git commit. After `--update`, tools find the downloaded tree via `NIX_PATH` or the default channels layout. The Nix manual notes that subscribed-channel state is **external** to the expressions that depend on it, which limits reproducibility: two machines that update on different days can evaluate different revisions under the same channel name. Rollback uses channel **generations** (`nix-channel --rollback`), not a project lockfile. Concept: [Channel](../02-concepts/channel.md); CLI: [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md).

**Flakes: lockfile, flakerefs, and pure eval.** `flake.nix` lists inputs; the first flake command writes `flake.lock` with concrete revisions and content hashes. Collaborators and CI share that graph when the lockfile is committed. Flake commands take **flakerefs** such as `.`, `github:NixOS/nixpkgs/nixos-26.05`, or a registry alias like `nixpkgs#hello`. Pure evaluation blocks undeclared filesystem and environment access, which makes “what went into this build?” auditable. Flakes remain experimental (requires enabling the feature; see [experimental `flakes`](../08-experimental-features/flakes.md)). Concept: [Flake](../02-concepts/flake.md); CLI: [`nix flake`](../05-cli-and-tooling/modern-cli/nix-flake.md).

**Registry flakeref ≠ channel.** `nix run nixpkgs#hello` resolves through the [flake registry](../07-flakes/registries-and-refs.md), not through `nix-channel --update`. For a **project**, locked inputs in `flake.lock` are the source of truth; the registry is CLI convenience and can move independently of any given repo’s pins.

**Both still used.** A machine can keep channel subscriptions for legacy `nix-shell` / `nix-env` workflows while a repository builds exclusively from locked flake inputs. Channel updates then no longer define that project’s nixpkgs revision—the lockfile does. Thin wrappers, `flake-compat`, or non-flake pin tools (for example npins) are options when full flake adoption is blocked; the migration guide covers the primary flake path.

**Migration in brief.** Enable `experimental-features = nix-command flakes`, add `flake.nix` with pinned inputs, generate and commit `flake.lock`, move configuration into flake outputs (`nixosConfigurations`, `packages`, …), replace `import <nixpkgs>` with the realized input, and switch rebuilds to `--flake`. Step-by-step: [Migration from Channels](../07-flakes/migration-from-channels.md).

## Examples

**Channel workflow** — subscribe, update, resolve via search path:

```bash
nix-channel --add https://channels.nixos.org/nixpkgs-unstable nixpkgs
nix-channel --update
nix-shell -p hello --run hello
# or: nix-instantiate --eval '<nixpkgs>' -A lib.version
```

**Flake workflow** — locked input + flakeref (no channel required for this build):

```nix
# flake.nix (fragment)
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default =
      nixpkgs.legacyPackages.x86_64-linux.hello;
  };
}
```

```bash
nix build .#default          # uses flake.lock pins
nix run nixpkgs#hello        # registry flakeref (not the same as a channel update)
```

**Coexistence.** Keep `nix-channel` for personal ad hoc packages; pin the project with `flake.lock` and bump only via `nix flake update` when you intend to change revisions.

## References

- [nix.dev — Flakes](https://nix.dev/concepts/flakes) — inputs, lockfile, pure eval, flakerefs
- [Nix manual — `nix-channel`](https://nix.dev/manual/nix/stable/command-ref/nix-channel.html) — subscribe, update, rollback; `NIX_PATH` and external state note
- [Nix manual — channels layout](https://nix.dev/manual/nix/stable/command-ref/files/channels.html) — on-disk channel profiles
- [Official NixOS channels](https://channels.nixos.org/) — stable and unstable channel URLs

## See also

- [Channel](../02-concepts/channel.md) — classic distribution model
- [Flake (concept)](../02-concepts/flake.md) — inputs, outputs, experimental status
- [`nix-channel`](../05-cli-and-tooling/classic-cli/nix-channel.md) — classic channel CLI
- [`nix flake`](../05-cli-and-tooling/modern-cli/nix-flake.md) — modern flake CLI
- [Experimental flakes](../08-experimental-features/flakes.md) — feature flag and status
- [Lockfile](../07-flakes/anatomy/lockfile.md) — `flake.lock` structure and updates
- [Migration from Channels](../07-flakes/migration-from-channels.md) — enable flakes, replace `<nixpkgs>`, switch rebuild commands
- [Pure eval and impure](../07-flakes/pure-eval-and-impure.md) — flake purity defaults and escape hatches
- [Registries and refs](../07-flakes/registries-and-refs.md) — flakerefs and the flake registry
