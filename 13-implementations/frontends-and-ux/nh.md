---
status: complete
---

# nh

## Overview

**nh** (“yet another Nix helper”) is a community CLI that reimplements rebuild-style workflows for **NixOS**, **Home Manager**, and **nix-darwin** with a single, more ergonomic front door. Packaged in nixpkgs as `nh` ([nix-community/nh](https://github.com/nix-community/nh)).

In this domain it sits next to the classic [nixos-rebuild](nixos-rebuild.md) frontend and apart from [GUIs and installers](guis-and-installers.md): still a terminal tool, but aimed at clearer progress, pre-activation diffs, and unified flags across platforms. It is **not** a thin shell around `nixos-rebuild`; activation still ends in the same place once you switch.

For day-to-day commands, flags, and how nh relates to `nvd` and official rebuild actions, see the tooling page [nh / nvd / nixos-rebuild](../../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md). Switch / boot / test / build semantics: [rebuild actions](../../09-nixos/operations/rebuild-switch-boot-test.md).

## Details

### Where it fits

| Surface | Role |
|---------|------|
| [nixos-rebuild](nixos-rebuild.md) | Official NixOS rebuild / activate frontend |
| **nh** | Unified UX over NixOS / HM / Darwin rebuild-style flows |
| [GUIs and installers](guis-and-installers.md) | Graphical install / setup tooling |
| `nvd` | Focused package/version diffs (often used with either rebuild path) |

nh improves review and ergonomics; it does not invent a new activation model. A successful `nh os switch` still activates a system generation the same way a rebuild would.

### UX goals (high level)

Upstream positions nh as a cohesive reimplementation rather than a wrapper:

- **One CLI** for `os`, `home`, and `darwin` (plus extras such as `search` and `clean`)
- **Build-tree / progress** output and **diff / change review** before activation
- **Specialisation** and **generation** helpers with explicit targeting
- Optional integration with familiar third-party presentation (e.g. nix-output-monitor) via env / config

Exact subcommands and flags change between releases—prefer `nh --help` / `man 1 nh` and the [adjacent-tools](../../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md) page over memorizing every switch.

### Packaging and modules

Available from nixpkgs (`nixpkgs#nh`) and from the project flake for development builds. NixOS and Home Manager modules under `programs.nh` can enable the binary, set a default flake path (`NH_FLAKE` / platform-specific vars), and optionally schedule `nh clean`.

### Vs official rebuild

Use **nixos-rebuild** when you want the stock NixOS path documented in the manual. Prefer **nh** when you want one tool for NixOS + Home Manager + Darwin with richer pre-switch feedback. Either way, activation semantics for NixOS match [rebuild-switch-boot-test](../../09-nixos/operations/rebuild-switch-boot-test.md).

## Examples

Try from a shell (nixpkgs attribute):

```bash
nix shell nixpkgs#nh
nh --help
```

Shape of a NixOS switch (confirm flags with `nh os switch --help`):

```bash
nh os switch
# or with an explicit flake / host, depending on NH_* and module setup
nh os switch /path/to/flake -H myhost
```

Minimal NixOS module pattern (from upstream docs; adjust paths):

```nix
{
  programs.nh = {
    enable = true;
    flake = "/home/user/my-nixos-config";
  };
}
```

Build-then-review before activating remains a good habit whether you use nh or stock rebuild—see patterns on [nh / nvd / nixos-rebuild](../../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md).

## See also

- [nh / nvd / nixos-rebuild](../../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md) — CLI detail, nvd, and rebuild comparison
- [nixos-rebuild](nixos-rebuild.md) — classic rebuild frontend (this folder)
- [GUIs and installers](guis-and-installers.md) — graphical tooling landscape
- [Rebuild switch / boot / test](../../09-nixos/operations/rebuild-switch-boot-test.md) — activation action semantics

## References

- [nix-community/nh](https://github.com/nix-community/nh) — Yet Another Nix Helper (canonical upstream)
- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config) — official `nixos-rebuild` switch/boot/test/build
