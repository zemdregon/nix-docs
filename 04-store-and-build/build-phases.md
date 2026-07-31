---
status: complete
---

# Build Phases

## Overview

Nixpkgs **stdenv** splits package builds into named **phases**—unpack, patch, configure, build, check, install, fixup, installCheck, and dist—executed in order by `genericBuild` inside the default builder. This is not the Nix evaluator’s fixed-point step; it is the bash-driven workflow that [stdenv.mkDerivation](../06-nixpkgs/architecture/mkDerivation.md) runs when realizing a [derivation](../02-concepts/derivation.md).

Phases exist so packagers can override or extend one step (for example `postInstall`) without reimplementing the whole build. Most packages rely on the default phase scripts in `pkgs/stdenv/generic/setup.sh`; language-specific hooks (Cargo, CMake, Waf, and others) replace individual phases when needed.

## Details

### How phases run

`stdenv.mkDerivation` sets the derivation builder to load `setup.sh` and call `genericBuild`. That function either runs `buildCommand` / `buildCommandPath`, or walks the `phases` list, calling each phase function in turn.

When `phases` is unset, `setup.sh`’s `definePhases` uses this order (insertion slots expand to zero or more phase names):

```text
$prePhases unpackPhase patchPhase $preConfigurePhases configurePhase
$preBuildPhases buildPhase checkPhase $preInstallPhases installPhase
$preFixupPhases fixupPhase installCheckPhase $preDistPhases distPhase
$postPhases
```

List elements must not contain spaces; in Nix attributes, use lists rather than a single string.

### Default phases (summary)

| Phase | Role |
|-------|------|
| `unpackPhase` | Unpack or copy `src` / `srcs` into the build directory; may set `sourceRoot`. |
| `patchPhase` | Apply entries in `patches` (skip with `dontPatch`). |
| `configurePhase` | Run `./configure` (or `configureScript`) when present (skip with `dontConfigure`). |
| `buildPhase` | Compile; default runs `make` if a Makefile exists (skip with `dontBuild`). |
| `checkPhase` | Run the upstream test suite via `make`; off unless `doCheck = true`. |
| `installPhase` | Install into `$out`; default runs `make install` (skip with `dontInstall`). |
| `fixupPhase` | Nix-specific post-processing on installed files (see below). |
| `installCheckPhase` | Run install-time tests via `make installcheck`; off unless `doInstallCheck = true`. |
| `distPhase` | Produce a source distribution; runs only when `doDist` is set. |

When the build platform cannot execute host binaries (`buildPlatform.canExecute hostPlatform` is false—typical of cross builds), `mkDerivation` forces `doCheck` and `doInstallCheck` off, so those phases do not run even if you set them true.

### fixupPhase

Do not drop `fixupPhase` lightly. The default implementation:

- Moves `man/`, `doc/`, and `info/` under `share/`.
- Strips debug symbols from libraries and executables.
- On Linux, runs `patchelf` to shrink `RPATH` and avoid spurious runtime dependencies.
- Rewrites script shebangs (`#!`) to interpreters found on `PATH` in the build environment.

Skipping fixup commonly leaves scripts pointing at `/usr/bin/...` or bloated closures.

### Hooks and overrides

Each phase has optional `pre*` and `post*` hooks (for example `preConfigure`, `postInstall`, `preFixup`). Prefer hooks when you only need to add commands.

To replace a phase entirely, set `namePhase` to a shell string or redefine the `namePhase` function. When overriding a full phase, start with `runHook prePhaseName` and end with `runHook postPhaseName` so downstream overrides still work.

Setting the full `phases` attribute is **discouraged**—it is easy to omit `fixupPhase` or other less obvious steps. To insert custom steps, use the insertion variables instead:

- `prePhases`, `preConfigurePhases`, `preBuildPhases`, `preInstallPhases`, `preFixupPhases`, `preDistPhases`, `postPhases`

In an interactive `nix-shell`, run `genericBuild` to execute phases in build order, or set `phases` temporarily to stop after a subset (useful when [debugging builds](debugging-builds.md)).

## Examples

Illustrative package fragment (not built in this pass). Override `buildPhase` for a Makefile-less tree, and add a `postInstall` hook:

```nix
stdenv.mkDerivation {
  pname = "example";
  version = "1.0";
  src = ./.;

  buildPhase = ''
    runHook preBuild
    make -C src all
    runHook postBuild
  '';

  postInstall = ''
    install -Dm755 src/example "$out/bin/example"
  '';
}
```

Insert a custom phase before configure without replacing the default list:

```nix
preConfigurePhases = [ "autoreconfPhase" ];
```

## References

- [Nixpkgs manual — Phases](https://nixos.org/manual/nixpkgs/stable/#sec-stdenv-phases)
- [Nixpkgs manual — stdenv](https://nixos.org/manual/nixpkgs/stable/#ch-stdenv)

## See also

- [Builders and sandboxes](builders-and-sandboxes.md) — who runs the builder and sandbox isolation during phase execution
- [Debugging builds](debugging-builds.md) — stepping through phases in `nix-shell`
- [stdenv](../06-nixpkgs/architecture/stdenv.md) — the standard build environment that defines phases
- [mkDerivation](../06-nixpkgs/architecture/mkDerivation.md) — the function that wires derivations to `genericBuild`
- [Derivation](../02-concepts/derivation.md) — what gets realized when phases complete
