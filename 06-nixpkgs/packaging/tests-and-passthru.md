---
status: complete
---

# Tests and passthru

## Overview

[`passthru`](../architecture/mkDerivation.md) attaches extra attributes to a package value without affecting the build. Consumers read them as `package.foo` (for example `hello.tests`). They are **not** passed to the derivation builder, so changing `passthru` alone does not rebuild the package—similar to [`meta`](../architecture/mkDerivation.md).

The most important convention is **`passthru.tests`**: an attrset of test derivations that exercise the built package as a downstream consumer. That complements, rather than replaces, upstream test suites run during [`checkPhase`](../../04-store-and-build/build-phases.md) and related stdenv hooks.

## Details

### What `passthru` is for

Use `passthru` when you need data or helper derivations on the package record that are not build inputs:

| Pattern | Purpose |
|---------|---------|
| `passthru.tests` | Attrset of test derivations (`version`, `smoke`, …) |
| `passthru.updateScript` | Script or derivation for bumping versions (used by update bots) |
| `passthru.withPackages` / `withPlugins` | Ecosystem helpers that wrap the package with extra modules or plugins |

Anything in `passthru` is visible on the final package after `mkDerivation` returns. It does not participate in input hashing for the main derivation.

### `passthru.tests` vs `checkPhase`

**During the build**, stdenv still runs upstream unit tests when appropriate:

- **`doCheck = true`** enables [`checkPhase`](../../04-store-and-build/build-phases.md) (typically `make check`) after `buildPhase`.
- **`doInstallCheck = true`** enables `installCheckPhase` after install.
- Hooks such as **`versionCheckHook`** assert the installed binary reports the expected version.

Those phases run inside the same derivation as the compile/install steps. Failures fail the package build; successes add build time to every consumer of that derivation.

**After the build**, `passthru.tests` holds separate derivations that depend on the package output:

- Each test is its own derivation; success means the test script exits 0 and produces `$out`.
- Tests run the package **as a consumer** would—CLI smoke tests, small integration scripts, NixOS VM tests wired as dependencies.
- Changing a test derivation does **not** rebuild the package; only the test job reruns.
- You opt in explicitly: `nix-build -A hello.tests` or `nix-build -A hello.tests.version`.

Because Hydra and [nixpkgs-review](https://github.com/Mic92/nixpkgs-review) do not build `passthru.tests` by default, local and CI runs must request them. **Ofborg** on Nixpkgs pull requests builds `passthru.tests` for packages touched in the PR. Flake-based projects often expose similar test derivations under [`checks`](../../07-flakes/workflows/checks-and-hydraJobs.md) instead.

### Referencing the package inside tests

When defining tests in the same `mkDerivation` call, prefer **`finalAttrs.finalPackage`** so overrides and `finalAttrs` fields resolve correctly:

```nix
stdenv.mkDerivation (finalAttrs: {
  pname = "example";
  version = "1.0.0";
  # … src, buildInputs, etc.

  passthru.tests = {
    version = testers.testVersion {
      package = finalAttrs.finalPackage;
    };
  };
})
```

Using `finalPackage` avoids stale self-references when attributes are overridden and matches the fixed-point style documented on [mkDerivation](../architecture/mkDerivation.md). For a trivial version smoke test that must fail the package build itself, prefer `versionCheckHook` over `passthru.tests` (see the manual’s [passthru.tests](https://nixos.org/manual/nixpkgs/stable/#var-passthru-tests) notes).

### When to use which

| Concern | Prefer |
|---------|--------|
| Upstream’s own `make test` / unit suite | `doCheck`, `checkPhase`, or language-specific test hooks |
| Installed-artifact checks that need `$out` | `installCheckPhase` or a `passthru.tests` entry |
| Fast CLI/version smoke test (CI/ofborg) | `passthru.tests` with `testers.testVersion` |
| Version check that must fail the package build | `versionCheckHook` (prefer over `passthru.tests` for that case) |
| Full integration or multi-machine scenario | `passthru.tests` with [NixOS VM tests](../../11-development/testing-nixos-vm-tests.md) or similar |
| Flake-local CI gate | `checks` output (see [checks and hydraJobs](../../07-flakes/workflows/checks-and-hydraJobs.md)) |

## Examples

Minimal package with a version smoke test:

```nix
{ lib, stdenv, fetchurl, testers }:

stdenv.mkDerivation (finalAttrs: {
  pname = "example";
  version = "1.0.0";

  src = fetchurl {
    url = "https://example.com/example-1.0.0.tar.gz";
    hash = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  };

  doCheck = true; # upstream unit tests during build

  passthru.tests = {
    version = testers.testVersion {
      package = finalAttrs.finalPackage;
    };
  };

  meta = with lib; {
    description = "Example tool";
    license = licenses.mit;
    platforms = platforms.all;
  };
})
```

Build the package and run all passthru tests:

```bash
nix-build -A example
nix-build -A example.tests
# or a single test:
nix-build -A example.tests.version
```

See [simple-package](simple-package.md) for the surrounding packaging walkthrough.

## See also

- [mkDerivation](../architecture/mkDerivation.md) — `passthru`, `finalAttrs.finalPackage`, and builder-visible attributes
- [Build phases](../../04-store-and-build/build-phases.md) — `checkPhase`, `installCheckPhase`, `doCheck`
- [checks and hydraJobs](../../07-flakes/workflows/checks-and-hydraJobs.md) — flake `checks` as an CI-facing test gate
- [Testing / NixOS VM tests](../../11-development/testing-nixos-vm-tests.md) — integration tests often wired through `passthru.tests`

## References

- Nixpkgs manual — [Passthru attributes](https://nixos.org/manual/nixpkgs/stable/#chap-passthru)
- Nixpkgs manual — [`passthru.tests`](https://nixos.org/manual/nixpkgs/stable/#var-passthru-tests)
- Nixpkgs manual — [Check phase](https://nixos.org/manual/nixpkgs/stable/#ssec-check-phase)
- Nixpkgs manual — [`testers.testVersion`](https://nixos.org/manual/nixpkgs/stable/#tester-testVersion)
