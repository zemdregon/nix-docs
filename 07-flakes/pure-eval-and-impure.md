---
status: complete
---

# Pure Eval and Impure

## Overview

**Flake commands evaluate in pure mode by default.** The result of a flake evaluation is fully determined by declared inputs—locked in [flake.lock](anatomy/lockfile.md)—not by ambient filesystem state, environment variables, or `NIX_PATH`. That hermetic eval plays well with caching and makes “what went into this build?” auditable.

This page is the flake-focused deep dive. The [Flake](../02-concepts/flake.md) concept page summarizes the idea; language-level rules live in [purity boundaries](../03-language/semantics/purity-boundaries.md). When something fails under pure eval, prefer fixing the root cause—declare an [input](anatomy/inputs-and-outputs.md), keep paths inside the flake tree, pin a fetch with a hash, pass `system` explicitly—over permanently relying on `--impure`.

Verified against Nix **2.34.x** (CLI `2.34.8` / stable manual). Flake installables and `nix flake` / `nix eval` require the experimental [`flakes`](../08-experimental-features/flakes.md) and [`nix-command`](../08-experimental-features/nix-command.md) features; flags and defaults can still change until those features stabilize.

## Details

### Pure vs impure (flake boundary)

| Concern | Pure flake eval (default) | With `--impure` |
|---------|---------------------------|-----------------|
| Declared flake inputs + lockfile | Allowed | Allowed |
| Paths inside the flake source tree | Allowed (see Git note below) | Allowed |
| Absolute host paths, `~/…`, paths outside the tree | Rejected | Allowed (mutable) |
| `builtins.currentSystem` / `currentTime` / `nixPath` / `storePath` | Disabled (attribute missing / pure-mode error) | Available |
| `builtins.getEnv` | Returns `""` | Real environment |
| `<nixpkgs>` / `NIX_PATH` | Not used for flake deps; angle-bracket lookups fail | Usable (e.g. with `--expr`) |
| Unpinned fetches / unlocked `getFlake` | Rejected | Allowed |

Global `nix.conf` defaults `pure-eval` to `false`, but **flake-based installables turn pure evaluation on** for the flake evaluation path. Non-flake workflows can opt in with `nix eval --pure-eval` or `pure-eval = true` in config. The CLI documents `--impure` as allowing access to **mutable paths and repositories**.

`--file` / `-f` **implies `--impure`**, because the file path itself is a mutable reference.

### What pure evaluation restricts

Pure evaluation mode (`pure-eval` in `nix.conf`) ensures expressions depend only on **explicitly declared inputs**, not on undeclared external state. When active, Nix generally:

- **Restricts** filesystem and network access to content pinned by cryptographic hash (store paths, hash-pinned fetches, locked flake inputs) and to the flake’s own source tree.
- **Disables impure constants:** `builtins.currentSystem`, `builtins.currentTime`, `builtins.nixPath`, and `builtins.storePath` (see the [`pure-eval`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-pure-eval) entry). Accessing those attributes fails with “attribute … missing” (or an equivalent pure-mode error for `storePath`).
- **Neutralizes ambient env reads:** `builtins.getEnv` returns the empty string rather than the process environment.
- **Rejects** home-directory path literals (`~/…` — including under `~/.config/…`), absolute host paths outside allowed inputs, and angle-bracket lookups like `<nixpkgs>` that depend on `NIX_PATH`.

Typical error wording (Nix 2.34.x): `access to absolute path '…' is forbidden in pure evaluation mode (use '--impure' to override)`, or `the path '~/.config/…' can not be resolved in pure mode`.

### Relative paths and the flake tree

Under flakes, a bare path installable (`.`, `./subdir`) is copied into the store as a `git+file:` or `path:` input before evaluation. Relative path literals that stay **inside** that tree (for example `./modules/foo.nix`, `builtins.readFile ./data.txt`) are fine. Paths that escape the tree (`../outside`, absolute `/home/…`, or `~/…`) are impure and fail unless you pass `--impure`.

Prefer path **literals** over string interpolation of paths. Antiquoting a subdirectory (e.g. `"${./host}/file.nix"`) copies only that subdirectory into the store; a later `../` import then leaves the allowed tree and triggers the same pure-eval path error. Keep modules as path values, or anchor with `self` / flake inputs—see [flake.nix schema](anatomy/flake-nix-schema.md).

### Flakes vs classic impurity

Classic channel workflows resolve dependencies through `NIX_PATH` and impure imports:

```nix
import <nixpkgs> {}
```

Flakes **ignore `NIX_PATH`** for dependency resolution. Dependencies must appear in the flake’s `inputs` block and be pinned in the lockfile—see [inputs and outputs](anatomy/inputs-and-outputs.md) and [migration from channels](migration-from-channels.md). Symbolic names like `nixpkgs#hello` use the [flake registry](registries-and-refs.md), not `<nixpkgs>` search paths.

### Git flakes and the source tree

For a path inside a Git repo, Nix treats the flake as a `git+file:` input and copies only files **indexed by Git** (committed or `git add`-ed). Untracked files and paths matched by `.gitignore` are invisible to evaluation—a common gotcha when a new file exists on disk but was never staged. Stage or commit files you need the flake to see before building.

To include the working tree as a plain directory (including untracked files), use an explicit `path:…` flake reference instead of a bare path. That changes how the source is copied; it does not by itself relax pure-eval rules for builtins or `NIX_PATH`.

### Fetches and fixed-output derivations

At **evaluation** time, unpinned network fetches (`fetchTarball` without a hash, unlocked `fetchGit`, and similar) are rejected under pure eval. Pin content with a revision and/or `sha256` (or use flake inputs instead). Unlocked `builtins.getFlake` refs likewise need `--impure`.

At **build** time, downloads go through [fixed-output derivations (FODs)](../02-concepts/fixed-output-derivation.md): `fetchurl`, `fetchFromGitHub`, and related helpers must declare an `outputHash`. That is controlled impurity—the network may be used, but only for bytes matching the declared hash. Eval purity and build-time FOD fetches are related but separate concerns; see [purity and reproducibility](../01-philosophy/purity-and-reproducibility.md).

### IFD is a separate switch

[Import from derivation (IFD)](../02-concepts/import-from-derivation.md) lets evaluation realise a derivation and then `import` / `readFile` its output. **Pure flake eval does not disable IFD.** IFD is gated by `allow-import-from-derivation` in `nix.conf` (default `true` in Nix 2.34.x) and the CLI overrides `--allow-import-from-derivation` / `--no-allow-import-from-derivation`.

Hydra and many CI setups set `allow-import-from-derivation = false` so `nix flake check` and similar eval-only jobs cannot trigger builds mid-evaluation. Pure eval controls *which* ambient paths and builtins are visible; IFD controls whether eval may *build* to continue. Both can fail a flake check for different reasons.

### Escape hatch: `--impure`

When you truly need impure evaluation—legacy expressions, reading host paths, one-off debugging, or tooling that reads the environment—pass **`--impure`** on the Nix command (for example `nix build --impure .#package`, `nix eval --impure .#value`, `nix flake check --impure`). Documented on the experimental `nix` / `nix eval` / `nix flake check` pages (Nix 2.34 stable manual).

Treat `--impure` as a temporary escape hatch, not a project default. Long-term fixes:

- Replace `<nixpkgs>` / `builtins.nixPath` with flake `inputs`.
- Keep imports and `readFile` targets inside the flake tree (or declare another flake input).
- Pass `system` explicitly (e.g. attribute paths under `packages.<system>` for [packages, apps, and devShells](workflows/packages-apps-devShells.md)) instead of `builtins.currentSystem`.
- Pin fetches and commit [flake.lock](anatomy/lockfile.md).
- Move host-specific values into flake inputs or module options rather than `getEnv` or `~/…`.

## Examples

### Failing `<nixpkgs>` inside a flake

```nix
# flake.nix (broken under flake pure eval)
{
  outputs = { ... }: {
    packages.x86_64-linux.default =
      (import <nixpkgs> { system = "x86_64-linux"; }).hello;
  };
}
```

`<nixpkgs>` depends on `NIX_PATH`, which flake evaluation does not use. Fix by declaring `nixpkgs` as an input:

```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default =
      nixpkgs.legacyPackages.x86_64-linux.hello;
  };
}
```

Run `nix flake lock` (or any flake command) to populate the lockfile, then `nix build .#default`. Requires experimental `nix-command` and `flakes` (Nix 2.34.x).

### Absolute / home paths vs in-tree paths

```nix
# flake.nix — in-tree read is pure-eval-safe once the file is in the flake source
{
  outputs = { self }: {
    note = builtins.readFile ./note.txt;
    # host = builtins.readFile /etc/hostname;   # fails: absolute path
    # cfg  = builtins.readFile ~/.config/nix/nix.conf;  # fails: ~ in pure mode
  };
}
```

```bash
nix eval .#note                 # OK under pure flake eval
nix eval --impure --expr 'builtins.readFile /etc/hostname'
```

### `builtins.currentSystem` under flakes

```nix
# flake.nix — fails: attribute 'currentSystem' missing
{
  outputs = { self }: {
    value = builtins.currentSystem;
  };
}
```

```bash
nix eval .#value              # error under pure flake eval
nix eval --impure .#value     # e.g. "x86_64-linux"
```

Prefer an explicit system in the output path (`packages.x86_64-linux.…`) rather than `--impure` plus `currentSystem`.

### When `--impure` might appear

A third-party helper that still calls `builtins.getEnv` or imports an unpinned / out-of-tree path may only work with `nix build --impure .#…`. Document that requirement for local experiments, but refactor toward declared inputs before shipping to CI. Inline `--expr` with `<nixpkgs>` similarly needs `--impure` (or an `-I` / flake pin). Separately, if CI sets `allow-import-from-derivation = false`, fix IFD in the expression—`--impure` alone does not re-enable IFD.

## References

- [Nix manual — `pure-eval` (`nix.conf`)](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-pure-eval) — pure evaluation mode settings (stable / 2.34.x)
- [Nix manual — `nix` (installables / `--impure`)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html) — flake path vs `path:`; `--impure` for mutable paths; `-f` implies `--impure` (experimental `nix-command`)
- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — flake format, inputs, outputs, and lock file (experimental `flakes`)
- [Nix manual — `nix eval`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-eval.html) — `--impure`, `--file` / `--expr` (experimental)
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — eval checks under pure flake eval; `--impure` escape
- [Nix manual — `allow-import-from-derivation`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-allow-import-from-derivation) — IFD gate (separate from `pure-eval`)
- [nix.dev — Flakes (concept)](https://nix.dev/concepts/flakes) — defaults to pure mode; Git staging requirement

## See also

- [Purity boundaries](../03-language/semantics/purity-boundaries.md) — language-level builtins, paths, eval vs build impurity
- [Import from derivation](../02-concepts/import-from-derivation.md) — IFD vs pure eval; `allow-import-from-derivation`
- [flake.nix schema](anatomy/flake-nix-schema.md) — inputs, outputs, `self`, path wiring
- [Packages, apps, and devShells](workflows/packages-apps-devShells.md) — explicit `<system>` output paths
- [flakes (experimental feature)](../08-experimental-features/flakes.md) — enabling `flakes` / pairing with `nix-command`
- [Inputs and outputs](anatomy/inputs-and-outputs.md) — declaring locked flake dependencies
