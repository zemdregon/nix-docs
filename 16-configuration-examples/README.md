---
status: index
---

# Configuration examples

Worked, copy-adaptable configurations that **compose** the teaching domains (`00`–`15`) into one coherent picture. Each leaf is a walkthrough: file layout, annotated Nix, activate/check commands, failure modes, and deep links into concept/module pages—not a second option encyclopedia.

**Not this domain:** tiny parseable fixtures under [meta/examples/](../meta/examples/README.md). Cite those fixtures when a one-file snippet is enough; use these leaves when the reader needs a multi-file “how the pieces fit” story.

Pins such as `nixos-26.05` and `system = "x86_64-linux"` are illustrative. Flake workflows need experimental [`nix-command`](../08-experimental-features/nix-command.md) and [`flakes`](../08-experimental-features/flakes.md). Stuck? [FAQ](../cheatsheets/faq-common-errors.md) → [Getting help](../15-history-and-governance/getting-help-and-community.md).

## Contents

- [Minimal flake NixOS host](minimal-flake-nixos-host.md) — Single-host flake + `configuration.nix` shape through first rebuild
- [NixOS with Home Manager](nixos-with-home-manager.md) — System + user profile in one `nixos-rebuild`
- [Project devShell and direnv](project-devshell-and-direnv.md) — Flake `devShells`, `mkShell`, and auto-enter
- [Custom package and overlay flake](custom-package-overlay-flake.md) — `callPackage`, overlay, and flake `packages` / host use
- [Homelab proxy, services, and secrets](homelab-proxy-secrets-services.md) — Reverse proxy, firewall, and ciphertext secrets
- [Multi-host config repo](multi-host-config-repo.md) — `hosts/` / `modules/` fleet flake and deploy hooks
- [nix-darwin with Home Manager](nix-darwin-with-home-manager.md) — macOS system + user config via `darwin-rebuild`
- [Disko + impermanence host](disko-impermanence-host.md) — Declarative disks, tmpfs root, and `/persist` survivors
- [nixos-anywhere bootstrap](nixos-anywhere-bootstrap.md) — Remote SSH wipe-and-install of a disko flake
- [deploy-rs fleet](deploy-rs-fleet.md) — Day-2 multi-profile hub deploy on a multi-host flake
- [Flake CI with GitHub Actions](flake-ci-github-actions.md) — Runner install, cache, `nix flake check`, host matrix
