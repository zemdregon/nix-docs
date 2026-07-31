---
status: complete
---

# Upstreaming Modules

## Overview

Upstreaming a NixOS module means landing it in nixpkgs so other systems can import it from the default module set and so its options appear on [search.nixos.org](https://search.nixos.org/options) after a channel picks up the merge. Upstream modules live under `nixos/modules/` and are registered in `nixos/modules/module-list.nix`.

The contribution path is a PR to [NixOS/nixpkgs](https://github.com/NixOS/nixpkgs) that follows [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md): a clear description, maintainers, option docs, and often a NixOS test. Write the module first as a local import (see [writing a module](writing-a-module.md)); upstream when the interface is stable enough to share.

## Details

**Where upstream modules live.** Files under `nixos/modules/` (services, programs, hardware, virtualisation, and so on) are wired into the default evaluation by listing their paths in `nixos/modules/module-list.nix`. A new module needs both the implementation file and that registration entry. Do not re-list paths that are already in the default set from `configuration.nix`.

**Contribution expectations.** Treat the PR like any nixpkgs change: explain *why*, name maintainers, document every option, and prefer a NixOS VM/integration test when the module starts services or has non-trivial activation. Review runs through nixpkgs CI. Details of review flow belong in [review process](../../06-nixpkgs/contribution/review-process.md) and CONTRIBUTING.md—do not invent extra bot or checklist names beyond that.

**Module `meta` attributes.** Like packages, modules may declare a top-level `meta` alongside `options` and `config`. The documented attrs are `meta.maintainers`, `meta.doc`, and `meta.buildDocsInSandbox`. Each may be defined at most once per module file. `maintainers` lists module maintainers; `doc` may point at a Nixpkgs-flavored CommonMark file whose contents feed the NixOS manual; `buildDocsInSandbox` (default `true`, honored only for nixpkgs-shipped modules) controls whether option docs build inside a sandbox for caching—set `false` only when docs need `pkgs` (beyond allowed sandbox refs) or non-sandboxed modules. User modules and `extraModules` always build docs outside the sandbox.

**Quality bar before opening a PR.**

- Typed options with clear `description`s (and helpers like `mkEnableOption` where appropriate)—see [custom options](custom-options.md).
- Gate `config` with `mkIf` on an enable flag so disabled modules stay inert.
- Use [assertions and warnings](assertions-and-warnings.md) for conflicting or unsupported combinations.
- No secrets, credentials, or machine-specific data in the tree.
- Follow patterns of neighboring modules under the same `services.*` / `programs.*` tree rather than inventing a one-off layout.
- After `meta.doc` changes, check that the NixOS manual still builds (`nix-build nixos/release.nix -A manual.x86_64-linux` from a nixpkgs checkout, as in the manual).

**Local iteration vs permanent fork.** While developing or temporarily diverging from upstream, `disabledModules` can drop the stock module (full path, path relative to the modules tree, or an attrset with a unique `key`) so your import replaces it. That is for iteration and targeted overrides—not a long-term substitute for contributing fixes upstream when the change is generally useful.

**Visibility after merge.** Options only show on search.nixos.org once the change has landed and a channel (or other documented update path) includes that nixpkgs revision. Until then, users must import your module explicitly.

## Examples

Minimal `meta` shape from the NixOS manual (maintainers list filled from `lib.maintainers`; optional `doc` / `buildDocsInSandbox` as needed):

```nix
{
  config,
  lib,
  pkgs,
  ...
}:
{
  options = {
    # … typed options with descriptions …
  };

  config = {
    # … typically mkIf cfg.enable { … } …
  };

  meta = {
    maintainers = with lib.maintainers; [ /* yourHandle */ ];
    # doc = ./default.md;
    # buildDocsInSandbox = true;  # default; rarely override
  };
}
```

Register the new file in `nixos/modules/module-list.nix` in the same PR. For the full PR checklist, use CONTRIBUTING.md rather than treating this snippet as a tutorial.

## References

- [NixOS manual (stable) — Writing NixOS Modules (Meta Attributes)](https://nixos.org/manual/nixos/stable/index.html#sec-writing-modules)
- [nixpkgs CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)
- [nixpkgs `nixos/modules`](https://github.com/NixOS/nixpkgs/tree/master/nixos/modules)

## See also

- [Writing a module](writing-a-module.md)
- [Custom options](custom-options.md)
- [Assertions and warnings](assertions-and-warnings.md)
- [Module system](../architecture/module-system.md)
- [Review process](../../06-nixpkgs/contribution/review-process.md)
