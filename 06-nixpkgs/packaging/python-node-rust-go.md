---
status: complete
---

# Python / Node / Rust / Go

## Overview

Most software in Python, Node/npm, Rust (Cargo), or Go is packaged in Nixpkgs with **language-specific builders and hooks**, not bare [`stdenv.mkDerivation`](../architecture/mkDerivation.md). Those helpers encode ecosystem conventions—dependency fetching, install layout, test runners, and wrapper behavior—while still running on top of [stdenv](../architecture/stdenv.md) phases and setup hooks.

This page is a **survey** of the main entry points. For attribute-level detail, use the [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) chapter of the Nixpkgs manual and sibling pages such as [simple-package.md](simple-package.md).

## Details

### Prefer builders over raw stdenv

When upstream already uses pip/setuptools, npm/yarn, Cargo, or Go modules, start from the matching helper:

| Ecosystem | Typical builder | Package set |
|-----------|-----------------|-------------|
| Python | `buildPythonPackage`, `buildPythonApplication` | `python3Packages` |
| Go | `buildGoModule` | top-level / scoped by Go version |
| Rust | `rustPlatform.buildRustPackage` | per-Rust-version `rustPlatform` |
| Node/npm | `buildNpmPackage`, or `npmHooks` + `stdenv` | `nodePackages`, project-local hooks |

Raw `stdenv.mkDerivation` remains valid—especially for mixed-language trees or unusual build scripts—but you reimplement what these builders already wire up (dependency FODs, install paths, check phases).

All of them assume packages live in the right [package set](../architecture/package-sets.md): Python deps must come from the same `python3Packages` scope (same interpreter), Rust from the matching `rustPlatform`, and so on. The [callPackage](../../03-language/idioms/callPackage.md) pattern is unchanged; only the inner function changes.

### Python

Python libraries and apps are registered under **`python3Packages`** (a scoped set tied to the default CPython 3 interpreter). Depend on sibling packages from that set so versions and `PYTHONPATH` stay consistent.

- **`buildPythonPackage`** — installable library or module (wheel/sdist workflow, `pyproject.toml` / setuptools hooks).
- **`buildPythonApplication`** — application with console scripts; often adds wrappers automatically.
- **`python.withPackages`** — build a custom interpreter environment from a list of packages in the same scope (similar in spirit to a venv, but as a derivation).

Python builders pull in setup hooks (test runners, path wiring) and enable install checks by default. Override phases or hooks when upstream is non-standard, but start from the builder API documented under [Python](https://nixos.org/manual/nixpkgs/stable/#python) in the manual.

### Go

**`buildGoModule`** is the standard builder for Go modules. It uses a two-step model: a fixed-output **`goModules`** derivation vendors or downloads module sources, then the main derivation compiles binaries from that output.

The usual fixed-output knob is **`vendorHash`** (hash of the `goModules` output). Set it to `null` when the upstream repo already commits a `vendor/` tree and you want to use that instead of re-vendoring. The manual’s [Building Go modules with buildGoModule](https://nixos.org/manual/nixpkgs/stable/#ssec-language-go) section documents `vendorHash`, migration from legacy `buildGoPackage`, and versioned builders such as `buildGo124Module` when you must pin a Go toolchain.

Versioned **`go_*`** / **`buildGo*Module`** pairs track upstream Go releases; prefer the default toolchain unless the project requires otherwise.

### Rust

**`rustPlatform.buildRustPackage`** wraps Cargo builds: fetch crates, run `cargo build` / `cargo install`, honor common test and feature flags.

Dependency locking uses one of:

- **`cargoHash`** — SRI hash over vendored crate sources (common when there is no committed lockfile, or for simpler expressions).
- **`cargoLock`** — import a `Cargo.lock` (via `lockFile` / `lockFileContents`) so hashes track the lockfile instead of manual `cargoHash` updates.

See [Compiling Rust applications with Cargo](https://nixos.org/manual/nixpkgs/stable/#compiling-rust-applications-with-cargo) and [Importing a Cargo.lock file](https://nixos.org/manual/nixpkgs/stable/#importing-a-cargo.lock-file). Pick the `rustPlatform` that matches the Rust version the crate expects (stable vs nightly is a separate manual topic).

### Node / JavaScript

The Node ecosystem moves quickly; Nixpkgs exposes several overlapping tools. For **npm** projects with `package-lock.json`, **`buildNpmPackage`** is the well-documented high-level builder: it builds a reproducible npm cache (fixed output via **`npmDepsHash`**) and runs standard build/install phases.

Lower-level composition uses **`npmHooks`** (`npmConfigHook`, `npmBuildHook`, `npmInstallHook`) inside a normal `stdenv.mkDerivation`—useful when you only need `node_modules` for a frontend subproject or when combining with another language builder (for example Rust + npm in one repo).

Yarn, pnpm, and other lockfile formats have separate fetchers and hooks; upstream lockfile type should drive tool choice. The manual’s [JavaScript](https://nixos.org/manual/nixpkgs/stable/#language-javascript) section lists options and known pitfalls; search existing nixpkgs packages for patterns when tooling churn outpaces the manual.

General guidance: match upstream **Node version** and **package manager** when possible, and respect the committed lockfile rather than regenerating it inside the derivation.

### What the helpers share

Language builders are thin orchestration around stdenv:

- They set **`nativeBuildInputs`** / **`buildInputs`** and register setup hooks.
- They still honor **`buildPhase`**, **`installPhase`**, **`checkPhase`**, and **`meta`** the same way as [mkDerivation](../architecture/mkDerivation.md).
- Fixed-output sub-derivations (`goModules`, npm deps, Cargo vendor trees) follow the same [FOD](../../02-concepts/fixed-output-derivation.md) workflow: placeholder hash, rebuild, copy the reported hash.

When a flag or hook name is not listed in the manual for your builder, prefer reading an existing package in nixpkgs over guessing attribute names.

## Examples

Minimal shapes only—replace placeholder hashes after the first failed build.

**Python library** (`buildPythonPackage`):

```nix
{ lib, buildPythonPackage, fetchPypi }:

buildPythonPackage rec {
  pname = "example";
  version = "1.0.0";
  pyproject = true;

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  pythonImportsCheck = [ "example" ];

  meta = with lib; {
    description = "Example Python library";
    license = licenses.mit;
  };
}
```

**Go module** (`buildGoModule` + `vendorHash`):

```nix
{ lib, buildGoModule, fetchFromGitHub }:

buildGoModule rec {
  pname = "example";
  version = "0.1.0";

  src = fetchFromGitHub {
    owner = "org";
    repo = "example";
    tag = "v${version}";
    hash = "sha256-BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=";
  };

  vendorHash = "sha256-CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC=";

  meta = with lib; {
    description = "Example Go program";
    license = lib.licenses.mit;
  };
}
```

**Rust crate** (`rustPlatform.buildRustPackage` + `cargoHash`):

```nix
{ lib, rustPlatform, fetchFromGitHub }:

rustPlatform.buildRustPackage rec {
  pname = "example";
  version = "0.1.0";

  src = fetchFromGitHub {
    owner = "org";
    repo = "example";
    tag = "v${version}";
    hash = "sha256-DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD=";
  };

  cargoHash = "sha256-EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE=";

  meta = with lib; {
    description = "Example Rust binary";
    license = lib.licenses.mit;
  };
}
```

**npm project** (`buildNpmPackage`):

```nix
{ lib, buildNpmPackage, fetchFromGitHub }:

buildNpmPackage rec {
  pname = "example";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "org";
    repo = "example";
    tag = "v${version}";
    hash = "sha256-FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF=";
  };

  npmDepsHash = "sha256-GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG=";

  meta = with lib; {
    description = "Example Node application";
    license = lib.licenses.mit;
  };
}
```

**Python environment** (`withPackages`):

```nix
# pkgs.python3.withPackages (ps: [ ps.requests ps.click ])
```

## References

- [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) — Nixpkgs manual hub
- [Python](https://nixos.org/manual/nixpkgs/stable/#python) — `buildPythonPackage`, `buildPythonApplication`, `withPackages`
- [Building Go modules with buildGoModule](https://nixos.org/manual/nixpkgs/stable/#ssec-language-go) — `vendorHash`, `goModules`
- [Compiling Rust applications with Cargo](https://nixos.org/manual/nixpkgs/stable/#compiling-rust-applications-with-cargo) — `buildRustPackage`, `cargoHash`
- [Importing a Cargo.lock file](https://nixos.org/manual/nixpkgs/stable/#importing-a-cargo.lock-file) — `cargoLock`
- [JavaScript / buildNpmPackage](https://nixos.org/manual/nixpkgs/stable/#javascript-buildNpmPackage) — npm packaging
- [npmConfigHook](https://nixos.org/manual/nixpkgs/stable/#npm-config-hook) — lower-level npm hooks

## See also

- [Package sets](../architecture/package-sets.md) — scoped sets like `python3Packages`
- [stdenv](../architecture/stdenv.md) — phases and setup hooks underneath builders
- [mkDerivation](../architecture/mkDerivation.md) — escape hatch and shared attributes
- [Simple package](simple-package.md) — Autotools/C-style packaging baseline
- [callPackage](../../03-language/idioms/callPackage.md) — wiring function arguments from `pkgs`
