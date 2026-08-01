---
status: draft
---

# nix-ld and foreign binaries

## Overview

NixOS does not ship a traditional FHS dynamic linker at paths such as `/lib64/ld-linux-x86-64.so.2`. Prebuilt Linux binaries from vendors (`.deb` extracts, AppImages, language-ecosystem downloads, game launchers) often hardcode those paths and expect libraries under `/usr/lib`. **`programs.nix-ld`** installs a shim at the usual loader location; it forwards execution to the real linker from nixpkgs and maps `NIX_LD_LIBRARY_PATH` into `LD_LIBRARY_PATH` so many unpatched x86_64 glibc binaries run without a full per-command FHS environment. It is a pragmatic desktop convenience, not a substitute for packaging in nixpkgs when you need reproducibility, updates, or policy control.

## Details

**Why foreign binaries fail.** On typical Linux distributions, ELF executables point at a system-wide link loader and resolve shared libraries from fixed hierarchy paths. NixOS stores each package under `/nix/store` with its own interpreter and `RPATH`; there is no global `/lib` tree. An unpatched upstream binary therefore often fails immediately with “No such file or directory” (missing interpreter) or “error while loading shared libraries” (missing `.so`).

**What nix-ld does.** [nix-ld](https://github.com/nix-community/nix-ld) (integrated in nixpkgs since NixOS 22.05) places a small loader at `/lib64/ld-linux-x86-64.so.2` (and the 32-bit analogue on multilib setups). That shim reads `NIX_LD` (which dynamic linker in the store to use) and `NIX_LD_LIBRARY_PATH` (colon-separated library search paths), then execs the real loader with `LD_LIBRARY_PATH` set accordingly. The NixOS module sets those variables system-wide when enabled.

**`programs.nix-ld` options.** `programs.nix-ld.enable = true` turns on the shim and wires default loader paths. `programs.nix-ld.libraries` lists nixpkgs packages whose `lib/` outputs are merged into `NIX_LD_LIBRARY_PATH` — add packages here when a binary complains about a missing shared object; do not rely on `environment.systemPackages` alone for unpackaged binaries. `programs.nix-ld.package` selects the shim implementation (upstream defaults to the maintained `nix-ld-rs` merge). After the first enable, log out and back in (or reboot) so session environment picks up the new variables; library list changes apply on `nixos-rebuild switch`. Disable temporarily with `unset NIX_LD` in a shell.

**Finding missing libraries.** Run the binary and read the loader error, then map the `.so` name to a nixpkgs attribute — [nix-index / comma](../../05-cli-and-tooling/adjacent-tools/nix-index-comma.md) (`nix-locate`) is the usual workflow. Add the providing package to `programs.nix-ld.libraries`, not only to `environment.systemPackages`.

**Not security isolation.** Like [FHS wrappers](flatpak-and-fhs.md) (`buildFHSEnv`, `steam-run`), nix-ld only fixes filesystem expectations for the dynamic linker. The foreign process runs on the host with your user privileges and can read anything that user can. Trust the binary source; prefer [Flatpak](flatpak-and-fhs.md) when you want sandboxing and runtime updates.

**Alternatives (when to use something else).**

| Approach | Best for |
|----------|----------|
| **nix-ld** | Quick runs of many unpatched x86_64 binaries; dev tools that download prebuilt helpers |
| **Flatpak** | Sandboxed desktop apps from remotes; managed runtimes |
| **`buildFHSEnv` / `steam-run`** | One command or installer inside a synthetic `/usr` tree — see [Flatpak and FHS](flatpak-and-fhs.md) and [Gaming: Steam and Proton](gaming-steam-proton.md) |
| **Repackage in nixpkgs** | Production use, CI, shared machines, license tracking |
| **nix-alien** (community) | Adjacent helper for wrapping `.deb`/`.rpm` with auto dependency mapping — overlaps nix-ld use cases; evaluate maturity per package |

**Pro audio note (optional).** Desktop audio on NixOS usually goes through [PipeWire and audio](audio-pipewire.md). For pro-audio low-latency stacks, some users add the community **musnix** overlay alongside PipeWire/JACK; treat it as an optional, channel-specific add-on rather than core nix-ld documentation — verify overlay compatibility with your NixOS release before relying on it.

**Foreign distros vs NixOS.** On Debian, Fedora, and similar hosts, the system already provides FHS loaders; Nix coexists without nix-ld. The mismatch is specific to NixOS as the host OS — see [Nix on other distros](../../10-home-and-user/nix-on-other-distros.md).

## Examples

Enable the shim with a small library set (extend as binaries demand):

```nix
{ pkgs, ... }: {
  programs.nix-ld = {
    enable = true;
    libraries = with pkgs; [
      stdenv.cc.cc
      zlib
      openssl
    ];
  };
}
```

Locate a missing library and add the provider:

```bash
./vendor-binary
# error while loading shared libraries: libxkbcommon.so.0: cannot open shared object file

nix-locate lib/libxkbcommon.so.0
# → add libxkbcommon (or xorg.libxkbcommon on your channel) to programs.nix-ld.libraries
```

Per-shell override in a `shell.nix` (development without changing system config):

```nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  NIX_LD = pkgs.stdenv.cc.bintools.dynamicLinker;
  NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc
    pkgs.openssl
  ];
}
```

## See also

- [Flatpak and FHS](flatpak-and-fhs.md) — sandboxed apps vs `buildFHSEnv` / `steam-run`
- [Gaming: Steam and Proton](gaming-steam-proton.md) — Steam’s FHS environment and `steam-run`
- [PipeWire and audio](audio-pipewire.md) — default desktop audio stack
- [nix-index / comma](../../05-cli-and-tooling/adjacent-tools/nix-index-comma.md) — find which package owns a `.so` or binary
- [Nix on other distros](../../10-home-and-user/nix-on-other-distros.md) — no nix-ld needed when Nix is not the host OS

## References

- [NixOS options — `programs.nix-ld`](https://search.nixos.org/options?query=programs.nix-ld) — `enable`, `libraries`, `package`
- [NixOS Wiki — Nix-ld](https://wiki.nixos.org/wiki/Nix-ld) — enablement patterns and troubleshooting (secondary)
- [nix-community/nix-ld](https://github.com/nix-community/nix-ld) — shim behaviour, `NIX_LD` / `NIX_LD_LIBRARY_PATH` semantics
