---
status: complete
---

# Scientific computing and HPC

## Overview

Scientific and HPC workloads on Nix depend on **one coherent package set** for MPI, BLAS, and LAPACK. Nixpkgs exposes generic attributes (`mpi`, `blas`, `lapack`) so dependents link against a site-wide choice; you switch implementations with [overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md), not by mixing libraries at runtime. Interactive work uses [dev shells](shells-and-direnv.md); large sites pin nixpkgs, apply overlays, and lean on [binary caches](../04-store-and-build/binary-caches.md) and [remote builders](../04-store-and-build/remote-builders.md) when rebuilds are unavoidable.

This page covers MPI/BLAS/LAPACK switching, the modules-vs-Nix pattern, and community site overlays. GPU/ML stacks are covered in [CUDA, ROCm, and ML stacks](cuda-rocm-ml.md). Job schedulers (Slurm, etc.) are out of scope: Nix supplies the software tree; the cluster still schedules jobs.

## Details

### MPI

Packages built with MPI support take the generic attribute `mpi` as an input. Nixpkgs ships native implementations:

| Implementation | Attribute | Notes |
|----------------|-----------|-------|
| Open MPI | `openmpi` | Default provider for `mpi` |
| MPICH | `mpich` | Common site choice |
| MVAPICH | `mvapich` | Third native implementation in nixpkgs |

Switch site-wide by overriding `mpi` in an overlay so every MPI-enabled package rebuilds against the same implementation. Do not mix Open MPI and MPICH in one coherent `pkgs`—ABI and wrapper behavior differ.

### BLAS and LAPACK

Packages should depend on the generic attributes `blas` and `lapack`, not on a specific implementation directly. Default LP64 BLAS uses OpenBLAS via `openblasCompat`; ILP64 OpenBLAS is `openblas`. Providers are selected via `blasProvider` and `lapackProvider` on those wrappers (manual examples cover OpenBLAS, reference LAPACK, BLIS, AMD BLIS/LIBFLAME, Intel MKL).

**LP64 vs ILP64:** `blas` and `lapack` are LP64 (32-bit integer interface) by default. ILP64 variants are `blas-ilp64` and `lapack-ilp64`. Check `blas.isILP64` / `lapack.isILP64` when software cannot tolerate ILP64; some derivations assert `(!blas.isILP64)`.

**MKL:** Intel MKL (`mkl`) is an unfree provider on `x86_64-linux` and `x86_64-darwin`. Hydra does not build or distribute pre-compiled binaries that use MKL—expect local or cache-backed rebuilds when you switch to it.

As with MPI, one BLAS/LAPACK provider per package set avoids subtle link-time and runtime conflicts.

### Environment modules vs Nix

Traditional HPC sites use **environment modules** (Lmod, Environment Modules/Tcl) to stack compilers, MPI, and math libraries per session. Nix has no drop-in Lmod replacement in nixpkgs core; the analogue is declarative composition:

- **Overlays** — site-wide MPI/BLAS/LAPACK (and other) choices on one `pkgs`
- **Dev shells** — `mkShell` / flake `devShells` for interactive stacks pinned to a project
- **Multiple instantiations** — separate `import nixpkgs { overlays = [ … ]; }` calls when you truly need parallel stacks (e.g. Open MPI vs MPICH jobs), not ad-hoc `module load` mixing inside one environment

Prefer one pinned nixpkgs revision per deployment; see [language toolchains](language-toolchains.md) for the same “one package set, one ABI story” rule for compilers.

### Site overlays (community pattern)

Research groups often publish **overlay layers** on top of nixpkgs rather than forking the tree. [NixOS-QChem](https://github.com/Nix-QChem/NixOS-QChem) is a representative example: chemistry/QM packages live under a `qchem` attrset, with `release-XX.XX` branches tracking nixpkgs releases, flake access for free packages, and a public Cachix (`nix-qchem.cachix.org`, key in their README). Treat such repos as **community overlays**, not nixpkgs core—pin the branch/input, read their overlay wiring, and add their cache if you consume their binaries.

For overlay mechanics, see [Writing overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md) and the [overlay concept](../02-concepts/overlay.md).

### Practical HPC notes

- **Pin nixpkgs** (flake input, channel, or `fetchTarball`) so MPI/BLAS choices and rebuild sets stay reproducible.
- **Keep one MPI and one BLAS/LAPACK provider** per `pkgs` instantiation used on a cluster image or shared store.
- **Shells for login nodes:** `mkShell` / `devShells` expose tools without polluting system profiles; pair with [direnv](../05-cli-and-tooling/adjacent-tools/direnv-nix-direnv.md) where useful ([shells and direnv](shells-and-direnv.md)).
- **Rebuilds at scale:** switching MPI or MKL invalidates large downstream graphs; configure [remote builders](../04-store-and-build/remote-builders.md) and [binary caches](../04-store-and-build/binary-caches.md) before rolling site overlays cluster-wide.

## Examples

Site overlay switching MPI to MPICH and BLAS/LAPACK to MKL (MKL only where `mkl` is available; unfree may need `config.allowUnfree`):

```nix
final: prev: {
  mpi = final.mpich;

  blas = prev.blas.override { blasProvider = final.mkl; };
  lapack = prev.lapack.override { lapackProvider = final.mkl; };
}
```

Apply via `import nixpkgs { overlays = [ mpiMpichMkl ]; }` or an equivalent flake `pkgs` input. All MPI- and BLAS-using packages in that instantiation must rebuild.

## See also

- [Shells and direnv](shells-and-direnv.md) — interactive dev environments
- [Language toolchains](language-toolchains.md) — compilers and builders in shells vs packaging
- [CUDA, ROCm, and ML stacks](cuda-rocm-ml.md) — GPU-accelerated scientific/ML workloads
- [Writing overlays](../06-nixpkgs/overlays-and-overrides/writing-overlays.md) — overlay shape and `final` / `prev`
- [Overlay](../02-concepts/overlay.md) — fixed-point package-set extension
- [Remote builders](../04-store-and-build/remote-builders.md) — offload large rebuilds
- [Binary caches](../04-store-and-build/binary-caches.md) — share built artifacts

## References

- [Nixpkgs manual — Switching the MPI implementation](https://nixos.org/manual/nixpkgs/unstable/#sec-overlays-alternatives-mpi)
- [Nixpkgs manual — BLAS/LAPACK alternatives](https://nixos.org/manual/nixpkgs/unstable/#sec-overlays-alternatives-blas-lapack)
- [NixOS-QChem](https://github.com/Nix-QChem/NixOS-QChem) — community chemistry/QM overlay and cache
