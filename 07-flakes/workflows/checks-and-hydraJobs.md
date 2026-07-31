---
status: complete
---

# checks and hydraJobs

## Overview

Flakes expose two **CI-oriented** conventional outputs: **`checks`** for local and forge validation, and **`hydraJobs`** for Hydra-style job trees. **`checks.<system>.<name>`** are [derivations](../../02-concepts/derivation.md) that `nix flake check` evaluates and **builds** (by default). **`hydraJobs`** is an arbitrarily nested attrset of derivation leaves that `nix flake check` **evaluates** the same way Hydra’s `hydra-eval-jobs` walks a job tree—without scheduling Hydra builds.

These are **not** substitutes for [packages, apps, and devShells](packages-apps-devShells.md). Packages are what you ship and `nix build`; checks are gate derivations; hydraJobs are the job graph a Hydra jobset imports. Wiring of `outputs` lives in [inputs and outputs](../anatomy/inputs-and-outputs.md) and the [flake.nix schema](../anatomy/flake-nix-schema.md).

`nix flake check` is experimental: enable [`nix-command`](../../08-experimental-features/nix-command.md) and [`flakes`](../../08-experimental-features/flakes.md) (Nix ≥ 2.4). Flags and validated output types can still change between releases.

## Details

### Roles at a glance

| Output | Shape | Who consumes it | `nix flake check` |
|--------|--------|-----------------|-------------------|
| `checks.<system>.<name>` | derivation | developers, GHA/Forgejo/`nix flake check` | type-check + **build** (unless `--no-build`) |
| `hydraJobs.…` | nested attrset → derivation leaves | Hydra flake jobsets (and compatible evaluators) | **evaluate** only (hydra-eval-jobs shape) |
| `packages` / `apps` / `devShells` | per-system installables | day-to-day CLI | type-check; does **not** build packages as “checks” |
| `legacyPackages.<system>` | package-set discovery | `nix-env`-style browse; Nixpkgs flake | evaluate like `nix-env --query --available` |

### `checks` — flake-local test gate

Each value under `checks.<system>.<name>` must be a **derivation**. Typical contents: unit/integration smoke tests, format/lint wrappers, “file present” assertions, or small NixOS/VM smoke derivations that must pass before merge.

**Contributor recipe:** add one check per distinct failure mode you care about locally; keep each check cheap enough that `nix flake check` is the default pre-push / PR gate. Prefer `pkgs.runCommand` / `pkgs.testers` style derivations that write `$out` on success and fail the build otherwise.

**Operator recipe (forge CI):** install Nix on the runner, keep `flake.lock` in the checkout, then run `nix flake check` (optionally with a [binary cache](../../11-development/ci-with-nix.md)). Same command works for GitHub Actions, Forgejo Actions, and similar runners—no special `hydraJobs` wiring required for that path.

### What `nix flake check` validates

From the [Nix manual](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html), the command:

1. Evaluates the flake successfully.
2. **Builds** every `checks.<system>.<name>` for the selected system(s), unless **`--no-build`**.
3. **Type-checks** other conventional outputs when present: `packages` and `devShells` (derivations), `apps` (app definitions), `templates`, `overlays`, `nixosModules`, `bundlers`, and `nixosConfigurations.<name>.config.system.build.toplevel` (derivation).
4. **Evaluates** `hydraJobs` as a nested attrset of derivations and `legacyPackages.<system>` like `nix-env --query --available`.

Useful flags:

- **`--all-systems`** — check outputs for every system key, not only the current host.
- **`--no-build`** — evaluate checks (and schema / hydraJobs) without building check derivations.
- **`keep-going`** — e.g. `--keep-going` or `--option keep-going true` — continue after the first error and report as many failures as possible.

`nix flake check` does **not** schedule Hydra builds and does **not** build every package under `packages` unless you also listed those derivations under `checks`.

### `hydraJobs` — Hydra job attrset

Values under `hydraJobs` form an **arbitrarily nested** attrset whose **leaves** are derivations. Nested attribute names become job / group names in Hydra; leaf derivations become build jobs. Flakes do not run Hydra for you—this output is the **shape** a Hydra **flake jobset** imports (flake URI → evaluate `hydraJobs`). Project/jobset/evaluation/build lifecycle belongs in [Hydra](../../12-deployment-and-infra/hydra.md).

**Operator recipe:** when you run Hydra, point a flake-type jobset at the repo flake URI and expose the jobs you want built under `hydraJobs` (often `inherit (self) packages;` or a nested `packages` / `tests` tree). Hydra evaluates flakes in **restricted mode**; allow expected input URI prefixes on the Hydra host (see the Hydra page—do not invent jobset UI fields here).

**Contributor recipe:** keep `hydraJobs` leaves as real derivations (same as checks). Reuse the same test derivation in both `checks` and `hydraJobs` when both forge CI and Hydra should build it. Nested layout is free-form; pick names Hydra operators can navigate (`hydraJobs.packages…`, `hydraJobs.tests…`).

Optional: wrap leaves with nixpkgs **`lib.hydraJob`** when preparing derivations for `hydra-eval-jobs`. It strips non-essential attributes and strictly evaluates the result so Hydra evaluation does not retain large thunks ([nixpkgs manual — `lib.customisation.hydraJob`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.customisation.hydraJob)). Most small application flakes can assign derivations directly.

### Choosing checks vs hydraJobs vs packages

- **Laptop + GHA/Forgejo only** → expose tests under `checks`; gate on `nix flake check`. Skip `hydraJobs` unless something else consumes that tree.
- **Hydra jobset** → expose `hydraJobs`; mirror packages/tests you want the farm to build. Still keep important gates in `checks` so contributors without Hydra get the same local command.
- **Ship / run / develop** → `packages` / `apps` / `devShells` (see [Packages, Apps, devShells](packages-apps-devShells.md)). Putting a package only under `packages` does not make `nix flake check` build it.

### `legacyPackages` — discovery, not a CI gate

`legacyPackages.<system>` is for browsing and ad hoc installables (`nix build .#legacyPackages.<system>.hello`). Nixpkgs uses it heavily; most application flakes only need `packages`.

## Examples

**Checks** as smoke-test derivations (single system):

```nix
{
  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    checks.${system}.hello-smoke = pkgs.runCommand "hello-smoke" {} ''
      ${pkgs.hello}/bin/hello | grep -q Hello
      touch $out
    '';

    checks.${system}.script-present = pkgs.runCommand "script-present" {} ''
      test -f ${./scripts/deploy.sh}
      touch $out
    '';
  };
}
```

Run from the flake directory (`nix-command` / `flakes` enabled):

```bash
nix flake check              # build checks for current system; validate other outputs
nix flake check --all-systems
nix flake check --no-build   # evaluate checks / hydraJobs / schema without building
```

**`hydraJobs`** nested tree (Hydra flake jobset consumes this attribute):

```nix
{
  outputs = { self, nixpkgs }: let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
    hello-smoke = pkgs.runCommand "hello-smoke" {} ''
      ${pkgs.hello}/bin/hello
      touch $out
    '';
  in {
    packages.x86_64-linux.default = pkgs.hello;

    checks.x86_64-linux.hello-smoke = hello-smoke;

    hydraJobs = {
      inherit (self) packages;
      tests.hello-smoke = hello-smoke;
    };
  };
}
```

Illustrative only: assumes `./scripts/deploy.sh` exists in the first example; adjust systems and package names for your flake. Forge CI typically runs the same `nix flake check` as a contributor laptop—see [CI with Nix](../../11-development/ci-with-nix.md).

## References

- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — checks, flags, validated output types, `hydraJobs` / `legacyPackages` evaluation
- [Nix manual — `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — conventional output attributes including `checks`, `hydraJobs`, and `legacyPackages`
- [nixpkgs manual — `lib.customisation.hydraJob`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.customisation.hydraJob) — strip/strict-eval helper for Hydra job leaves
- [NixOS/hydra](https://github.com/NixOS/hydra) — Hydra CI (projects, jobsets, flake job import)
- [NixOS Wiki — Hydra (flake jobset)](https://wiki.nixos.org/wiki/Hydra#Flake_jobset) — secondary; `hydraJobs` nested attrset for flake jobsets

## See also

- [Packages, Apps, devShells](packages-apps-devShells.md) — primary flake outputs for build, run, and develop
- [flake.nix schema](../anatomy/flake-nix-schema.md) — top-level `flake.nix` attributes and `outputs` contract
- [Inputs and outputs](../anatomy/inputs-and-outputs.md) — how `outputs` functions receive inputs
- [CI with Nix](../../11-development/ci-with-nix.md) — forge CI wiring `nix flake check`
- [Hydra](../../12-deployment-and-infra/hydra.md) — jobsets, evaluations, self-hosted Hydra
- [Derivation](../../02-concepts/derivation.md) — what check and hydraJobs leaves must evaluate to
