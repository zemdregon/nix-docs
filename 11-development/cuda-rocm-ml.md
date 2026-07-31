---
status: complete
---

# CUDA, ROCm, and ML stacks

## Overview

GPU-accelerated machine learning on Nix goes through **nixpkgs configuration**: CUDA redistributables are **unfree**, CUDA is **off by default**, and many ML packages optionally build with or without GPU support via `config.cudaSupport` / `config.rocmSupport`. You pick a **CUDA package set** (`cudaPackages` and versioned aliases), enable the right **config** flags, and—when possible—use **scoped variants** (`pkgsCuda`, `pkgsForCudaArch.*`, and for AMD `pkgsRocm`) instead of turning GPU support on globally.

Enabling `cudaSupport` or `rocmSupport` on a full `pkgs` instantiation can trigger a **mass rebuild** (Nixpkgs config docs); matching **substituters** are often limited for unfree GPU builds, so local compilation or community/private caches are common. The **NVIDIA driver stack** on the host is separate from nixpkgs CUDA redistributables—packaging CUDA libs does not install drivers.

Interactive work belongs in [dev shells](shells-and-direnv.md); Python ML packaging patterns live in [Python / Node / Rust / Go](../06-nixpkgs/packaging/python-node-rust-go.md). CPU/HPC MPI/BLAS switching is in [Scientific computing and HPC](scientific-and-hpc.md).

## Details

### CUDA package sets

Nixpkgs exposes versioned CUDA package sets with predictable names:

| Attribute | Meaning |
|-----------|---------|
| `cudaPackages_x_y` | A specific major.minor CUDA release |
| `cudaPackages_x` | Latest widely supported release in major series `x` |
| `cudaPackages` | Unversioned alias to the default set (preferred) |

Prefer unversioned **`cudaPackages`**. Versioned sets such as `cudaPackages_12_8` exist for pinning, but older versioned sets are **periodically removed** when upstream drops them.

The default **`cudaPackages`** alias may lag the newest upstream release when core packages (PyTorch, OpenCV, …) fail to build against it—the manual gives examples where `cudaPackages_12` or `cudaPackages` stay on an older minor/major until the graph is healthy again.

Each set includes redistributables (`libcublas`, `cudnn`, `tensorrt`, `nccl`, …). The monolithic `cudaPackages.cudatoolkit` join is discouraged for new work; use individual redistributables from `cudaPackages` instead (Nixpkgs manual).

### Enabling CUDA in nixpkgs

CUDA support is not on by default. Import nixpkgs with configuration along these lines (from the [CUDA user guide](https://nixos.org/manual/nixpkgs/unstable/#cuda-configuring-nixpkgs-for-cuda)):

```nix
{ pkgs }:
{
  allowUnfreePredicate = pkgs._cuda.lib.allowUnfreeCudaPredicate;
  cudaCapabilities = [ /* e.g. "8.9" */ ];
  cudaForwardCompat = true;
  cudaSupport = true;
}
```

Most CUDA packages are unfree, so set **`allowUnfreePredicate`** (narrower) or **`allowUnfree`** (broader). **`cudaCapabilities`** limits device code generation (smaller closures, faster compiles); omit it to use per-set defaults. **`cudaForwardCompat`** controls PTX for future hardware.

**`cudaSupport`** is the global switch packages consult when they can build with or without CUDA. Changing it on a full `pkgs` instantiation causes a **mass rebuild** (config option docs). Prefer **`pkgsCuda`** or per-package overrides when you only need a few CUDA-enabled tools.

### Scoped variants (prefer over global enable)

| Variant | Role |
|---------|------|
| `pkgsCuda` | Full nixpkgs with `cudaSupport = true`, `rocmSupport = false` |
| `pkgsRocm` | Full nixpkgs with `rocmSupport = true`, `cudaSupport = false` (nixpkgs variant; not covered in the CUDA user guide) |
| `pkgsForCudaArch.sm_89` (etc.) | Nixpkgs variant targeting one architecture; sets `cudaForwardCompat = false` |
| `cudaPackages_X.pkgs` | nixpkgs where that CUDA set is the default (reduces package-set leakage) |

Examples from the manual: `pkgs.pkgsCuda.python3Packages.torch`, `pkgsForCudaArch.sm_89.opencv`, `cudaPackages_12_8.pkgs.opencv`. Each variant **re-evaluates nixpkgs**—import once with the desired config when you can.

Architecture-specific sets may be useless if the default CUDA release does not support that capability (e.g. Blackwell on an older default set); you may need a newer `cudaPackages_* .pkgs` path instead.

### Packaging expressions that use CUDA

Give derivations a **`cudaPackages`** parameter (and optional **`config`** / **`cudaSupport`** when GPU support is optional). The manual strongly recommends:

```nix
{
  __structuredAttrs = true;
  strictDeps = true;
}
```

so CUDA setup hooks run correctly. Typical nixpkgs CUDA expressions add **`cudaPackages.cuda_nvcc`** to `nativeBuildInputs` and CUDA libraries to `buildInputs` (pattern seen in packaged derivations; the manual focuses on the attrs above). Pass a non-default set via `callPackage` only when necessary—overrides can leak mismatched CUDA versions across dependencies.

### ROCm (AMD)

ROCm uses the same config pattern: **`config.rocmSupport = true`** (off by default; also causes a mass rebuild when toggled globally) or the **`pkgsRocm`** variant (`rocmSupport = true`, `cudaSupport = false`). AMD libraries live under **`rocmPackages`**. There is no ROCm user guide section comparable to CUDA in the Nixpkgs manual—verify attribute paths against current nixpkgs rather than secondary write-ups.

### Binary caches and rebuilds

Default **`cache.nixos.org`** coverage for GPU-enabled paths is often limited compared with CPU-only builds, because many CUDA packages are unfree and Hydra does not publish the full graph. Enabling `cudaSupport` widely therefore **often** means local compilation unless you add a **community or private substituter** that builds those paths. Cache contents change over time—do not assume a specific package is cached. See [Binary caches](../04-store-and-build/binary-caches.md), [Signing and caches](../14-security-and-trust/signing-and-caches.md), and [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) for wiring extra caches.

### Dev shells

CUDA discoverability relies on nixpkgs **setup hooks**. The manual warns that **`devShell`** builds without manually invoking phases may fail to expose CUDA the same way a full derivation build does—prefer pulling CUDA libraries through normal `buildInputs` / `packages` and matching how packaged apps declare deps; see [Shells and direnv](shells-and-direnv.md).

### NixOS and containers

On NixOS, **`hardware.nvidia-container-toolkit.enable = true`** enables CDI generation for GPU access in Docker/Podman (`--device=nvidia.com/gpu=…`). That is the **container runtime integration**, not a substitute for installing the proprietary **driver** or for choosing `cudaPackages` in your dev/build config.

## Examples

Scoped CUDA for a Python ML shell (illustrative pin; needs compatible driver/GPU; build may not substitute):

```nix
# flake.nix (excerpt)
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.pkgsCuda.python3Packages.torch
        ];
      };
    };
}
```

Using `pkgsCuda` limits CUDA enablement to that attribute subtree instead of setting `config.cudaSupport = true` on the root import—still allow unfree licenses for NVIDIA redistributables.

## See also

- [Shells and direnv](shells-and-direnv.md) — `mkShell` / `nix develop` patterns
- [Language toolchains](language-toolchains.md) — compilers and package sets in shells
- [Python / Node / Rust / Go packaging](../06-nixpkgs/packaging/python-node-rust-go.md) — `python3Packages` builders (PyTorch, JAX, …)
- [Scientific computing and HPC](scientific-and-hpc.md) — MPI/BLAS site overlays (CPU-side HPC)
- [Binary caches](../04-store-and-build/binary-caches.md) — substituters and cache layout
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — adding private/community caches

## References

- [Nixpkgs manual — CUDA](https://nixos.org/manual/nixpkgs/unstable/#cuda)
- [Nixpkgs manual — Configuring Nixpkgs for CUDA](https://nixos.org/manual/nixpkgs/unstable/#cuda-configuring-nixpkgs-for-cuda)
- [Nixpkgs manual — Using `pkgsCuda`](https://nixos.org/manual/nixpkgs/unstable/#cuda-using-pkgscuda)
- [Nixpkgs manual — Using `pkgsForCudaArch`](https://nixos.org/manual/nixpkgs/unstable/#cuda-using-pkgsforcudaarch)
- [Nixpkgs manual — Using `cudaPackages`](https://nixos.org/manual/nixpkgs/unstable/#cuda-using-cudapackages)
- [Nixpkgs manual — Docker/Podman with CUDA](https://nixos.org/manual/nixpkgs/unstable/#cuda-docker-podman)
- [NixOS Wiki — CUDA](https://wiki.nixos.org/wiki/CUDA) (secondary; examples may lag the manual)
