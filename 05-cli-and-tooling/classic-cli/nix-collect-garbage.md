---
status: complete
---

# nix-collect-garbage

## Overview

`nix-collect-garbage` deletes **unreachable** [store paths](../../02-concepts/store-path.md) from the Nix store. It is mostly an alias of [`nix-store --gc`](nix-store.md): both run the same reachability-based garbage collector and remove paths that are not **live**—not reachable from [GC roots](../../04-store-and-build/garbage-collection.md) through store references and closures.

The command adds profile-management flags (`--delete-old` / `-d`, `--delete-older-than`) that drop old [profile generations](../../02-concepts/generation.md) before collecting garbage. Because each kept generation is a root, removing old generations frees more disk space but also removes rollback targets for those generations.

For how GC works (live vs dead paths, root categories, `nix.conf` settings), see [Garbage collection](../../04-store-and-build/garbage-collection.md). The experimental [`nix store gc`](../modern-cli/nix-store-ops.md) subcommand is the modern CLI equivalent of store GC.

## Details

**Relation to `nix-store --gc`.** With no extra flags, `nix-collect-garbage` behaves like `nix-store --gc`: it deletes every store path that no root transitively references. Shared options include `--max-freed` _bytes_ (stop after freeing at least that much; suffixes `K`, `M`, `G`, `T`).

Use `nix-store --gc` when you only need GC or inspection flags that `nix-collect-garbage` does not expose:

- `--print-roots` — list GC roots without deleting
- `--print-live` / `--print-dead` — show reachable or deletable paths without deleting

**Profile deletion flags.** These run the equivalent of `nix-env --delete-generations` on profiles `nix-collect-garbage` discovers, then run GC:

| Flag | Effect |
|------|--------|
| `--delete-old` / `-d` | Delete all old generations on each found profile (keep only the current generation). |
| `--delete-older-than` _period_ | Delete generations older than _period_ (e.g. `30d`), except generations that were active at that time. |

Nix searches default [profile](../../02-concepts/profile.md) locations and, for migration cleanup, deprecated paths under `$NIX_STATE_DIR/profiles` (except `default` and `per-user/root`, which other commands still use). It cannot know about every profile on the system—only those it finds in those locations.

**Roots and safety.** GC only removes paths with no path from any root. Roots include explicit symlinks under `/nix/var/nix/gcroots/` (searched recursively), profile generation links, and auto-registered roots from `--add-root` / `result` symlinks. Deleting a generation removes its root, so that generation's closure becomes eligible for collection unless referenced elsewhere.

**Caution.** `-d` and `--delete-older-than` affect all profiles found in the searched locations, including other users' profiles on multi-user systems. Deleted generations cannot be rolled back to.

## Examples

**Delete unreachable store paths only** (same as `nix-store --gc`):

```bash
nix-collect-garbage
```

**Drop old profile generations, then collect garbage** (common on NixOS and long-lived user profiles):

```bash
nix-collect-garbage -d
```

**Free at least 500 MiB, then stop:**

```bash
nix-collect-garbage --max-freed 500M
```

**Delete generations older than 30 days, then GC:**

```bash
nix-collect-garbage --delete-older-than 30d
```

**Inspect without deleting** (use `nix-store`):

```bash
nix-store --gc --print-roots
nix-store --gc --print-dead
```

## References

- [Nix reference manual — `nix-collect-garbage`](https://nix.dev/manual/nix/stable/command-ref/nix-collect-garbage.html)
- [Nix reference manual — `nix-store --gc`](https://nix.dev/manual/nix/stable/command-ref/nix-store/gc.html)
- [Nix reference manual — garbage collector roots](https://nix.dev/manual/nix/stable/package-management/garbage-collector-roots.html)

## See also

- [Garbage collection](../../04-store-and-build/garbage-collection.md) — live/dead paths, root types, `nix.conf` GC settings
- [Profile](../../02-concepts/profile.md) — environments whose generations are GC roots
- [Generation](../../02-concepts/generation.md) — numbered profile snapshots; deleting old ones enables reclamation
- [nix-store](nix-store.md) — classic store CLI, including `--gc` inspection flags
- [nix store](../modern-cli/nix-store-ops.md) — modern store subcommands including `gc`
