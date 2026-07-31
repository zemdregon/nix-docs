---
status: complete
---

# Testing / NixOS VM Tests

## Overview

NixOS tests boot one or more QEMU VMs (or `systemd-nspawn` containers) from NixOS modules, then drive them with a Python `testScript`. In nixpkgs they live under `nixos/tests` and exercise service modules end-to-end; outside nixpkgs, `pkgs.testers.runNixOSTest` is the usual entry point. They are slower than package checks, but give high-confidence coverage of systemd and networking. Flake projects often wire them into `checks` (see [Checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) and [CI with Nix](ci-with-nix.md)).

## Details

**Test module shape.** The whole test is a module. QEMU machines go in `nodes.<name>` (each value is a NixOS module); optional `containers.<name>` use nspawn. Shared config for every machine goes in `defaults` (or `nodeDefaults` / `containerDefaults`). The Python driver runs `testScript`: each node name becomes a Python object (`nodes.machine` → `machine`; invalid characters become underscores). Machines start on first action; use `start_all()` to bring multi-node tests up in parallel. Common APIs: `succeed` / `fail`, `wait_for_unit`, `copy_from_host`, and `t` for `unittest.TestCase` assertions.

**VMs vs containers.** QEMU nodes run a separate kernel (needed for kernel features, X11, many systemd namespace options, specialisations, setuid). Containers share the host kernel, start faster, use less RAM, and work more easily in nested CI—but need host Nix settings (`auto-allocate-uids`, `uid-range`, `cgroups`). Mixed VM+container tests that share a VLAN also need `/dev/net` in the sandbox.

**Where they run.** Inside nixpkgs, register tests in `nixos/tests/all-tests.nix` and build `nixosTests.<name>` (e.g. `nix-build -A nixosTests.hostname`). Outside nixpkgs:

```nix
pkgs.testers.runNixOSTest {
  imports = [ ./test.nix ];
  # optional defaults / package overrides
}
```

`runNixOSTest` returns a derivation that runs the test, pins the current `pkgs` set, and makes `nixpkgs.*` options read-only. Packages link integration coverage via `passthru.tests` and the `nixosTests` argument (see [Tests and passthru](../06-nixpkgs/packaging/tests-and-passthru.md)).

**Requirements and debugging.** QEMU nodes need `kvm` (or `apple-virt` on macOS; Linux builder required there). Expect minutes per test. For authoring, build `.driverInteractive` and run `./result/bin/nixos-test-driver` for a Python REPL (`test_script()`, `machine.shell_interact()`). Evaluation issues while authoring modules: [Debugging evaluation](debugging-evaluation.md). Module and service patterns: [Writing a module](../09-nixos/modules/writing-a-module.md), [Service patterns](../09-nixos/services/service-patterns.md).

## Examples

Minimal single-node test with `runNixOSTest`. Shape matches the Nixpkgs manual’s `runNixOSTest` example (API details: NixOS manual [NixOS Tests](https://nixos.org/manual/nixos/stable/index.html#sec-nixos-tests)—do not invent driver methods beyond that chapter). **Not run offline here**—needs QEMU/`kvm` (or a Linux builder) and several minutes:

```nix
pkgs.testers.runNixOSTest (
  { lib, ... }:
  {
    name = "hello";
    nodes.machine =
      { pkgs, ... }:
      {
        environment.systemPackages = [ pkgs.hello ];
      };
    testScript = ''
      machine.succeed("hello")
    '';
  }
)
```

Expose that derivation from a flake `checks` attr, or `nix build` / `nix-build` the expression, to run the VM. Interactive debug: `nix-build -A someTest.driverInteractive` then `./result/bin/nixos-test-driver`.

## References

- [NixOS manual — NixOS Tests](https://nixos.org/manual/nixos/stable/index.html#sec-nixos-tests) — primary: modules, `nodes` / `containers`, `testScript`, VMs vs nspawn, interactive driver
- [Nixpkgs manual — Testers](https://nixos.org/manual/nixpkgs/stable/#chap-testers) — `pkgs.testers` helpers including `runNixOSTest`
- [Nixpkgs manual — `runNixOSTest`](https://nixos.org/manual/nixpkgs/stable/#tester-runNixOSTest) — out-of-tree entry point
- [Nixpkgs manual — NixOS tests (`passthru` / `nixosTests`)](https://nixos.org/manual/nixpkgs/stable/#var-passthru-tests-nixos) — linking package `passthru.tests` to VM tests

## See also

- [Tests and passthru](../06-nixpkgs/packaging/tests-and-passthru.md)
- [Writing a module](../09-nixos/modules/writing-a-module.md)
- [Service patterns](../09-nixos/services/service-patterns.md)
- [Checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md)
- [CI with Nix](ci-with-nix.md)
- [Debugging evaluation](debugging-evaluation.md)
