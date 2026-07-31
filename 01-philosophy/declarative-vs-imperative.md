---
status: complete
---

# Declarative vs Imperative

## Overview

Package and system management is either **imperative**—a sequence of mutations (`apt install`, editing files in place)—or **declarative**—a description of the desired end state that a tool realizes. Nix bets on the latter: you write what should exist; evaluation and activation compute how to get there.

The practical distinction is where the **source of truth** lives. Imperative workflows treat the live machine as the record of what happened. Declarative workflows treat a Nix expression (and the module system that evaluates it) as the record of what should exist. You still run rebuild and switch commands; those commands apply the description—they are not the description.

## Details

### Imperative mutation

Imperative tools change the current environment step by step. Each install, upgrade, or hand edit alters what is present now. The resulting state is the accumulated history of those mutations. There is no single checked-in artifact that fully specifies the system—only the live tree plus whatever notes or logs you kept. Reproducing the same setup elsewhere means replaying (or reinventing) that history.

Classic examples outside Nix: `apt install`, `pip install --user`, and editing `/etc` directly. Inside Nix, ad-hoc `nix-env` / `nix profile add` without a committed definition behaves the same way: the active [profile](../02-concepts/profile.md) is whatever you mutated last.

### Declarative end state

Declarative tools take a description of packages, services, users, and settings. NixOS configuration and the [module system](../09-nixos/modules/README.md) evaluate that description into a concrete system closure; activation then converges the machine to match. The expression states **what**; rebuild builds or substitutes the closure and switches to it.

Declarative does **not** mean “no CLI.” `nixos-rebuild switch`, `nix build`, and similar commands are how you ask Nix to realize the current expression. The authority remains the expression you version-control and review—not the transcript of commands you typed.

### Profiles, generations, and atomic switch

Nix makes the declarative model operational through [profiles](../02-concepts/profile.md) and [generations](../02-concepts/generation.md). Changing a definition and rebuilding produces a new generation; activating it updates which closure is current. Previous generations stay referenced until garbage-collected, so rollback is “point at the prior generation” rather than manually undoing installs. On NixOS, activation aims to switch the running system to the new generation as a unit—an **atomic** flip rather than piecemeal mutation of `/etc` and services. See [Immutability and rollback](immutability-and-rollback.md).

### Coexistence on the spectrum

The ecosystem is not all-or-nothing:

| Style | Typical tools / workflows |
|-------|---------------------------|
| More imperative | `nix-env`, ad-hoc `nix profile add` without a checked-in definition |
| More declarative | NixOS `configuration.nix`, Home Manager, flake `nixosConfigurations`, flake-defined [dev shells](../07-flakes/workflows/packages-apps-devShells.md) |

NixOS is the clearest declarative case: one evaluated configuration yields one system generation. Imperative profile installs remain available for exploration; lasting environments belong in an expression you can share and rebuild.

## Examples

**Imperative (mutate a profile):**

```bash
nix-env -iA nixpkgs.htop
nix-env -e htop   # remove later; state is whatever you ran last
```

Each command changes the active profile directly. Matching that set on another machine means repeating the commands or exporting a snapshot—not checking out a file.

**Declarative (NixOS fragment):**

```nix
# configuration.nix (fragment)
{ pkgs, ... }: {
  environment.systemPackages = [ pkgs.htop ];
}
```

After editing, `nixos-rebuild switch` builds a new generation that includes `htop`. The config—not the command history—is what you commit, review, and share. See [configuration.nix](../09-nixos/configuration/configuration-nix.md).

**Declarative (flake-named system):**

```nix
# flake.nix (fragment)
{
  outputs = { self, nixpkgs, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [ ./configuration.nix ];
    };
  };
}
```

The flake pins inputs and exposes a named configuration; rebuild targets that expression rather than an ad-hoc install sequence. See [NixOS configurations](../07-flakes/workflows/nixos-configurations.md).

## References

- [NixOS manual — Configuration](https://nixos.org/manual/nixos/stable/index.html#ch-configuration) — declarative model, modules, packages, and rebuild
- [nix.dev](https://nix.dev/) — ecosystem docs; declarative machine specification and related concepts

## See also

- [Why Nix](why-nix.md)
- [Immutability and rollback](immutability-and-rollback.md)
- [Generation](../02-concepts/generation.md)
- [Profile](../02-concepts/profile.md)
- [configuration.nix](../09-nixos/configuration/configuration-nix.md)
- [NixOS configurations (flakes)](../07-flakes/workflows/nixos-configurations.md)
