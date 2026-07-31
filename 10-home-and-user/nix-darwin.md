---
status: complete
---

# nix-darwin

## Overview

**nix-darwin** brings a NixOS-like [module system](../09-nixos/architecture/module-system.md) to macOS: declare system packages, services, defaults, and related settings in Nix, then activate with `darwin-rebuild`. It is **not** NixOS—there is no Linux systemd, no NixOS install ISO, and activation targets macOS mechanisms (notably **launchd** and macOS defaults) rather than a full Linux rootfs rebuild.

The project lives under the [nix-darwin](https://github.com/nix-darwin) org (`github:nix-darwin/nix-darwin`). Upstream positions it as “`/etc/nixos/configuration.nix` for macOS”: familiar module composition over Nixpkgs, aimed at declarative Mac system config. Maturity and coverage differ from NixOS—many options are Darwin-specific; consult the [reference manual](https://nix-darwin.github.io/nix-darwin/manual/index.html) rather than assuming NixOS option names work unchanged.

For the ecosystem role among other module stacks, see [module ecosystems: nix-darwin](../13-implementations/module-ecosystems/nix-darwin.md). For Nix on non-NixOS Linux, see [Nix on other distros](nix-on-other-distros.md).

## Details

### What it configures

Typical system-level concerns (exact options: see the manual):

- Packages on the system profile (`environment.systemPackages` and related environment options).
- **launchd** agents/daemons and other Darwin service wiring.
- macOS **defaults** (plist / `defaults`-style settings) where modules exist.
- Optional **Homebrew** integration (`homebrew.*`) that can drive `brew bundle` during activation—useful for casks and software not packaged in Nixpkgs; not required for a Nix-only setup.

User dotfiles and per-user environments are usually left to [Home Manager](home-manager/README.md), either standalone or as a nix-darwin module (below).

### Activation vs NixOS

| | NixOS | nix-darwin |
|---|--------|------------|
| Rebuild CLI | `nixos-rebuild` | `darwin-rebuild` |
| Flake output | `nixosConfigurations` | `darwinConfigurations` |
| Builder | `nixosSystem` | `darwinSystem` |
| Init / services | systemd | launchd (and Darwin activation scripts) |
| Scope | Full OS (kernel, modules, …) | macOS host config layered on Apple’s OS |

Same module *style* (options, `mkIf`, imports); different option set and activation backend. Flake-shaped cousins: [nixosConfigurations workflows](../07-flakes/workflows/nixos-configurations.md).

### Flakes and `darwin-rebuild`

Upstream recommends flakes for new setups. A flake exposes `darwinConfigurations.<name>` via `nix-darwin.lib.darwinSystem`. After `darwin-rebuild` is on `PATH`, apply with:

```bash
sudo darwin-rebuild switch --flake .#hostname
```

Replace `hostname` with the attr name in `darwinConfigurations` (commonly the machine’s LocalHostName from `scutil --get LocalHostName`). First install often uses `nix run` against the nix-darwin flake to invoke `darwin-rebuild` before it is installed locally—see the [project README](https://github.com/nix-darwin/nix-darwin#readme).

Set `nixpkgs.hostPlatform` to `aarch64-darwin` (Apple Silicon) or `x86_64-darwin` (Intel) in configuration.

### Home Manager

Home Manager ships a Darwin module: include `home-manager.darwinModules.home-manager` in the `darwinSystem` `modules` list, then set `home-manager.users.<name>`. System and user configs rebuild together on `darwin-rebuild switch`. Compare entry modes in [Standalone vs NixOS module](home-manager/standalone-vs-nixos-module.md) (the Darwin path is the macOS analogue of the NixOS module integration).

### Docs and version pins

- Online option reference: [nix-darwin manual](https://nix-darwin.github.io/nix-darwin/manual/index.html); locally `darwin-help` or `man 5 configuration.nix`.
- Release branches track Nixpkgs (e.g. `nix-darwin-26.05` alongside unstable/`master`)—pin flake inputs so nix-darwin and nixpkgs stay compatible.

## Examples

Minimal flake shape (hostname and modules are illustrative):

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs@{ self, nix-darwin, nixpkgs }: {
    darwinConfigurations."Johns-MacBook" = nix-darwin.lib.darwinSystem {
      modules = [ ./configuration.nix ];
    };
  };
}
```

Apply from the flake directory:

```bash
sudo darwin-rebuild switch --flake .#Johns-MacBook
```

With Home Manager as a Darwin module (abbreviated; see Home Manager’s nix-darwin flake docs for full flags):

```nix
# inside darwinSystem { modules = [ ... ]; }
home-manager.darwinModules.home-manager
{
  home-manager.useGlobalPkgs = true;
  home-manager.useUserPackages = true;
  home-manager.users.alice = ./home.nix;
}
```

## See also

- [Standalone vs NixOS module](home-manager/standalone-vs-nixos-module.md) — Home Manager entry modes (including Darwin module)
- [Nix on other distros](nix-on-other-distros.md) — Nix without NixOS on Linux
- [Module ecosystems: nix-darwin](../13-implementations/module-ecosystems/nix-darwin.md) — placement among module stacks
- [nixosConfigurations workflows](../07-flakes/workflows/nixos-configurations.md) — flake cousin on NixOS
- [NixOS module system](../09-nixos/architecture/module-system.md) — shared module mechanics

## References

- [nix-darwin/nix-darwin](https://github.com/nix-darwin/nix-darwin) — source, README, install/uninstall
- [nix-darwin site](https://nix-darwin.github.io/nix-darwin/) — project landing page
- [nix-darwin reference manual](https://nix-darwin.github.io/nix-darwin/manual/index.html) — options reference
- [Home Manager: nix-darwin flake module](https://nix-community.github.io/home-manager/index.xhtml#sec-flakes-nix-darwin-module) — `darwinModules.home-manager` integration
