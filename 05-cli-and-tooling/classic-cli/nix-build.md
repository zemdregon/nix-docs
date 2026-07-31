---
status: complete
---

# nix-build

## Overview

`nix-build` is the classic Nix command that evaluates one or more Nix expressions, realizes the resulting [derivations](../../02-concepts/derivation.md), and places a symlink to the built output in the current directory. It is the high-level “build this expression” entry point from the pre-flakes era and remains common in older tutorials and nixpkgs workflows.

The command is distinct from [`nix build`](../modern-cli/nix-build-develop-run.md) (the modern CLI). Both ultimately realize store derivations; they differ in argument style, output linking, and integration with flakes.

## Details

**What it builds.** `nix-build` takes paths to `.nix` files (or tarball URLs containing a `default.nix`). With no paths, it uses `./default.nix` if present. It evaluates the expression, obtains one or more derivations, and builds them. Options such as `--arg`, `--argstr`, and `-E` / `--expr` are forwarded to evaluation—the same pattern as `nix-instantiate`.

**The `result` symlink.** On success, `nix-build` creates a symlink named `result` pointing at the default (first) output path. Multiple expressions or derivations produce `result`, `result-2`, and so on. Use `-o` / `--out-link` to choose a different name. For derivations with multiple outputs, `nix-build` can create `result-<outputname>` symlinks (for example `result-bin`); the `out` output keeps the plain `result` name.

**`-A` / `--attr`.** Select an attribute from the top-level expression instead of expecting it to evaluate directly to a derivation. Attribute paths use dot notation (`hello`, `xorg.xorgserver`, `foo.3.bar`). This is how most nixpkgs builds are invoked: `nix-build '<nixpkgs>' -A hello`.

**`--no-out-link`.** Skip creating the symlink. The build still runs and outputs are still in the store, but nothing is registered as a garbage-collector root via an out-link. Those paths may be collected by `nix-store --gc` unless kept alive by another root.

**Relation to `nix-instantiate` and `nix-store --realise`.** The manual describes `nix-build` as a wrapper around two lower-level steps:

1. **`nix-instantiate`** — evaluate the Nix expression and register `.drv` files in the store (options like `--arg`, `--argstr`, and `-A` go here).
2. **`nix-store --realise`** — build the derivation and materialize output paths (most other flags are passed through to this step).

So `nix-build default.nix` is roughly equivalent to realizing the derivation produced by `nix-instantiate default.nix`, with the convenience of creating a `result` symlink and registering a GC root for it.

**GC roots via out-links.** The `result` symlink is a garbage-collector root: deleting or renaming it removes that root. Do not rename it casually if you rely on the build staying cached.

**Contrast with `nix build`.** The modern [`nix build`](../modern-cli/nix-build-develop-run.md) command uses the experimental CLI (`nix3-build`), works naturally with flake outputs and installables (`.#hello`, `nixpkgs#hello`), and writes results under `./result` by default but with different flag names and behaviors (for example `--out-link`, `--no-link`, JSON logging). `nix-build` remains attribute- and path-oriented (`-A`, `default.nix`, `<nixpkgs>`). New projects on flakes usually prefer `nix build`; classic docs and one-off `.nix` file builds still reach for `nix-build`.

**Build failures.** Failed builds can exit with `1xx` status codes (for example `100` generic failure, `102` hash mismatch). See [debugging builds](../../04-store-and-build/debugging-builds.md) when a build fails or exits non-zero.

## Examples

Build an attribute from nixpkgs (realization may substitute or build; use `--dry-run` to plan only):

```bash
nix-build '<nixpkgs>' -A hello
ls -l result
```

Build without creating an out-link (output path printed, no `result` symlink):

```bash
nix-build '<nixpkgs>' -A hello --no-out-link
```

Build from an inline expression:

```bash
nix-build -E 'with import <nixpkgs> { }; runCommand "foo" { } "echo bar > $out"'
cat ./result
```

Rough manual decomposition (evaluation then realization):

```bash
drv=$(nix-instantiate '<nixpkgs>' -A hello)
nix-store --realise "$drv"
```

## References

- [nix-build — Nix reference manual](https://nix.dev/manual/nix/stable/command-ref/nix-build.html)

## See also

- [nix build / develop / run](../modern-cli/nix-build-develop-run.md)
- [Derivation](../../02-concepts/derivation.md)
- [Debugging builds](../../04-store-and-build/debugging-builds.md)
- [nix-store](nix-store.md)
