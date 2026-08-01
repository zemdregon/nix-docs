---
status: complete
---

# nix-darwin

## Overview

**nix-darwin** brings a NixOS-like [module system](../09-nixos/architecture/module-system.md) to macOS: declare system packages, services, defaults, and related settings in Nix, then activate with `darwin-rebuild`. It is **not** NixOS—there is no Linux systemd, no NixOS install ISO, and activation targets macOS mechanisms (notably **launchd** and macOS defaults) rather than a full Linux rootfs rebuild.

The project lives under the [nix-darwin](https://github.com/nix-darwin) org (`github:nix-darwin/nix-darwin`). Upstream positions it as “`/etc/nixos/configuration.nix` for macOS”: familiar module composition over Nixpkgs, aimed at declarative Mac system config. Maturity and coverage differ from NixOS—many options are Darwin-specific; consult the [reference manual](https://nix-darwin.github.io/nix-darwin/manual/index.html) rather than assuming NixOS option names work unchanged.

For the ecosystem role among other module stacks, see [module ecosystems: nix-darwin](../13-implementations/module-ecosystems/nix-darwin.md). For Nix on non-NixOS Linux, see [Nix on other distros](nix-on-other-distros.md). Contrast (Linux guest / foreign OS, not Darwin modules): [WSL and foreign OS](wsl-and-foreign-os.md).

## Details

### What it configures

Typical system-level concerns (exact options: see the manual):

- Packages on the system profile (`environment.systemPackages` and related environment options).
- **launchd** agents/daemons and other Darwin service wiring.
- macOS **defaults** (plist / `defaults`-style settings) where modules exist.
- Optional **Homebrew** integration (`homebrew.*`) that can drive `brew bundle` during activation—useful for casks and software not packaged in Nixpkgs; not required for a Nix-only setup. `homebrew.enable` defaults to `false` and does not install Homebrew itself.

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

### Apple Silicon vs Intel

Set `nixpkgs.hostPlatform` in configuration to the machine’s Nix platform (upstream getting-started checklist):

| Hardware | `nixpkgs.hostPlatform` |
|----------|------------------------|
| Apple Silicon | `aarch64-darwin` |
| Intel | `x86_64-darwin` |

The option specifies where the nix-darwin configuration will run (manual: `nixpkgs.hostPlatform`). Prefer it over the older `nixpkgs.system` string when both are available. Wrong platform produces wrong-arch packages and build failures—match the Mac you activate on.

### Flakes and `darwin-rebuild`

Upstream recommends flakes for new setups. A flake exposes `darwinConfigurations.<name>` via `nix-darwin.lib.darwinSystem`. After `darwin-rebuild` is on `PATH`, apply with:

```bash
sudo darwin-rebuild switch --flake .#hostname
```

Replace `hostname` with the attr name in `darwinConfigurations` (commonly the machine’s LocalHostName from `scutil --get LocalHostName`). First install often uses `nix run` against the nix-darwin flake to invoke `darwin-rebuild` before it is installed locally—see the [project README](https://github.com/nix-darwin/nix-darwin#readme).

### Flake pins (nix-darwin ↔ nixpkgs)

Release branches track Nixpkgs. Illustrative pairing **as of 2026-08** (from the nix-darwin README; adjust when you upgrade):

| Track | nix-darwin input | Typical nixpkgs input |
|-------|------------------|------------------------|
| Unstable | `github:nix-darwin/nix-darwin/master` | `github:NixOS/nixpkgs/nixpkgs-unstable` |
| 26.05 | `github:nix-darwin/nix-darwin/nix-darwin-26.05` | `github:NixOS/nixpkgs/nixpkgs-26.05-darwin` |

Pin both inputs and keep them on matching tracks. Use `nix-darwin.inputs.nixpkgs.follows = "nixpkgs"` so nix-darwin evaluates against *your* nixpkgs pin rather than a second, drifting copy. Mismatched release lines (e.g. `nix-darwin-26.05` with a random unstable nixpkgs, or the reverse) are a common source of eval and module breakage.

Template init mirrors the same tracks: `nix flake init -t nix-darwin/master` vs `nix flake init -t nix-darwin/nix-darwin-26.05`.

### Home Manager

Home Manager ships a Darwin module: include `home-manager.darwinModules.home-manager` in the `darwinSystem` `modules` list, then set `home-manager.users.<name>`. System and user configs rebuild together on `darwin-rebuild switch`. Compare entry modes in [Standalone vs NixOS module](home-manager/standalone-vs-nixos-module.md) (the Darwin path is the macOS analogue of the NixOS module integration). Full flake wiring: [Home Manager — nix-darwin module](https://nix-community.github.io/home-manager/index.xhtml#sec-flakes-nix-darwin-module).

Common companion options (same names as the NixOS HM module path):

- `home-manager.useGlobalPkgs` — share the system `pkgs` with Home Manager.
- `home-manager.useUserPackages` — install user packages into the user profile.
- `home-manager.extraSpecialArgs` — pass flake `inputs` (or other values) into `home.nix`.

Standalone Home Manager remains valid on macOS if you want user config on a different cadence than `darwin-rebuild`.

### Common failure modes

- **Activation needs elevated privileges.** Upstream install and switch examples use `sudo darwin-rebuild switch` (and `sudo nix run …#darwin-rebuild -- switch` before `darwin-rebuild` is on `PATH`). Privilege errors usually mean the command was run without that elevation.
- **Wrong flake attribute.** `--flake .#name` must match a key under `darwinConfigurations`. Upstream expects that name to match `scutil --get LocalHostName` when following the getting-started sed/rename flow; a typo or ComputerName vs LocalHostName mix-up yields “attribute missing” style failures.
- **Assuming systemd / NixOS options.** Services and timers are **launchd**-backed. Do not copy `systemd.services.*` or other Linux-only NixOS options into Darwin configs; look up Darwin option names in the nix-darwin manual.
- **Homebrew is optional.** Enabling `homebrew.*` is not required for a working Nix-only system. When used, `homebrew.enable` manages Brewfile-driven installs during activation; Homebrew must already be installed separately (manual note on `homebrew.enable`).
- **Input skew.** See [Flake pins](#flake-pins-nix-darwin--nixpkgs)—unfollowed or cross-track nixpkgs/nix-darwin pins cause hard-to-debug eval errors.

### Docs and local help

- Online option reference: [nix-darwin manual](https://nix-darwin.github.io/nix-darwin/manual/index.html); locally `darwin-help` or `man 5 configuration.nix`.

## Examples

Minimal flake shape (hostname and modules are illustrative; pin pair as of 2026-08):

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs@{ self, nix-darwin, nixpkgs }: {
    darwinConfigurations."Johns-MacBook" = nix-darwin.lib.darwinSystem {
      modules = [
        ./configuration.nix
        # configuration.nix should set nixpkgs.hostPlatform
        # to "aarch64-darwin" or "x86_64-darwin"
      ];
    };
  };
}
```

Apply from the flake directory:

```bash
sudo darwin-rebuild switch --flake .#Johns-MacBook
```

With Home Manager as a Darwin module (illustrative; see [HM nix-darwin flake docs](https://nix-community.github.io/home-manager/index.xhtml#sec-flakes-nix-darwin-module) for the full template):

```nix
# flake inputs also need home-manager; then inside darwinSystem:
modules = [
  ./configuration.nix
  home-manager.darwinModules.home-manager
  {
    home-manager.useGlobalPkgs = true;
    home-manager.useUserPackages = true;
    home-manager.extraSpecialArgs = { inherit inputs; };
    home-manager.users.alice = ./home.nix;
  }
];
```

## See also

- [Standalone vs NixOS module](home-manager/standalone-vs-nixos-module.md) — Home Manager entry modes (including Darwin module)
- [Nix on other distros](nix-on-other-distros.md) — Nix without NixOS on Linux
- [WSL and foreign OS](wsl-and-foreign-os.md) — foreign Linux / NixOS-WSL contrast (not Darwin)
- [Module ecosystems: nix-darwin](../13-implementations/module-ecosystems/nix-darwin.md) — placement among module stacks
- [nixosConfigurations workflows](../07-flakes/workflows/nixos-configurations.md) — flake cousin on NixOS
- [NixOS module system](../09-nixos/architecture/module-system.md) — shared module mechanics
- [nix-darwin with Home Manager](../16-configuration-examples/nix-darwin-with-home-manager.md) — worked Darwin + HM flake walkthrough

## References

- [nix-darwin/nix-darwin](https://github.com/nix-darwin/nix-darwin) — source, README, install/uninstall
- [nix-darwin site](https://nix-darwin.github.io/nix-darwin/) — project landing page
- [nix-darwin reference manual](https://nix-darwin.github.io/nix-darwin/manual/index.html) — options reference (`nixpkgs.hostPlatform`, `homebrew.*`, …)
- [Home Manager: nix-darwin flake module](https://nix-community.github.io/home-manager/index.xhtml#sec-flakes-nix-darwin-module) — `darwinModules.home-manager` integration
