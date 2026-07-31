---
status: complete
---

# nix.conf knobs

Dense lookup for high-signal `nix.conf` settings and their NixOS `nix.settings` equivalents. Semantics, load order, and trust model: [nix.conf](../05-cli-and-tooling/config/nix-conf.md) · [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md). Inspect effective values: `nix config show` (needs `experimental-features = nix-command`).

**Version stamp:** knob names and defaults checked against the [Nix stable manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) (~**Nix 2.34.x**; stable redirect `/manual/nix/2.34/…`).

**List settings:** `name = a b` replaces; `extra-name = c d` appends (CLI: `--extra-substituters`, `--option extra-trusted-public-keys …`). **Priority:** CLI > `NIX_CONFIG` > user conf > system conf; daemon policy must live in system conf the daemon reads.

## Trust and binary caches

To **use** a substituter URL, the caller must be in `trusted-users` **or** the URL must be in `trusted-substituters` (default empty). Matching `trusted-public-keys` (or CA / `trusted=true` store) still apply. Do not conflate “who may connect” (`allowed-users`) with “who may change trust” (`trusted-users`).

| Knob | Meaning | Operator tip | Wiki link |
|------|---------|--------------|-----------|
| `substituters` | Whitespace-separated store URLs queried for pre-built paths (default `https://cache.nixos.org/`). Lower cache priority number = tried first. | Prefer `extra-substituters` to append. Unprivileged callers need each URL in `trusted-substituters` (or be `trusted-users`). | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| `trusted-public-keys` | Public keys whose signatures Nix accepts when copying non–content-addressed paths from other stores. | Every substituter you rely on needs a matching key here (or `extra-trusted-public-keys`). Default includes `cache.nixos.org-1:…`. | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| `trusted-substituters` | Substituter URLs unprivileged users may enable via `--substituters` / user conf. Not used until requested. Default empty. | Allow-list third-party caches without widening `trusted-users`. Pair with matching keys. | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| `trusted-users` | Users/groups (`@wheel`) with elevated daemon rights: extra substituters, unsigned imports, etc. Default `root`. | Treat as root-equivalent; keep minimal. On NixOS often `root @wheel`. Distinct from multi-machine inter-trust. | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| `allowed-users` | Who may connect to the multi-user daemon (`*` default). | `trusted-users` always connect even if omitted here. Tighten on shared hosts. | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| `require-sigs` | If `true` (default), substituted non-CA paths need a trusted signature (unless store URL has `trusted=true` or path is CA). | Leave `true`; `false` disables signature checking—security-sensitive. | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |
| `substitute` | Global on/off for attempting substitution (default `true`). | Per-invocation: `nix build --option substitute false`. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `always-allow-substitutes` | If `true`, ignore derivation `allowSubstitutes` and always try substituters. | Default `false`; enable only when you want substitution even when derivations opt out. | [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) |

## Build parallelism and remotes

| Knob | Meaning | Operator tip | Wiki link |
|------|---------|--------------|-----------|
| `max-jobs` | Max parallel **local** build jobs (default `1`). | `auto` = CPU count; `0` = remotes-only via `builders` (except `preferLocalBuild`). Override: `-j` / `--max-jobs`. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `cores` | Sets `NIX_BUILD_CORES` for each builder (intra-job parallelism). `0` = detect CPUs. | Independent of `max-jobs`. Nixpkgs `enableParallelBuilding` passes `-j${NIX_BUILD_CORES}` to Make. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `builders` | Remote build machines (`;` or newline separated), or `@/path` to a machines file. | `max-jobs = 0` for remote-only. Remotes need SSH + Nix on target; daemon runs builds as root toward remote user. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `builders-use-substitutes` | Remote builders use their own substituters (default `false`). | Turn on when upload to remote is slow; remotes need their own cache trust configured. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `extra-platforms` | Additional `system` values executable locally (e.g. `i686-linux` on `x86_64-linux`). | Lets Nix build foreign `system` locally when CPU/emulation supports it—verify outputs vs native builds. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `system` | Native platform Nix was built for; local builds require matching `system` or `extra-platforms`. | Usually leave default; use `eval-system` to evaluate for another platform without changing build eligibility. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |

## Sandbox

| Knob | Meaning | Operator tip | Wiki link |
|------|---------|--------------|-----------|
| `sandbox` | Isolate builds: `true`, `false`, or `relaxed` (FODs and `__noChroot` skip sandbox). Default `true` on Linux, `false` elsewhere. | Needs root + build users on Linux/macOS. Set in **system** conf for daemon builds. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `sandbox-paths` | Bind-mounts into sandbox (`target=source`, `path?` if optional). | GPU/tests: e.g. `/dev/nvidiactl?`. Nix store sources pull in closure. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |

## Experimental features and flakes

| Knob | Meaning | Operator tip | Wiki link |
|------|---------|--------------|-----------|
| `experimental-features` | Space-separated flags to enable (`nix-command`, `flakes`, …). Default empty. | Still experimental as of Nix **2.34.x**. NixOS: `experimental-features = [ "nix-command" "flakes" ];`. One-shot: `--extra-experimental-features 'nix-command flakes'`. | [Feature flags overview](../08-experimental-features/feature-flags-overview.md) |
| `extra-experimental-features` | Appends to `experimental-features`. | Safer than replacing when layering flags from user conf. | [Feature flags overview](../08-experimental-features/feature-flags-overview.md) |
| `flake-registry` | Path or URI of global flake registry (default `https://channels.nixos.org/flake-registry.json`). Empty disables. | Requires `flakes` in `experimental-features`. | [Feature flags overview](../08-experimental-features/feature-flags-overview.md) |
| `use-registries` | Whether flake registries resolve flake refs (default `true`). | Requires `flakes`. Set `false` to disable registry-based resolution. | [Feature flags overview](../08-experimental-features/feature-flags-overview.md) |

## GC, store, and retention

| Knob | Meaning | Operator tip | Wiki link |
|------|---------|--------------|-----------|
| `keep-outputs` | GC keeps outputs of non-garbage derivations (default `false`). | `true` retains build-time-only outputs for traceability; uses more disk. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `keep-derivations` | GC keeps `.drv` files for live outputs (default `true`). | Pair with `keep-outputs = true` for dev/GC-friendly retention; turn off to save space. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `auto-optimise-store` | Hard-link identical store files on add (default `false`). | Saves disk; or run `nix-store --optimise` manually when off. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `min-free` / `max-free` | Auto-GC when `/nix/store` free space drops below `min-free` until `max-free` available. `min-free = 0` disables. | Tune on small disks; `max-free` defaults to unlimited. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |

## Network and downloads

| Knob | Meaning | Operator tip | Wiki link |
|------|---------|--------------|-----------|
| `connect-timeout` | Seconds to establish substituter connections (`curl --connect-timeout`; default `15`). `0` = no limit. | Raise on high-latency links; `0` only if you accept indefinite hangs. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `download-buffer-size` | Internal download buffer in bytes (default 1 MiB). | Increase if large-cache downloads stall (producer slower than buffer drain). | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `http-connections` | Max parallel HTTP connections for binary caches (default `25`; `0` = unlimited). | Lower on constrained networks; raise for fast mirrors. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `max-substitution-jobs` | Parallel substitution jobs (default `16`; min effective `1`). | Independent of `max-jobs` (build parallelism). | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `fallback` | Build from source if substituter fetch fails (default `false`). | Equivalent to `--fallback`; can hide cache outages at build-time cost. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |

## Developer and hygiene

| Knob | Meaning | Operator tip | Wiki link |
|------|---------|--------------|-----------|
| `warn-dirty` | Warn when Git/Mercurial trees are dirty (default `true`). | Set `false` to silence; unrelated to `allow-dirty` (default allows dirty trees). | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `allow-dirty` | Allow dirty VCS trees in flake/fetch inputs (default `true`). | `false` fails eval on dirty trees—stricter reproducibility. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |
| `show-trace` | Print stack trace on Nix expression errors (default `false`). | Enable while debugging eval; `--show-trace` on CLI. | [nix.conf](../05-cli-and-tooling/config/nix-conf.md) |

## NixOS `nix.settings` (quick map)

NixOS generates `/etc/nix/nix.conf` from `nix.settings`—do not edit the file by hand.

```nix
nix.settings = {
  experimental-features = [ "nix-command" "flakes" ];
  max-jobs = "auto";          # string "auto" is valid
  sandbox = true;
  extra-substituters = [ "https://example.cachix.org" ];
  extra-trusted-public-keys = [
    "example.cachix.org-1:…="
  ];
  keep-outputs = true;
  keep-derivations = true;
};
```

List-valued options become space-separated lines; booleans become `true`/`false`. See [nix.conf](../05-cli-and-tooling/config/nix-conf.md) for load order and daemon vs client conf.

## See also

- [CLI Cheatsheet](cli.md) — commands, `--option`, experimental one-shots
- [FAQ: Common Errors](faq-common-errors.md) — untrusted substituter / missing experimental features
- [Feature flags overview](../08-experimental-features/feature-flags-overview.md) — full flag inventory and stabilization notes
- [nix.conf](../05-cli-and-tooling/config/nix-conf.md) — file locations, format, key settings essay
- [Trusted users and substituters](../05-cli-and-tooling/config/trusted-users-and-substituters.md) — trust model for caches and daemon clients

## References

- [Nix stable manual](https://nix.dev/manual/nix/stable/)
- [Nix manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html) (stable; verified ~2.34.x)
- [Nix manual — `nix config show`](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-config-show.html) (experimental `nix-command`)
