---
status: complete
---

# Templates

## Overview

A flake can expose **templates**: starter directory trees that `nix flake init` or `nix flake new` copy into a project. Templates live under the `templates` output alongside [packages, apps, and dev shells](packages-apps-devShells.md). They are a lightweight way to publish “clone this layout” without teaching users your full flake API—useful for libraries, services, or internal scaffolding.

Each template is a small record: a `path` to copy, a one-line `description`, and optionally `welcomeText` shown after init. The built-in [templates](https://github.com/NixOS/templates) flake ships common starters; any flake can define its own.

`nix flake init`, `nix flake new`, and `nix flake check` are part of the experimental **`nix-command`** + **`flakes`** CLI. As of the Nix **2.34.x** stable manual, they remain experimental.

## Details

**Output shape.** Under `outputs`, declare `templates.<name>` with at least `path` and `description`. The `description` is one line of CommonMark; `welcomeText` is optional markdown printed when someone initializes from that template.

**Default template.** `templates.default` is what `nix flake init` picks when you pass no `-t` flag. You can alias it to another entry, e.g. `templates.default = self.templates.rust`, instead of duplicating the record.

**Init vs new.** `nix flake init` copies a template into the **current** directory and does not overwrite files that already exist. `nix flake new <dir>` creates a **new** directory and fills it from the template. Both accept `-t` / `--template` for a flake reference and template name.

**Selecting a template.** With no `-t`, init uses the registry flake `templates#templates.default`. To pick by name: `nix flake init -t templates#simpleContainer`. For a local flake: `nix flake init -t ./#mytemplate` (or `nix flake new myproj -t ./#mytemplate`).

**Discovery.** `nix flake show templates` lists outputs of the built-in templates flake, including available template names and descriptions.

**Validation.** `nix flake check` evaluates template definitions and requires that `templates.default` and each `templates.<name>` you declare are well-formed (valid `path`, required attributes present).

**Migration.** Older flakes used a top-level `defaultTemplate` attribute; that name was renamed to `templates.default`. Nix emits a warning if the old name is still present.

For where `templates` sits in the wider output schema, see [inputs and outputs](../anatomy/inputs-and-outputs.md) and [flake.nix schema](../anatomy/flake-nix-schema.md). For flake basics, start with [Flake (concept)](../../02-concepts/flake.md).

## Examples

**Define templates in `flake.nix`:**

```nix
{
  outputs = { self, ... }: {
    templates.rust = {
      path = ./rust;
      description = "Rust binary with crane and dev shell";
      welcomeText = ''
        # Rust template

        Run `nix develop` for the toolchain, then `cargo build`.
      '';
    };
    templates.default = self.templates.rust;
  };
}
```

**CLI usage:**

```bash
# Built-in default template into current directory
nix flake init

# Named template from the templates flake
nix flake init -t templates#simpleContainer

# Local template from this flake
nix flake init -t ./#rust

# New directory from a template
nix flake new my-service -t templates#simpleContainer

# List built-in templates
nix flake show templates
```

## References

- [Nix manual — `nix flake init`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-init.html) — copying templates into a directory (experimental; Nix 2.34.x)
- [Nix manual — `nix flake new`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-new.html) — creating a directory from a template
- [Nix manual — `nix flake check`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check.html) — validating template definitions
- [Nix manual — flakes and `nix flake`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html) — flake outputs, including templates

## See also

- [Packages, apps, devShells](packages-apps-devShells.md) — sibling flake outputs for build and develop workflows
- [Inputs and outputs](../anatomy/inputs-and-outputs.md) — how outputs are structured
- [flake.nix schema](../anatomy/flake-nix-schema.md) — required and optional flake attributes
- [Flake (concept)](../../02-concepts/flake.md) — entry file, lockfile, and CLI overview
