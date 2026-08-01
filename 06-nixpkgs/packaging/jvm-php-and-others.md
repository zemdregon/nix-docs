---
status: complete
---

# JVM / PHP and other languages

## Overview

Beyond the Python / Node / Rust / Go survey, Nixpkgs’ [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) chapter covers many other ecosystems—JVM (Java/Gradle), PHP (Composer), Ruby, Perl, OCaml, and more. Each has specialised builders or hooks on top of [`stdenv.mkDerivation`](../architecture/mkDerivation.md), usually scoped into a matching [package set](../architecture/package-sets.md).

This page is a **survey hub**: entry points and FOD patterns, not a mirror of each manual section. Same rules as [Python / Node / Rust / Go](python-node-rust-go.md): prefer language builders; stay in the matching package set; pin lock/vendor inputs with fixed-output hashes ([fetchers and pinning](fetchers-and-pinning.md)).

## Details

### Shared packaging rules

| Rule | Why |
|------|-----|
| Prefer the documented language builder / hooks | They wire phases, setup hooks, and dependency FODs you would otherwise reimplement |
| Depend inside the matching package set | Same interpreter/compiler scope (e.g. `php.extensions`, `ruby.gems`, `perlPackages`) |
| Pin lock / vendor trees with FODs | `vendorHash`, Gradle `deps.json` / `mitmCache`, Composer repository hashes — same [FOD](../../02-concepts/fixed-output-derivation.md) workflow as `cargoHash` / `npmDepsHash` |

Explore nested sets in `nix repl` (the Languages chapter shows tab-completing `javaPackages` and similar). For shell-oriented toolchain maps, see [language toolchains](../../11-development/language-toolchains.md).

### JVM / Java

**`javaPackages`** groups compiler and related variants (OpenJFX releases, `javaPackages.compiler`, helpers such as `mavenfod`). The manual’s Languages intro walks navigating that set with `nix repl` ([Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support)).

Classic **Ant**-based packages usually take `ant`, a `jdk`, and often `stripJavaArchivesHook` in `nativeBuildInputs`, then run `ant` in `buildPhase`. Install shared JARs under `$out/share/java` so JDK setup hooks can put them on `CLASSPATH`; wrap programs with `makeWrapper` and a JRE. Details: [Java](https://nixos.org/manual/nixpkgs/stable/#sec-language-java).

**Gradle** (Java/Kotlin) does not make dependency resolution reproducible by itself. Nixpkgs records Gradle network fetches via a MITM cache:

1. Put `gradle` in `nativeBuildInputs` so the Gradle setup hook runs configure/build/check.
2. Set **`mitmCache = gradle.fetchDeps { …; data = ./deps.json; }`** (and usually `pname` or `pkg`) so the build restores pinned deps.
3. Refresh the lock with the cache’s **`updateScript`** when dependencies change.

Optional knobs include `gradleFlags`, `gradleBuildTask` (default `assemble`), and `gradleCheckTask` (default `test`). Full API: [Gradle](https://nixos.org/manual/nixpkgs/stable/#gradle) / [Building a Gradle package](https://nixos.org/manual/nixpkgs/stable/#building-a-gradle-package).

### PHP

PHP interpreters live under versioned attributes (`php81`, …); **`php`** is the release’s preferred default. Extensions and tools hang off that interpreter (`php.extensions`, `php.packages.composer`); compose runtimes with `php.withExtensions` / `php.buildEnv` ([PHP](https://nixos.org/manual/nixpkgs/stable/#sec-php)).

For Composer applications, the documented high-level builder is **`php.buildComposerProject2`**: a `mkDerivation` wrapper that builds a fixed-output Composer repository from `composer.json` / `composer.lock`, installs `vendor`, and links `bin` scripts. Pin deps with **`vendorHash`**; if upstream omits the lockfile, pass **`composerLock`**. Lower-level composition uses `php.mkComposerRepository` and `php.composerHooks` inside a normal derivation. See [Building PHP projects](https://nixos.org/manual/nixpkgs/stable/#ssec-building-php-projects).

### Ruby

Default interpreter is **`ruby`** (versioned MRI as `ruby_3_y`, plus `jruby` / `mruby`). Gems live under **`ruby.gems`** (and per-interpreter sets); prefer **`ruby.withPackages (ps: [ … ])`** so the interpreter can `require` them. Application packaging may use a locked `Gemfile` workflow or the shared gem set—follow [Ruby](https://nixos.org/manual/nixpkgs/stable/#sec-language-ruby) rather than inventing Bundler helpers.

### Perl

CPAN-style libraries use **`buildPerlPackage`** and live in **`perlPackages`**. The builder runs `perl Makefile.PL`, adjusts shebangs/`PERL5LIB`, and propagates Perl deps for `nix-env`-style installs. Prefer `mirror://cpan/` sources and depend on siblings from the same set. See [Perl](https://nixos.org/manual/nixpkgs/stable/#sec-language-perl) / [Packaging Perl programs](https://nixos.org/manual/nixpkgs/stable/#ssec-perl-packaging).

### Rest of the Languages chapter

OCaml (`ocamlPackages` / `ocaml-ng.ocamlPackages_*`), and many other ecosystems, are documented in the same [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) chapter. Treat those sections as the source of truth for builders and package-set names; this hub does not duplicate them. Haskell has its own leaf: [Haskell packaging](haskell-packaging.md).

## Examples

Minimal shapes only—replace placeholder hashes after the first failed build.

**Gradle** (`mitmCache` + `gradle.fetchDeps`):

```nix
stdenv.mkDerivation (finalAttrs: {
  pname = "example";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "example";
    repo = "example";
    tag = "v${finalAttrs.version}";
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  nativeBuildInputs = [ gradle makeWrapper ];

  mitmCache = gradle.fetchDeps {
    inherit (finalAttrs) pname;
    data = ./deps.json;
  };

  # gradleFlags / gradleBuildTask as needed — see Gradle manual section
  # Refresh deps: $(nix-build -A mitmCache.updateScript) then commit deps.json
})
```

**PHP Composer app** (`php.buildComposerProject2`):

```nix
{ php, fetchFromGitHub }:

php.buildComposerProject2 (finalAttrs: {
  pname = "php-app";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "example";
    repo = "php-app";
    tag = finalAttrs.version;
    hash = "sha256-BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=";
  };

  vendorHash = "sha256-CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC=";
  # composerLock = ./composer.lock;  # if missing from src
})
```

**Ruby environment** (`withPackages`):

```nix
# pkgs.ruby.withPackages (ps: with ps; [ nokogiri pry ])
```

**Perl library** (`buildPerlPackage` in `perlPackages`):

```nix
buildPerlPackage rec {
  pname = "Class-C3";
  version = "0.21";
  src = fetchurl {
    url = "mirror://cpan/authors/id/F/FL/FLORA/Class-C3-${version}.tar.gz";
    hash = "sha256-DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD=";
  };
}
```

## References

- [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) — chapter hub; `javaPackages` / package-set navigation
- [Java](https://nixos.org/manual/nixpkgs/stable/#sec-language-java) — Ant, JARs, wrappers, JDKs
- [Gradle](https://nixos.org/manual/nixpkgs/stable/#gradle) — `gradle.fetchDeps`, `mitmCache`
- [Building a Gradle package](https://nixos.org/manual/nixpkgs/stable/#building-a-gradle-package)
- [PHP](https://nixos.org/manual/nixpkgs/stable/#sec-php) — interpreters, extensions, `withExtensions`
- [Building PHP projects](https://nixos.org/manual/nixpkgs/stable/#ssec-building-php-projects) — `php.buildComposerProject2`, `vendorHash`
- [Ruby](https://nixos.org/manual/nixpkgs/stable/#sec-language-ruby) — `ruby.withPackages`, gems
- [Perl](https://nixos.org/manual/nixpkgs/stable/#sec-language-perl) — `buildPerlPackage`, `perlPackages`
- [OCaml](https://nixos.org/manual/nixpkgs/stable/#sec-language-ocaml) — `ocamlPackages` / `ocaml-ng`

## See also

- [Python / Node / Rust / Go](python-node-rust-go.md) — parallel survey for those four ecosystems
- [Haskell packaging](haskell-packaging.md) — `haskellPackages` and Cabal builders
- [Package sets](../architecture/package-sets.md) — nested scopes (`perlPackages`, language sets)
- [Fetchers and pinning](fetchers-and-pinning.md) — FODs and lock-style hashes
- [Language toolchains](../../11-development/language-toolchains.md) — shells vs packaging entry points
- [Simple package](simple-package.md) — Autotools/C-style baseline
