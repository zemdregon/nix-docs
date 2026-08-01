---
status: complete
---

# Packaging builders

Dense map: ecosystem → Nixpkgs builder → FOD / hash knobs → wiki leaf. Prefer language builders over bare [`stdenv.mkDerivation`](../06-nixpkgs/architecture/mkDerivation.md). Canonical API: [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support). Stay inside one [package set](../06-nixpkgs/architecture/package-sets.md) scope. Cross: keep tools in `nativeBuildInputs` and libraries in `buildInputs` — [Cross compilation](../06-nixpkgs/packaging/cross-compilation.md).

## Builders and FOD knobs

| Ecosystem | Builder / entry | Hash / FOD knobs | Deep leaf |
|-----------|-----------------|------------------|-----------|
| Generic / Autotools | `stdenv.mkDerivation` | `src` via `fetchurl` / `fetchFromGitHub` / … (`hash`) | [Simple package](../06-nixpkgs/packaging/simple-package.md) · [Fetchers](../06-nixpkgs/packaging/fetchers-and-pinning.md) |
| Python | `buildPythonPackage`, `buildPythonApplication`; env: `python.withPackages` | `src` hash; deps from same `python3Packages` | [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Go | `buildGoModule` (versioned `buildGo*Module` when needed) | `vendorHash` (`null` if committed `vendor/`); `src` hash | [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Rust | `rustPlatform.buildRustPackage` | `cargoHash` **or** `cargoLock` (`lockFile` / …); `src` hash | [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Node / npm | `buildNpmPackage`; or `npmHooks` + `stdenv` | `npmDepsHash`; `src` hash | [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md) |
| Haskell | `haskellPackages.mkDerivation` / `callPackage` | Set pins one version per name (no Cabal solver); `jailbreak` / `doJailbreak` for bounds | [Haskell packaging](../06-nixpkgs/packaging/haskell-packaging.md) |
| Gradle / Java | Gradle setup hook + `mitmCache`; Ant + `jdk` / `javaPackages` | `mitmCache = gradle.fetchDeps { data = ./deps.json; … }`; refresh via `updateScript` | [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md) |
| PHP / Composer | `php.buildComposerProject2` | `vendorHash`; optional `composerLock` if lock missing from `src` | [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md) |
| Perl | `buildPerlPackage` in `perlPackages` | `src` hash (often `mirror://cpan/`); siblings from same set | [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md) |

**FOD loop:** placeholder / fake hash → build → copy reported SRI hash. Changing URL/`rev` without resetting the hash can serve stale store content — [Fetchers and pinning](../06-nixpkgs/packaging/fetchers-and-pinning.md).

## Shell vs package

| Goal | Reach for | Not a substitute for |
|------|-----------|----------------------|
| Reproducible package / CI | Language builder above | Host `pip` / `cargo` / `npm` / `go` alone |
| Day-to-day edit | `mkShell` + compilers from nixpkgs | Packaging FODs and install layout |

Map of shell tools vs builders: [Language toolchains](../11-development/language-toolchains.md). Nested sets (`python3Packages`, `haskellPackages`, …): [Package sets](../06-nixpkgs/architecture/package-sets.md).

## Failure callouts

| Symptom / mistake | Fix |
|-------------------|-----|
| `hash mismatch in fixed-output derivation` (src / vendor / npm / cargo) | Reset the FOD hash after URL/`rev`/lock changes; copy the reported SRI — [Fetchers and pinning](../06-nixpkgs/packaging/fetchers-and-pinning.md) |
| Haskell Cabal version-bound / dependency check fails | Set pins one version; `jailbreak` / `doJailbreak` lifts bounds only (still no solver) — [Haskell packaging](../06-nixpkgs/packaging/haskell-packaging.md) |
| Gradle deps / `mitmCache` fail; PHP `vendorHash` mismatch | Refresh `deps.json` via `mitmCache.updateScript`, or re-pin Composer `vendorHash` / lock — [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md) |
| Works native, breaks under cross | Tools in `nativeBuildInputs`, libraries in `buildInputs`; try `strictDeps` — [Cross compilation](../06-nixpkgs/packaging/cross-compilation.md) |
| Mixing package-set scopes (wrong Python/GHC/…) | Depend on siblings from the same set — [Package sets](../06-nixpkgs/architecture/package-sets.md) |

## See also

- [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md)
- [Haskell packaging](../06-nixpkgs/packaging/haskell-packaging.md)
- [JVM / PHP and others](../06-nixpkgs/packaging/jvm-php-and-others.md)
- [Simple package](../06-nixpkgs/packaging/simple-package.md)
- [Cross compilation](../06-nixpkgs/packaging/cross-compilation.md)
- [Fetchers and pinning](../06-nixpkgs/packaging/fetchers-and-pinning.md)
- [Language toolchains](../11-development/language-toolchains.md)
- [FAQ: common errors](faq-common-errors.md) — FOD / Gradle / Composer / Cabal symptoms

## References

- [Languages and frameworks](https://nixos.org/manual/nixpkgs/stable/#chap-language-support) — Nixpkgs manual chapter hub
- [Python](https://nixos.org/manual/nixpkgs/stable/#python)
- [Building Go modules with buildGoModule](https://nixos.org/manual/nixpkgs/stable/#ssec-language-go)
- [Compiling Rust applications with Cargo](https://nixos.org/manual/nixpkgs/stable/#compiling-rust-applications-with-cargo)
- [JavaScript / buildNpmPackage](https://nixos.org/manual/nixpkgs/stable/#javascript-buildNpmPackage)
- [Haskell](https://nixos.org/manual/nixpkgs/stable/#haskell)
- [Gradle](https://nixos.org/manual/nixpkgs/stable/#gradle) · [Building a Gradle package](https://nixos.org/manual/nixpkgs/stable/#building-a-gradle-package)
- [Building PHP projects](https://nixos.org/manual/nixpkgs/stable/#ssec-building-php-projects)
- [Perl](https://nixos.org/manual/nixpkgs/stable/#sec-language-perl)
