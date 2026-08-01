---
status: complete
last-checked: 2026-08
---

# Testing / NixOS VM Tests

## Overview

NixOS tests boot one or more QEMU VMs (or `systemd-nspawn` containers) from NixOS modules, then drive them with a Python `testScript`. In nixpkgs they live under `nixos/tests` and exercise service modules end-to-end; outside nixpkgs, `pkgs.testers.runNixOSTest` is the usual entry point. They are slower than package checks, but give high-confidence coverage of systemd and networking. Flake projects often wire them into `checks` (see [Checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md) and [CI with Nix](ci-with-nix.md)).

## Details

**Test module shape.** The whole test is a module. QEMU machines go in `nodes.<name>` (each value is a NixOS module); optional `containers.<name>` use nspawn. Shared config for every machine goes in `defaults` (or `nodeDefaults` / `containerDefaults`). The Python driver runs `testScript`: each node name becomes a Python object (`nodes.machine` → `machine`; invalid characters become underscores). Machines start on first action; use `start_all()` to bring multi-node tests up in parallel. Common APIs from the NixOS manual: `succeed` / `fail`, `wait_for_unit`, `wait_for_open_port`, `wait_until_succeeds`, `copy_from_host`, and `t` for `unittest.TestCase` assertions. Prefer those wait helpers over fixed `sleep` when a service or port is ready asynchronously.

**VMs vs containers.** QEMU nodes run a separate kernel (needed for kernel features, X11, many systemd namespace options, specialisations, setuid). Containers share the host kernel, start faster, use less RAM, and work more easily in nested CI—but need host Nix settings (`auto-allocate-uids`, `uid-range`, `cgroups`). Mixed VM+container tests that share a VLAN also need `/dev/net` in the sandbox (`nix.settings.sandbox-paths = [ "/dev/net" ]` on the builder host).

**Where they run.** Inside nixpkgs, register tests in `nixos/tests/all-tests.nix` and build `nixosTests.<name>` (e.g. `nix-build -A nixosTests.hostname`). Outside nixpkgs:

```nix
pkgs.testers.runNixOSTest {
  imports = [ ./test.nix ];
  # optional defaults / package overrides
}
```

`runNixOSTest` returns a derivation that runs the test, pins the current `pkgs` set, and makes `nixpkgs.*` options read-only. Packages link integration coverage via `passthru.tests` and the `nixosTests` argument (see [Tests and passthru](../06-nixpkgs/packaging/tests-and-passthru.md)).

**When to use a VM test vs a package check.** Prefer cheap package-level checks (`checkPhase`, `testers.testVersion`, small `passthru.tests` derivations) when you only need “binary installs and runs.” Use a NixOS VM/container test when the failure mode is module merge, systemd unit activation, multi-host networking, or service integration that only appears in a real NixOS system. Nixpkgs documents that NixOS tests are slower than regular package tests; wire the same `nixosTests.*` attr into `passthru.tests` so OfBorg (and local `nix-build -A pkg.tests`) can run it when the package changes—without making every package rebuild pay VM cost.

**Requirements and debugging.** QEMU nodes need `kvm` (or `apple-virt` on macOS; Linux builder required there). Features are autodetected locally (`apple-virt` since Nix 2.19); remote builders need `supportedFeatures` configured. Expect minutes per test. For authoring, build `.driverInteractive` and run `./result/bin/nixos-test-driver` for a Python REPL (`test_script()`, `machine.shell_interact()`). Container machines need root for interactive runs (`sudo ./result/bin/nixos-test-driver`). Evaluation issues while authoring modules: [Debugging evaluation](debugging-evaluation.md). Module and service patterns: [Writing a module](../09-nixos/modules/writing-a-module.md), [Service patterns](../09-nixos/services/service-patterns.md).

**Failure modes.**

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| Build fails: missing `kvm` / no hardware virt | CI runner or nested VM without KVM; macOS without Linux builder | Use a runner with `/dev/kvm` (or nested virt enabled), set builder `supportedFeatures` to include `kvm`, or prefer `containers.*` where the host kernel is enough; on macOS enable a Linux builder (`nix.linux-builder` on nix-darwin) |
| Eval fails before QEMU starts | Module option clash, typo, wrong `pkgs` in a node | Fix the NixOS modules; `--show-trace` / REPL — [Debugging evaluation](debugging-evaluation.md) |
| Test hangs or times out on `wait_for_*` | Service never reaches active / port never opens; race | Wait on the real unit or port; raise only with the documented `timeout=` args; debug with `.driverInteractive` and `machine.shell_interact()` |
| Eval is very slow or pulls IFD | Nodes import full NixOS; IFD during module eval | Keep test modules lean; avoid [import from derivation](../02-concepts/import-from-derivation.md) in the test graph; see [Lazy trees and eval perf](lazy-trees-and-eval-perf.md) |
| Mixed VM + nspawn VLAN fails in sandbox | TAP bridge needs `/dev/net` | Add `/dev/net` to sandbox paths on the host (manual: `nix.settings.sandbox-paths`) |
| Container-only test fails on host | Missing `auto-allocate-uids` / `uid-range` / `cgroups` | Configure those Nix daemon settings as in the NixOS manual System Requirements |

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

Wire that derivation into flake `checks` so `nix flake check` builds it (illustrative; needs `nix-command` / `flakes`). Same pattern as other check derivations in [Checks and hydraJobs](../07-flakes/workflows/checks-and-hydraJobs.md)—CI must have virt features or the check will fail:

```nix
{
  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      checks.${system}.hello-vm = pkgs.testers.runNixOSTest (
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
      );
    };
}
```

Interactive debug: `nix-build -A someTest.driverInteractive` then `./result/bin/nixos-test-driver` (or `nix build .#checks.<system>.hello-vm.driverInteractive` when exposed that way).

## References

- [NixOS manual — NixOS Tests](https://nixos.org/manual/nixos/stable/index.html#sec-nixos-tests) — primary: modules, `nodes` / `containers`, `testScript`, VMs vs nspawn, system requirements, interactive driver
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
