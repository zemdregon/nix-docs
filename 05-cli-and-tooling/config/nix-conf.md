---
status: complete
---

# nix.conf

## Overview

**`nix.conf`** is the configuration file for the Nix client and (on multi-user installs) the Nix daemon. It controls substituters and trust, experimental features, build parallelism, sandboxing, garbage-collector keep flags, remote builders, and related settings.

On most systems the system file is `/etc/nix/nix.conf`. Per-user overrides live under the XDG config tree (typically `~/.config/nix/nix.conf`). On NixOS, do not edit `/etc/nix/nix.conf` by hand—set `nix.settings`; the module generates that file.

Inspect the **effective** merged configuration with [`nix config show`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-config-show.html) (experimental **`nix-command`** interface; Nix stable manual redirects to **2.34** as of 2026-07). Older Nix exposed the same idea as `nix show-config`; on Nix 2.34 that name remains a **deprecated alias** for `config show`.

Daemon trust knobs (`trusted-users`, system substituters) are **local** privilege on one install—not fleet or mesh membership. See [Trusted users and substituters](trusted-users-and-substituters.md) and [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md).

## Details

### File locations and load order

By default Nix reads settings in this order (later sources override earlier ones for ordinary keys)—[conf-file manual](https://nix.dev/manual/nix/stable/command-ref/conf-file.html):

1. **System** — `sysconfdir/nix/nix.conf` (usually `/etc/nix/nix.conf`), or `$NIX_CONF_DIR/nix.conf` if `NIX_CONF_DIR` is set. Values from this file are **not** forwarded to the daemon; the client assumes the daemon already loaded its own copy.
2. **User** — if `NIX_USER_CONF_FILES` is set, those `:`-separated paths (loaded in reverse order); otherwise `nix/nix.conf` under `XDG_CONFIG_DIRS` / `XDG_CONFIG_HOME` (defaults `/etc/xdg` and `$HOME/.config`).
3. **`NIX_CONFIG`** — if set, its contents are treated as another configuration file.
4. **CLI** — every setting has a matching flag (e.g. `--max-jobs 16`), or use `--option name value`. These override file/`NIX_CONFIG` values.

So effective priority is: **CLI flags > `NIX_CONFIG` > user conf > system conf**. Daemon-facing policy (`trusted-users`, system substituters, sandbox defaults, …) must live in the system conf the daemon reads—user conf alone cannot reconfigure a remote daemon.

### File format

Lines are `name = value`. Comments start with `#`. Other files can be pulled in with `include <path>` (relative to the current file); `!include` ignores a missing file.

Most settings replace any previous value. For **list** settings, prefix with `extra-` to **append** (e.g. `extra-substituters`, `extra-experimental-features`). Unknown option names in files are ignored with a warning; unknown CLI flags are errors (unless `--option` is used, which warns like a file).

Booleans are `true` / `false`. On the CLI, boolean flags take no argument; disable with a `no-` prefix (e.g. `--keep-failed`, `--no-keep-failed`). List values are whitespace-separated (except `builders`, which is semicolon- or newline-separated). Integer settings accept `K` / `M` / `G` / `T` suffixes (powers of 1024).

### Key settings

Defaults and semantics below match the Nix **stable** [`nix.conf` manual](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) (~**Nix 2.34**). Dense operator lookup: [nix.conf knobs](../../cheatsheets/nix-conf-knobs.md).

| Setting | Role |
|---------|------|
| `experimental-features` | Enable experimental surfaces (`nix-command`, `flakes`, …). Empty by default; both `nix-command` and `flakes` remain experimental in the stable manual. See [feature flags overview](../../08-experimental-features/feature-flags-overview.md). |
| `substituters` | Whitespace-separated store URLs used as binary caches (default `https://cache.nixos.org/`). Tried by priority; paths must also satisfy `trusted-public-keys` / trust rules. Store URI schemes: [`nix help-stores`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html). |
| `trusted-public-keys` | Keys accepted when verifying substituted store objects (default includes `cache.nixos.org-1:…`). |
| `trusted-users` / `allowed-users` | Who may connect to the daemon and who may change substituters / import unsigned paths. **Local daemon privilege only**—not multi-machine inter-trust. See [Trusted users and substituters](trusted-users-and-substituters.md) and [trusted users (security)](../../14-security-and-trust/trusted-users.md). |
| `sandbox` | Isolate builds: `true`, `false`, or `relaxed` (FODs and `__noChroot` skip the sandbox). Linux/macOS only; needs root + build users. Default `true` on Linux, `false` elsewhere. |
| `max-jobs` | Parallel **local** build jobs (default `1`). `auto` = CPU count; `0` = remotes-only via `builders` (except `preferLocalBuild`). Override with `-j` / `--max-jobs`. Deprecated alias: `build-max-jobs`. |
| `cores` | Sets `NIX_BUILD_CORES` in each builder (intra-job parallelism). `0` (default) = detect CPU count. Independent of `max-jobs`. |
| `builders` | Remote build machines (`;` or newline separated), or `@/absolute/path` to a machines file (default often `@/etc/nix/machines`). See [Remote builders](../../04-store-and-build/remote-builders.md). |
| `auto-optimise-store` | Hard-link identical store files as they are added (default `false`). |
| `keep-outputs` / `keep-derivations` | GC behavior: keep outputs of live `.drv`s / keep `.drv`s for live outputs. |
| `access-tokens` | `host=token` credentials for private Git hosts; see [Access tokens](access-tokens.md). |

Trust and cache wiring (`trusted-users`, `trusted-substituters`, when a substituter is accepted) are expanded on the sibling page—do not treat `trusted-users` as a casual convenience; the manual equates it with root-equivalent store access.

## Examples

Examples use settings and defaults from the conf-file manual (~Nix 2.34). Snippets are illustrative config—not a runnable end-to-end build. Inspect live merged values with `nix config show` (verified on Nix 2.34.8: `nix show-config` prints a deprecation warning and delegates to `config show`).

Minimal user override enabling the modern CLI and flakes (both remain **experimental** per the Nix stable manual):

```bash
# ~/.config/nix/nix.conf
experimental-features = nix-command flakes
keep-outputs = true
keep-derivations = true
```

Build parallelism, sandbox, and an appended substituter (system/daemon conf for sandbox and trust; user may append caches only when trust policy allows):

```bash
# /etc/nix/nix.conf  (or nix.settings on NixOS)
max-jobs = auto
cores = 0
sandbox = true
extra-substituters = https://example.cachix.org
extra-trusted-public-keys = example.cachix.org-1:…=
```

Append a cache without replacing the default substituter list:

```bash
extra-substituters = https://example.cachix.org
extra-trusted-public-keys = example.cachix.org-1:…=
```

Remote-only local scheduling (builds go to `builders`; `preferLocalBuild` still runs locally)—[conf-file `max-jobs`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html#conf-max-jobs):

```bash
# /etc/nix/nix.conf
max-jobs = 0
builders = ssh://builder.example x86_64-linux - 8 1
# or: builders = @/etc/nix/machines
```

NixOS equivalent (generates `/etc/nix/nix.conf`):

```nix
nix.settings = {
  experimental-features = [ "nix-command" "flakes" ];
  max-jobs = "auto";
  sandbox = true;
  keep-outputs = true;
  keep-derivations = true;
};
```

Inspect effective values:

```bash
nix config show                          # needs experimental-features = nix-command
nix config show experimental-features
nix config show --json
# older / alias: nix show-config  (deprecated alias for config show as of Nix 2.34)
```

One-shot override without editing files:

```bash
nix build --extra-experimental-features 'nix-command flakes' .
nix build --option max-jobs 4 .
```

## See also

- [Trusted users and substituters](trusted-users-and-substituters.md) — trust model for caches and daemon clients
- [nix.conf knobs](../../cheatsheets/nix-conf-knobs.md) — dense setting ↔ `nix.settings` lookup
- [Binary caches](../../04-store-and-build/binary-caches.md) — substituter workflow end-to-end
- [Signing and caches](../../14-security-and-trust/signing-and-caches.md) — signatures and cache authenticity
- [Inter-machine trust](../../14-security-and-trust/inter-machine-trust.md) — axes beyond one daemon’s `trusted-users`
- [Feature flags overview](../../08-experimental-features/feature-flags-overview.md) — enabling experimental features

## References

- [Nix manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) (stable → Nix **2.34** as of 2026-07)
- [Nix manual — `nix config show`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-config-show.html) (stable; experimental `nix-command` interface)
- [Nix manual — Store types (`nix help-stores`)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-help-stores.html) (stable; experimental interface)
