---
status: complete
---

# Multiple Outputs

## Overview

A single Nix derivation can produce more than one [store path](../../02-concepts/store-path.md). Set `outputs = [ "out" "dev" "doc" … ]` on an `mkDerivation` package and each name becomes an attribute on the resulting package value (for example `pkgs.zlib.dev`).

The main motivation is smaller [closures](../../02-concepts/closure.md): runtime dependencies can omit development-only files (headers, static libraries, documentation) that would otherwise live in the same output. Nixpkgs provides a framework—triggered by declaring `outputs`—that assigns files to outputs by convention during install and fixup.

## Details

**Separate paths, one build.** Each output gets its own store path and can be garbage-collected or substituted independently. Building from source always realizes all outputs of the derivation; you cannot build only one output in isolation.

**Declaring outputs.** The `outputs` attribute is a list of output name strings. Nix creates a matching attribute for each name. The usual split is:

| Output | Typical contents |
|--------|------------------|
| `out` | Runtime files not placed elsewhere (catch-all) |
| `lib` | Shared libraries (`lib/`, `libexec/`) |
| `bin` | User-facing executables (`bin/`) |
| `dev` | Development files (headers, `.pc`, CMake config) |
| `doc` | User documentation |
| `man` | Manual pages |

Often a single `outputs = [ "out" "dev" "doc" ];` line is enough; the framework handles the rest.

**Builder environment.** For each output name `foo`, the builder receives `$foo` pointing at that output’s store path. Install phases write into `$out`, `$dev`, and so on. The [`multiple-outputs.sh`](https://nixos.org/manual/nixpkgs/stable/#chap-multiple-output) setup hook (part of stdenv) configures common build systems and moves files into the correct outputs during fixup according to file-type groups (`outputDev`, `outputBin`, `outputLib`, …). See the manual for the full group list and default target names—do not rely on undocumented move rules.

**Using packages as build inputs.** When a split package appears in `buildInputs` (or related input lists) without a suffix, Nixpkgs adds the `dev` output if it exists, otherwise the first listed output. `propagatedBuildOutputs` (defaulting to the `bin` and `lib` output groups) are propagated alongside. To depend on a specific slice, reference it explicitly: `buildInputs = [ zlib.dev pkg-config ];`.

**Installing for users.** `meta.outputsToInstall` controls which outputs land in a profile when the package name is used unqualified (defaults favor `bin`, `out`, or the first output, plus `man` when present).

**Recombining outputs.** [`symlinkJoin`](https://nixos.org/manual/nixpkgs/stable/#trivial-builder-symlinkJoin) merges multiple outputs under one path when a single prefix is needed (for example wrapping an interpreter with plugins). This restores convenience at the cost of closure-size benefits from splitting.

**Caveats.** Outputs of one derivation may reference each other, but circular references are forbidden. Some upstream build systems assume a single install prefix or reject `--docdir`-style flags; set `setOutputFlags = false` when configure breaks. Libraries that embed data from `out` (locale strings, and similar) are often kept in `out` rather than split into `lib`.

## Examples

**Minimal split declaration** (framework assigns files by type):

```nix
stdenv.mkDerivation {
  pname = "example";
  version = "1.0";
  src = ./.;
  outputs = [ "out" "dev" "doc" "man" ];
}
```

**Referencing a specific output** in another derivation:

```nix
stdenv.mkDerivation {
  pname = "consumer";
  version = "1.0";
  src = ./.;
  buildInputs = [ zlib.dev ];  # explicit; bare `zlib` would also pick `.dev`
}
```

**Runtime-only dependency** (omit development files from the closure):

```nix
{ lib, stdenv, fetchurl, zlib }:

stdenv.mkDerivation {
  pname = "app";
  version = "1.0";
  src = fetchurl { /* … */ };
  buildInputs = [ zlib.dev ];
  # propagated runtime deps can use the non-dev output explicitly:
  propagatedBuildInputs = [ zlib.out ];
}
```

**Combining outputs** when one prefix is required:

```nix
{ symlinkJoin, hello }:

symlinkJoin {
  name = "hello-with-man";
  paths = [ hello.out hello.man ];
}
```

## References

- [Multiple-output packages](https://nixos.org/manual/nixpkgs/stable/#chap-multiple-output) — Nixpkgs manual (framework overview)
- [Using a split package](https://nixos.org/manual/nixpkgs/stable/#sec-multiple-outputs-using-split-packages) — build-input and install behavior
- [Writing a split derivation](https://nixos.org/manual/nixpkgs/stable/#sec-multiple-outputs-) — declaring `outputs`, file-type groups, caveats
- [symlinkJoin](https://nixos.org/manual/nixpkgs/stable/#trivial-builder-symlinkJoin) — merging outputs into one path

## See also

- [mkDerivation](../architecture/mkDerivation.md) — package constructor where `outputs` is set
- [Store path](../../02-concepts/store-path.md) — what each output name resolves to
- [Closure](../../02-concepts/closure.md) — why splitting reduces runtime dependencies
- [Garbage collection](../../04-store-and-build/garbage-collection.md) — outputs can be collected independently
- [Simple package](simple-package.md) — single-output baseline before splitting
