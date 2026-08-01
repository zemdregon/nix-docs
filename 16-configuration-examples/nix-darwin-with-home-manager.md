---
status: complete
last-checked: 2026-08
---

# nix-darwin with Home Manager

## Overview

This walkthrough wires [Home Manager](../10-home-and-user/home-manager/standalone-vs-nixos-module.md) into a [flake](../02-concepts/flake.md) as a **nix-darwin module**: one `darwinConfigurations.<name>` output evaluates macOS system modules and per-user home modules together, and a single `darwin-rebuild switch` activates both. That is the opposite of standalone [`homeConfigurations`](../07-flakes/workflows/home-configurations.md), where user profiles are built and switched with `home-manager switch` independently of the host.

The pattern fits a Mac where dotfiles should stay aligned with system packages and defaults, share one `pkgs` via `home-manager.useGlobalPkgs`, and ride the same [generation](../02-concepts/generation.md) cadence as nix-darwin. Pins below use **master** / **nixpkgs-unstable** as an illustrative unstable track (mid-2026); swap to matching **26.05** branches when you want a stable release line—see [nix-darwin](../10-home-and-user/nix-darwin.md#flake-pins-nix-darwin--nixpkgs).

## Details

### Domains composed

| Domain | Role in this example |
|--------|----------------------|
| [Flake (concept)](../02-concepts/flake.md) | Inputs, lock, and `darwinConfigurations` output |
| [homeConfigurations](../07-flakes/workflows/home-configurations.md) | Contrast only — not used when HM is embedded |
| [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md) | Flake cousin on NixOS (`nixos-rebuild`, not `darwin-rebuild`) |
| [Experimental flakes / nix-command](../08-experimental-features/flakes.md) | Required for `nix flake` and `--flake` rebuilds |
| [Module system](../09-nixos/architecture/module-system.md) | Shared option/import mechanics (different option tree on Darwin) |
| [Standalone vs NixOS module](../10-home-and-user/home-manager/standalone-vs-nixos-module.md) | Integration modes; Darwin path is the macOS analogue |
| [nix-darwin](../10-home-and-user/nix-darwin.md) | Activation, platform, pins, HM module import |
| [Module ecosystems: nix-darwin](../13-implementations/module-ecosystems/nix-darwin.md) | Placement among module stacks |

Home Manager’s flake integration is **experimental**; pin the `home-manager` input to a release branch that matches your Nixpkgs channel and review upstream notes before bumping. See [follows and overrides](../07-flakes/anatomy/follow-and-overrides.md) and [lockfile](../07-flakes/anatomy/lockfile.md).

### Differences from the NixOS + HM example

| | NixOS + HM | nix-darwin + HM (this page) |
|---|------------|----------------------------|
| Flake output | `nixosConfigurations.<host>` | `darwinConfigurations.<name>` |
| Builder | `nixpkgs.lib.nixosSystem` | `nix-darwin.lib.darwinSystem` |
| HM module | `home-manager.nixosModules.home-manager` | `home-manager.darwinModules.home-manager` |
| Activate | `sudo nixos-rebuild switch --flake .#<host>` | `sudo darwin-rebuild switch --flake .#<name>` |
| Services | systemd | **launchd** (Darwin activation scripts) |
| Platform | `system = "x86_64-linux"` (typical) | `nixpkgs.hostPlatform = "aarch64-darwin"` or `"x86_64-darwin"` |
| Accounts | Declared in `users.users` | Existing **macOS** login user; HM configures the home directory |

Do not copy NixOS-only options (`systemd.services.*`, kernel modules, etc.) into Darwin configs—look up Darwin names in the [nix-darwin manual](https://nix-darwin.github.io/nix-darwin/manual/index.html).

### Apple Silicon vs Intel

Set `nixpkgs.hostPlatform` in the system module to the machine you activate on (from the [nix-darwin getting-started checklist](../10-home-and-user/nix-darwin.md#apple-silicon-vs-intel)):

| Hardware | `nixpkgs.hostPlatform` |
|----------|------------------------|
| Apple Silicon | `aarch64-darwin` |
| Intel Mac | `x86_64-darwin` |

Wrong platform produces wrong-arch packages and build failures. Build and switch on the Mac itself unless you have a deliberate cross setup.

### Repository layout

A minimal mono-repo keeps the host entry thin and colocates the user module next to the machine (alternatives in [config repo layout](../07-flakes/workflows/config-repo-layout.md)):

```text
.
├── flake.nix
├── flake.lock
└── hosts/
    └── macbook/
        ├── default.nix          # Darwin entry: imports + HM wiring
        └── home.nix             # Home Manager module for one macOS user
```

There is no NixOS-style `hardware-configuration.nix` on macOS; machine-specific facts (hostname, platform) live in the host module.

### `flake.nix` (annotated)

```nix
{
  description = "nix-darwin host with embedded Home Manager";

  inputs = {
    # Pin Nixpkgs (unstable track — illustrative).
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    # Match nix-darwin branch to the same track (see nix-darwin README).
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";

    # Home Manager on the same Nixpkgs revision via follows.
    home-manager = {
      url = "github:nix-community/home-manager/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{ self, nix-darwin, nixpkgs, home-manager, ... }: {

    # Name commonly matches `scutil --get LocalHostName` (see Activate).
    darwinConfigurations."Johns-MacBook" = nix-darwin.lib.darwinSystem {
      modules = [
        ./hosts/macbook/default.nix
      ];
    };

  };
}
```

**Stable-track alternative** (pair branches, do not mix tracks):

```nix
nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-26.05-darwin";
nix-darwin.url = "github:nix-darwin/nix-darwin/nix-darwin-26.05";
home-manager.url = "github:nix-community/home-manager/release-26.05";
# … both nix-darwin and home-manager should follow "nixpkgs"
```

There is **no** `homeConfigurations` key for the embedded user — that output is for [standalone Home Manager](../07-flakes/workflows/home-configurations.md) only. The same `./home.nix` can be reused in a standalone config later; only the import and activation path change.

### `hosts/macbook/default.nix` (system + Home Manager wiring)

```nix
{ inputs, ... }:

{
  imports = [
    inputs.home-manager.darwinModules.home-manager
  ];

  # Required: match the Mac you rebuild on.
  nixpkgs.hostPlatform = "aarch64-darwin"; # or "x86_64-darwin"

  # Share the system pkgs with Home Manager modules.
  home-manager.useGlobalPkgs = true;
  # Install user packages into the usual user profile layout.
  home-manager.useUserPackages = true;
  # Pass flake inputs into home.nix (optional but common).
  home-manager.extraSpecialArgs = { inherit inputs; };

  # macOS user must already exist; HM configures /Users/<name>.
  home-manager.users.alice = import ./home.nix;

  # Illustrative system-level options — expand per role.
  environment.systemPackages = with pkgs; [ git ];
  services.nix-daemon.enable = true;
}
```

`home-manager.users.<name>` must match an existing macOS account. Unlike NixOS, nix-darwin does not create Unix users—you log in with the account Apple (or your org) already provisioned.

### `hosts/macbook/home.nix` (user environment)

```nix
{ pkgs, ... }:

{
  home.username = "alice";
  home.homeDirectory = "/Users/alice";
  home.stateVersion = "26.05"; # Set once; do not change casually.

  home.packages = with pkgs; [
    ripgrep
    jq
  ];

  programs.git = {
    enable = true;
    userName = "Alice Example";
    userEmail = "alice@example.org";
  };

  # programs.* / xdg.configFile patterns: see dotfiles guidance.
}
```

With `useGlobalPkgs = true`, `pkgs` in this module is the system package set. Program modules and file options follow normal Home Manager semantics; see [dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md) and [writing HM modules](../10-home-and-user/home-manager/writing-hm-modules.md).

### Activate

Enable experimental [`flakes`](../08-experimental-features/flakes.md) and [`nix-command`](../08-experimental-features/nix-command.md) in your Nix config before using flake rebuilds.

**First install** (before `darwin-rebuild` is on `PATH`): run `darwin-rebuild` via `nix run` against the nix-darwin input, with elevation—upstream install flow in the [nix-darwin README](https://github.com/nix-darwin/nix-darwin#readme). Illustrative:

```bash
sudo nix run github:nix-darwin/nix-darwin#darwin-rebuild -- switch --flake .#Johns-MacBook
```

**Routine switch** (from the flake directory, after `darwin-rebuild` is installed):

```bash
sudo darwin-rebuild switch --flake .#Johns-MacBook
```

Replace `Johns-MacBook` with the key under `darwinConfigurations`. Upstream getting-started flow expects that name to match `scutil --get LocalHostName` (not always the same as the friendly ComputerName shown in System Settings).

That one command builds the Darwin closure **and** activates Home Manager profiles for every `home-manager.users.*` entry. Do **not** run `home-manager switch` for this integration path—it maintains a separate generation line and can fight module-mode activation.

Optional checks before switching:

```bash
nix flake check
nix build .#darwinConfigurations.Johns-MacBook.config.system.build.toplevel
```

### Failure modes

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Permission denied / privilege errors | `darwin-rebuild switch` run without `sudo` | Use `sudo` as in upstream examples |
| Attribute missing on `--flake .#name` | Flake key ≠ `darwinConfigurations` entry or hostname mismatch | Align with `scutil --get LocalHostName`; fix typo |
| Wrong-arch or build failures | `nixpkgs.hostPlatform` does not match hardware | Set `aarch64-darwin` vs `x86_64-darwin` on the target Mac |
| HM option unknown / eval skew | `home-manager`, `nix-darwin`, or `nixpkgs` on mismatched tracks | Pin all three to the same release line; use `follows` |
| Two Nixpkgs checkouts / slow builds | Inputs not following root `nixpkgs` | Set `inputs.nixpkgs.follows = "nixpkgs"` on HM and nix-darwin |
| `home-manager.users` has no effect | Forgot `home-manager.darwinModules.home-manager` import | Add the module to `imports` or `modules` |
| Copied NixOS options fail | systemd / Linux-only modules on Darwin | Use nix-darwin manual options; **launchd**, not systemd |
| Duplicate or stale user packages | Ran `home-manager switch` alongside module mode | Use only `darwin-rebuild` for this setup |
| Collision on activation | Unmanaged file in `~` blocks symlinks | Migrate into config or use backup/`force` sparingly — [dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md) |

For user configs on a different cadence than system changes—or on a Mac without nix-darwin—use [`homeConfigurations`](../07-flakes/workflows/home-configurations.md) and `home-manager switch --flake .#<name>` instead; see [standalone vs NixOS module](../10-home-and-user/home-manager/standalone-vs-nixos-module.md).

## Examples

**Inline user module** instead of `import ./home.nix`:

```nix
home-manager.users.alice = { pkgs, ... }: {
  home.stateVersion = "26.05";
  programs.git.enable = true;
};
```

**Shared user module across hosts** (person follows the laptop, not the hardware):

```nix
# hosts/macbook/default.nix
home-manager.users.alice = import ../../users/alice/home.nix;
```

**Passing flake inputs into `home.nix`** when modules need custom flakes or sources:

```nix
# home.nix — inputs available because default.nix set home-manager.extraSpecialArgs
{ inputs, pkgs, ... }:
{
  # …
}
```

**Template from Home Manager upstream** (same wiring, different input names):

```bash
nix flake new ~/.config/darwin -t github:nix-community/home-manager#nix-darwin
```

## References

- [nix-darwin/nix-darwin](https://github.com/nix-darwin/nix-darwin) — source, README, install/uninstall, branch pairing
- [nix-darwin site](https://nix-darwin.github.io/nix-darwin/) — project landing page
- [nix-darwin reference manual](https://nix-darwin.github.io/nix-darwin/manual/index.html) — options reference (`nixpkgs.hostPlatform`, `homebrew.*`, …)
- [Home Manager — nix-darwin flake module](https://nix-community.github.io/home-manager/index.xhtml#sec-flakes-nix-darwin-module) — `darwinModules.home-manager` integration (experimental)
- [Home Manager manual — Nix Flakes](https://nix-community.github.io/home-manager/index.xhtml#ch-nix-flakes) — standalone, NixOS, and nix-darwin flake setups

## See also

- [nix-darwin](../10-home-and-user/nix-darwin.md) — activation, pins, platform, HM module overview
- [Standalone vs NixOS module](../10-home-and-user/home-manager/standalone-vs-nixos-module.md) — when to embed vs use `homeConfigurations`
- [homeConfigurations](../07-flakes/workflows/home-configurations.md) — standalone flake output and `home-manager switch`
- [NixOS with Home Manager](nixos-with-home-manager.md) — Linux system + user in one `nixos-rebuild`
- [nixosConfigurations](../07-flakes/workflows/nixos-configurations.md) — `nixosSystem` wiring (flake cousin)
- [Config repo layout](../07-flakes/workflows/config-repo-layout.md) — `hosts/`, `modules/`, `users/` conventions
- [Module ecosystems: nix-darwin](../13-implementations/module-ecosystems/nix-darwin.md) — ecosystem placement
- [Module system](../09-nixos/architecture/module-system.md) — how imported modules merge
- [Dotfiles patterns](../10-home-and-user/home-manager/dotfiles-patterns.md) — `programs.*`, collisions, secrets
- [Writing HM modules](../10-home-and-user/home-manager/writing-hm-modules.md) — composing user modules
- [Flake (concept)](../02-concepts/flake.md) — inputs, outputs, reproducibility
- [Generation (concept)](../02-concepts/generation.md) — what `switch` registers
- [Flakes (experimental feature)](../08-experimental-features/flakes.md) — enabling flake commands
- [nh / nixos-rebuild adjacent tools](../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md) — `nh darwin switch` as an optional frontend
