---
status: complete
---

# Garbage Collection

## Overview

**Garbage collection (GC)** reclaims disk space in the [Nix store](nix-store-layout.md) by deleting [store paths](../02-concepts/store-path.md) that are no longer needed. `nix-store --gc` (and the mostly equivalent `nix-collect-garbage`) removes every path that is not **live**—not reachable from a set of **GC roots** through store references and the [closure](../02-concepts/closure.md) of kept paths.

GC is safe for live paths: the collector only removes **dead** paths (no path from any root). Understanding what counts as a root, and what keeps old profile [generations](../02-concepts/generation.md) alive, is the main lever for freeing space without breaking rollbacks.

## Details

**Live vs dead.** A path is **live** if it is reachable from GC roots by following references between store objects (outputs, `.drv` files, sources, etc.). Everything in the closure of a live path stays live. A path is **dead** if no root transitively references it; dead paths are candidates for deletion.

**Root categories.** Roots are starting points for the reachability scan. Major categories include:

- **Explicit GC roots** — Symlinks under `/nix/var/nix/gcroots/` (searched recursively). Symlinks to store paths count as roots; tools also register roots under `gcroots/auto/` when you pass `--add-root` / `--out-link` / keep a `result` symlink.
- **[Profile](../02-concepts/profile.md) and generation links** — Profile version symlinks (and related system links such as NixOS `/run/booted-system`) are roots. Each kept generation pins its closure, so rollbacks stay possible until those generations are deleted.
- **Runtime roots** — Store paths held open by running processes (discovered via `/proc` when the collector can scan it). This keeps in-use binaries from being deleted while processes still reference them.

Use `nix-store --gc --print-roots` to list roots the collector will use; `--print-live` and `--print-dead` show the resulting sets without deleting.

**Running GC.** `nix-store --gc` deletes all unreachable paths. `nix-collect-garbage` is mostly an alias with extra profile-management flags:

- `--delete-old` / `-d` — Delete old (non-current) profile generations on profiles it finds, then run GC. Frees more space because generations are roots; also removes rollback targets for deleted generations. Use carefully: it can affect other users’ profiles on a shared machine.
- `--delete-older-than` _period_ — Same idea for generations older than a period (e.g. `30d`), then GC.
- `--max-freed` _bytes_ — Stop once at least that many bytes have been freed (suffixes `K`, `M`, `G`, `T` supported).

**Configuration (`nix.conf`).** GC behavior is also shaped by:

| Setting | Effect |
|---------|--------|
| `keep-derivations` | If `true` (default), retain `.drv` files from which non-garbage store paths were built. If `false`, those derivations can be collected unless separately rooted. |
| `keep-outputs` | If `true`, retain outputs of non-garbage derivations (including build-time-only deps such as compilers). Default `false`; with an output rooted, build-only inputs can still be dropped. |
| `min-free` | During builds, if free space under the store falls below this threshold, Nix triggers GC until enough space is available. Default `0` (disabled). |
| `max-free` | When GC is triggered by `min-free`, stop once this much free space exists (default: effectively unlimited). |

**Common pitfall: builds without a lasting root.** `nix build`, `nix-build`, and similar commands may register a `result` symlink (under `gcroots/auto/`) so the output survives until you remove that link. If you use `--no-link` / `--no-out-link`, or delete `result` without installing into a profile, the built paths have no lasting root and become GC-eligible on the next collection—even if you still expect them on disk.

**Related layout.** GC roots and profile state live under `/nix/var/nix/` (not inside `/nix/store` itself). See [Nix store layout](nix-store-layout.md).

## Examples

**Delete all unreachable store paths:**

```bash
nix-store --gc
```

**Free at least 500 MiB, then stop:**

```bash
nix-store --gc --max-freed 500M
```

**Inspect roots and dead paths without deleting:**

```bash
nix-store --gc --print-roots
nix-store --gc --print-dead
```

**Drop old profile generations, then collect garbage** (more aggressive; removes rollback to deleted generations):

```bash
nix-collect-garbage -d
```

**Keep recent generations; delete ones older than 30 days, then GC:**

```bash
nix-collect-garbage --delete-older-than 30d
```

## References

- [Nix reference manual — garbage collection](https://nix.dev/manual/nix/stable/package-management/garbage-collection.html)
- [Nix reference manual — `nix-store --gc`](https://nix.dev/manual/nix/stable/command-ref/nix-store/gc.html)
- [Nix reference manual — `nix-collect-garbage`](https://nix.dev/manual/nix/stable/command-ref/nix-collect-garbage.html)
- [Nix reference manual — garbage collector roots](https://nix.dev/manual/nix/stable/package-management/garbage-collector-roots.html)
- [Nix reference manual — `nix.conf`](https://nix.dev/manual/nix/stable/command-ref/conf-file.html)

## See also

- [Profile](../02-concepts/profile.md) — user and system environments whose generations are GC roots
- [Generation](../02-concepts/generation.md) — numbered profile snapshots; deleting old ones enables reclamation
- [Closure](../02-concepts/closure.md) — dependency set kept alive with a rooted path
- [Store path](../02-concepts/store-path.md) — individual immutable store objects
- [Nix store layout](nix-store-layout.md) — `/nix/store` vs `/nix/var/nix/` (profiles, gcroots)
- [Binary caches](binary-caches.md) — substituting paths back after GC deletes local copies
