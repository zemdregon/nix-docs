---
status: complete
---

# Hermetic Builds

## Overview

A **hermetic build** runs in an isolated builder that may use only the inputs declared in the [derivation](../02-concepts/derivation.md). Nix enforces that with a **sandbox**: restricted filesystem views and (on Linux) private namespaces so undeclared tools, headers, and libraries cannot silently participate. The aim is **reproducibility and complete dependency graphs**, not a perfect security boundary against a compromised host.

That closes a common gap behind “works on my machine”—where a build succeeds because `$PATH`, `/usr/include`, or a cached download happened to be present locally, but fails or behaves differently elsewhere. With the sandbox and declared inputs in place, the same derivation should produce the same store path on a laptop, in CI, or on a **remote builder**, given the same inputs. How that relates to evaluation purity and bit-for-bit goals is covered in [purity and reproducibility](purity-and-reproducibility.md); this page focuses on the build-time isolation mechanism.

## Details

### Declared inputs only

Each derivation lists its dependencies as store paths and sources. During the build, the sandbox mounts those paths (and a minimal set of bind mounts from `sandbox-paths`) and hides the rest of the host filesystem. If a build script calls `gcc`, `curl`, or a library that was not declared, the build fails rather than succeeding with an undeclared dependency. That makes the [closure](../02-concepts/closure.md) an honest account of what the build actually used.

### The `sandbox` setting

Isolation is controlled by the [`sandbox`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-sandbox) option in `nix.conf` (and matching CLI flags):

- `true` — builds run in a sandboxed environment: only declared store inputs, the temporary build directory, and configured `sandbox-paths` are visible. On Linux, builds also get private PID, mount, network, IPC, and UTS namespaces.
- `false` — no sandbox (weaker hermeticity; undeclared host files may leak in).
- `relaxed` — fixed-output derivations and derivations with `__noChroot = true` skip the sandbox; other builds remain sandboxed.

Default is `true` on Linux and `false` elsewhere. Sandboxing currently works on Linux and macOS; implementations differ. Deeper builder and platform detail lives in [builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md).

Remote builders use the same model: they receive a derivation and its input paths and run under the same sandbox rules, so offload is a performance choice, not different semantics.

### Fixed-output exceptions

Fetching upstream sources needs the network. Nix allows that only for [fixed-output derivations](../02-concepts/fixed-output-derivation.md) (FODs): on Linux they are **not** placed in a private network namespace, so they can reach the outside world. In exchange, the derivation must declare [`outputHash`](https://nix.dev/manual/nix/stable/language/advanced-attributes.html) (with `outputHashAlgo` / `outputHashMode` as required). If the built content does not match the declared hash, the build fails. Everything else in the closure stays content-addressed and fully sandboxed—no further network.

### Limits of the model

The sandbox targets **build reproducibility and complete dependency graphs**, not absolute isolation from a malicious or compromised host. Privilege, misconfiguration, `sandbox-paths` leaks, or sandbox bugs can still affect builds. For threat-model detail, see [sandbox escape surface](../14-security-and-trust/sandbox-escape-surface.md).

## Examples

**Undeclared tool on `$PATH`.** A `stdenv.mkDerivation` build script invokes `python3` without listing it in `nativeBuildInputs`. On a developer machine with Python installed globally, the script might appear to work; with `sandbox = true`, `python3` is unavailable and the build fails—surfacing the missing declaration.

**Same derivation locally and remotely.** You run `nix build` with `--builders 'ssh://buildfarm.example'` for a heavy package. The remote machine never sees your home directory; it receives the derivation and its store inputs, builds in the sandbox, and returns the output path. Matching inputs yield the same store path you would get locally.

**Pinned fetch via `outputHash`.** A `fetchurl` / `fetchFromGitHub` call is an FOD: Nix allows network access for that step only, checks content against the declared `outputHash` (and related `outputHashAlgo` / `outputHashMode`), and stores the result. Later build steps see a normal store path—no further network—and remain hermetic. If upstream changes the tarball, the hash check fails until you update the attribute.

## References

- [Nix manual — `sandbox` (nix.conf)](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-sandbox)
- [Nix manual — advanced attributes (`outputHash`)](https://nix.dev/manual/nix/stable/language/advanced-attributes.html)
- [Nix manual — derivations](https://nix.dev/manual/nix/stable/language/derivations.html)
- [nix.dev — Nix documentation home](https://nix.dev/)

## See also

- [Purity and reproducibility](purity-and-reproducibility.md)
- [Why Nix](why-nix.md)
- [Builders and sandboxes](../04-store-and-build/builders-and-sandboxes.md)
- [Fixed-output derivation](../02-concepts/fixed-output-derivation.md)
- [Derivation](../02-concepts/derivation.md)
