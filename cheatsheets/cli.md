---
status: complete
---

# CLI Cheatsheet

Dense lookup for classic Nix tools, the experimental unified `nix` CLI, and `nixos-rebuild`. Prefer leaf pages under [05-cli-and-tooling](../05-cli-and-tooling/README.md) for semantics; this sheet is for lookup only.

**Version stamp:** command pairs and experimental notes checked against the [Nix stable manual](https://nix.dev/manual/nix/stable/) (~**Nix 2.34.x**).

## Experimental features

Unified `nix …` subcommands need [`nix-command`](../08-experimental-features/nix-command.md). Flake refs (`nixpkgs#hello`, `.#pkg`) and `nix flake …` also need [`flakes`](../08-experimental-features/flakes.md). As of Nix **2.34.x**, both remain **experimental**—interfaces can change until stabilization.

| Where | Setting |
|-------|---------|
| `nix.conf` / NixOS `nix.settings` | `experimental-features = nix-command flakes` |
| One-shot | `nix --extra-experimental-features 'nix-command flakes' …` |

Classic hyphenated tools (`nix-build`, `nix-shell`, `nix-env`, …) do **not** need those flags. Confirm flags against the [command reference](https://nix.dev/manual/nix/stable/command-ref/) for your Nix version. Config: [nix.conf](../05-cli-and-tooling/config/nix-conf.md) · [nix.conf knobs](nix-conf-knobs.md).

## Classic CLI

### `nix-build`

Leaf: [nix-build](../05-cli-and-tooling/classic-cli/nix-build.md)

| Task | Command |
|------|---------|
| Attr from nixpkgs | `nix-build '<nixpkgs>' -A hello` |
| File / expr | `nix-build ./default.nix` · `nix-build -E '…'` |
| No / custom `result` | `nix-build … --no-out-link` · `-o ./my-result` |
| Dry-run | `nix-build … --dry-run` |

### `nix-shell`

Leaf: [nix-shell](../05-cli-and-tooling/classic-cli/nix-shell.md)

| Task | Command |
|------|---------|
| Packages on `$PATH` | `nix-shell -p git jq` |
| Derivation env | `nix-shell` · `nix-shell '<nixpkgs>' -A hello` |
| Pure / one-shot | `nix-shell --pure` · `nix-shell --run 'cmd'` |

### `nix-env`

Leaf: [nix-env](../05-cli-and-tooling/classic-cli/nix-env.md)

| Task | Command |
|------|---------|
| Install (attr) | `nix-env -iA nixpkgs.hello` |
| Query installed / available | `nix-env -q` · `nix-env -qaP` |
| Upgrade / uninstall | `nix-env -uA nixpkgs.hello` · `nix-env -e hello` |
| Generations | `nix-env --list-generations` · `--rollback` · `--switch-generation N` |

### `nix-channel`

Leaf: [nix-channel](../05-cli-and-tooling/classic-cli/nix-channel.md)

| Task | Command |
|------|---------|
| List / update | `nix-channel --list` · `nix-channel --update` |
| Add / remove | `nix-channel --add URL name` · `nix-channel --remove name` |

### `nix-store`

Leaf: [nix-store](../05-cli-and-tooling/classic-cli/nix-store.md)

| Task | Command |
|------|---------|
| Realise / delete | `nix-store --realise PATH` · `nix-store --delete PATH` |
| GC roots / live / dead | `nix-store --gc --print-roots` · `--print-live` · `--print-dead` |
| Query refs / referrers | `nix-store --query --references PATH` · `--referrers PATH` |

### `nix-collect-garbage`

Leaf: [nix-collect-garbage](../05-cli-and-tooling/classic-cli/nix-collect-garbage.md)

| Task | Command |
|------|---------|
| Collect dead paths | `nix-collect-garbage` |
| Also delete old generations | `nix-collect-garbage -d` |
| Older than period | `nix-collect-garbage --delete-older-than 30d` |

## Modern `nix` CLI

Requires experimental `nix-command` (and `flakes` for `#` flake refs). Installables: `nixpkgs#hello`, `.#pkg`, `--file` / `--expr`, or store paths.

| Classic | Modern (`nix-command`) |
|---------|------------------------|
| `nix-build` | `nix build` |
| `nix-shell -p` | `nix shell` |
| derivation `nix-shell` | `nix develop` |
| `nix-env` | `nix profile` |
| `nix-collect-garbage` / `nix-store --gc` | `nix store gc` |

### `nix build` / `develop` / `run` / `shell`

Leaf: [nix build / develop / run](../05-cli-and-tooling/modern-cli/nix-build-develop-run.md)

| Task | Command |
|------|---------|
| Build | `nix build` · `nix build nixpkgs#hello` · `nix build .#pkg` |
| No / custom link | `nix build --no-link` · `nix build --out-link ./out` |
| Print out paths | `nix build --print-out-paths nixpkgs#hello` |
| Dev / build env | `nix develop` · `nix develop .#devShell` · `nix develop -c cmd` |
| Run app / mainProgram | `nix run nixpkgs#hello` · `nix run . -- --help` |
| Packages on `$PATH` | `nix shell nixpkgs#jq nixpkgs#ripgrep` |
| Search | `nix search nixpkgs hello` |

### `nix flake`

Leaf: [nix flake](../05-cli-and-tooling/modern-cli/nix-flake.md)

| Task | Command |
|------|---------|
| Show / check | `nix flake show` · `nix flake check` |
| Init / new | `nix flake init` · `nix flake new ./dir` |
| Lock / update | `nix flake lock` · `nix flake update` · `nix flake update INPUT` |

### `nix profile`

Leaf: [nix profile](../05-cli-and-tooling/modern-cli/nix-profile.md)

| Task | Command |
|------|---------|
| Add / list / remove | `nix profile add nixpkgs#hello` · `nix profile list` · `nix profile remove hello` (`install` = deprecated alias of `add`) |
| History / rollback | `nix profile history` · `nix profile rollback` · `nix profile rollback --to N` |

### `nix repl` / `fmt`

Leafs: [nix repl](../05-cli-and-tooling/modern-cli/nix-repl.md) · [nix fmt / edit](../05-cli-and-tooling/modern-cli/nix-fmt-and-edit.md)

| Task | Command |
|------|---------|
| Eval / repl | `nix eval .#pkg.name` · `nix repl` · `nix repl nixpkgs` |
| Format (flake `formatter`) | `nix fmt` · `nix fmt ./path` |

### Store helpers

Leaf: [nix store ops](../05-cli-and-tooling/modern-cli/nix-store-ops.md)

| Task | Command |
|------|---------|
| GC / path info | `nix store gc` · `nix path-info -Sh nixpkgs#hello` |
| Why depends / copy | `nix why-depends A B` · `nix copy --to ssh://host PATH` |
| Config / help | `nix config show` · `nix build --help` |

## `nixos-rebuild`

System generations (not the user profile). Actions that activate or change the boot default usually need root. Details: [switch / boot / test](../09-nixos/operations/rebuild-switch-boot-test.md) · [rollbacks](../09-nixos/operations/rollbacks.md).

| Action | Build | Boot default | Activate now | Example |
|--------|-------|--------------|--------------|---------|
| `switch` | yes | yes | yes | `sudo nixos-rebuild switch` |
| `boot` | yes | yes | no | `sudo nixos-rebuild boot` |
| `test` | yes | no | yes | `sudo nixos-rebuild test` |
| `build` | yes | no | no | `nixos-rebuild build` |

| Task | Command |
|------|---------|
| Flake host | `sudo nixos-rebuild switch --flake .#host` |
| Dry-run | `sudo nixos-rebuild dry-build` · `dry-activate` |
| Rollback | `sudo nixos-rebuild switch --rollback` |

Adjacent UX: [nh / nvd](../05-cli-and-tooling/adjacent-tools/nh-nvd-nixos-rebuild.md).

## Common flags

| Flag | Era | Role |
|------|-----|------|
| `-A` / `--attr` | Classic | Attribute path |
| `-f` / `--file` | Both | Expression file |
| `-E` / `--expr` | Both | Inline expression |
| `-I` / `--include` | Both | Lookup path (`<nixpkgs>`) |
| `--arg` / `--argstr` | Eval | Function arguments |
| `-j` / `--max-jobs` | Builds | Local parallelism |
| `--dry-run` | Many | Preview |
| `-L` / `--print-build-logs` | Modern `nix` | Full build logs |
| `--impure` | Modern `nix` | Allow impure eval |
| `--no-link` / `--out-link` | `nix build` | Result symlink control |
| `--option NAME VALUE` | All Nix | Override `nix.conf` |
| `--extra-experimental-features …` | Modern `nix` | Enable `nix-command` / `flakes` |
| `--flake URI[#name]` | `nixos-rebuild` | Flake `nixosConfigurations` |

## See also

- [Classic CLI](../05-cli-and-tooling/classic-cli/README.md) · [Modern CLI](../05-cli-and-tooling/modern-cli/README.md)
- [nix.conf knobs](nix-conf-knobs.md) · [Config](../05-cli-and-tooling/config/README.md)
- [NixOS operations](../09-nixos/operations/README.md)
- [FAQ: Common Errors](faq-common-errors.md)
- [nix-command](../08-experimental-features/nix-command.md) · [flakes](../08-experimental-features/flakes.md)
- [nix-index / comma](../05-cli-and-tooling/adjacent-tools/nix-index-comma.md) — locate packages by binary name; one-shot `,` runs

## References

- [Nix stable manual](https://nix.dev/manual/nix/stable/)
- [Command reference (index)](https://nix.dev/manual/nix/stable/command-ref/)
- [nix-build](https://nix.dev/manual/nix/stable/command-ref/nix-build.html)
- [nix-shell](https://nix.dev/manual/nix/stable/command-ref/nix-shell.html)
- [nix-env](https://nix.dev/manual/nix/stable/command-ref/nix-env.html)
- [nix-channel](https://nix.dev/manual/nix/stable/command-ref/nix-channel.html)
- [nix-store](https://nix.dev/manual/nix/stable/command-ref/nix-store.html)
- [nix-collect-garbage](https://nix.dev/manual/nix/stable/command-ref/nix-collect-garbage.html)
- [nix (new CLI)](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix.html)
- [nix build](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-build.html)
- [nix develop](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop.html)
- [nix run](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-run.html)
- [nix flake](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake.html)
- [nix profile](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-profile.html)
- [nix repl](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-repl.html)
- [nix fmt](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-fmt.html)
- [NixOS manual — Changing the Configuration](https://nixos.org/manual/nixos/stable/index.html#sec-changing-config)
- [NixOS manual — Rolling Back](https://nixos.org/manual/nixos/stable/index.html#sec-rollback)
