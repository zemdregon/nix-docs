---
status: complete
---

# Forks and Governance Splits

## Overview

The Nix *language and store model* are shared ideas; the *implementations* and *project structures* around them are not a single monolith. The widely used C++ lineage lives primarily as [CppNix](../13-implementations/nix-evaluator/cpp-nix.md) ([NixOS/nix](https://github.com/NixOS/nix)), the reference implementation shipped with NixOS. [Lix](../13-implementations/nix-evaluator/lix.md) is a documented community fork of that lineage (last shared release: CppNix 2.18), with its own releases, hosting, and governance.

This page is a high-level map of that fork and of how governance is organized on each side—drawn from first-party project statements, not chat lore. For chronology and Foundation structure, see [Timeline](timeline.md) and [NixOS Foundation](nixos-foundation.md). For evaluator behavior and install details, prefer the implementation pages over this summary.

## Details

### Two C++-lineage implementations

| | [CppNix](../13-implementations/nix-evaluator/cpp-nix.md) | [Lix](../13-implementations/nix-evaluator/lix.md) |
|--|--|--|
| Upstream | [NixOS/nix](https://github.com/NixOS/nix) | [lix.systems](https://lix.systems/) (community variant) |
| Lineage | Reference C++ Nix | Fork of CppNix; last shared release **2.18** ([About Lix](https://lix.systems/about/)) |
| Compatibility (stated) | Baseline for “stock Nix” | Designed to stay compatible with existing Nix expressions while evolving tooling |
| Typical role | Default on NixOS; most tutorials assume this binary | Drop-in alternative daemon/CLI when deliberately installed |

Lix’s first-party positioning ([About Lix](https://lix.systems/about/), [homepage](https://lix.systems/)): correctness, usability, selective stability guarantees, community-owned infrastructure, and language/tooling evolution without sacrificing backwards compatibility for valid clients. Documented technical deltas versus CppNix (lazy trees, CA derivations stance, build system, etc.) belong on the [Lix](../13-implementations/nix-evaluator/lix.md) page—verify against current Lix docs before relying on any single difference.

Other evaluators ([Tvix](../13-implementations/nix-evaluator/tvix.md), [Snix](../13-implementations/nix-evaluator/snix.md)) are separate implementation efforts, not CppNix forks in the same sense. Compare them on the [implementations](../13-implementations/nix-evaluator/README.md) index.

### Governance: separate projects, separate rules

**Nix / NixOS community side.** Official community structure—Foundation board, Steering Committee, specialized teams (Nix, Nixpkgs, moderation, releases, and others)—is described on the [NixOS community](https://nixos.org/community/) page. Technical direction for shared ecosystem changes also runs through the [RFC process](rfc-process.md). Legal and operational support for shared infrastructure sits with the [NixOS Foundation](nixos-foundation.md).

**Lix side.** Lix publishes its own binding [governance](https://lix.systems/governance/) document: overlapping **core team** (technical stewardship, strategy, conflict resolution), **community team** (moderation, culture, public presence), and **committers** (day-to-day merge authority). Decision-making defaults to consensus where possible; the document defines voting and escalation when consensus fails. Hosting and sponsorship posture are stated by Lix (community-owned infrastructure; open conflict-of-interest statements)—see [About Lix](https://lix.systems/about/).

These are **parallel** governance surfaces. Choosing an implementation does not automatically change which Foundation or Lix bodies govern the other project’s repositories, caches, or moderation spaces.

### Documented tensions (stick to project text)

Treat secondary retellings as non-authoritative. First-party Lix materials state, among other things:

- Lix exists partly as an alternative to “commercial interests that have long plagued both upstream CppNix and corporate-authored forks,” and emphasizes volunteer governance and published conflict-of-interest posture ([About Lix](https://lix.systems/about/)).
- Lix cites significant regressions in upstream CppNix in recent years and notes that Nixpkgs has repeatedly opted not to default stable-channel users to the latest CppNix release; Lix’s “Lix on main” program is framed as keeping releases close to daily drivers ([About Lix](https://lix.systems/about/)).
- Lix and Snix are described as similar goals, different approaches (evolve the C++ lineage vs greenfield Rust), with possible future component sharing ([About Lix](https://lix.systems/about/)).

CppNix / NixOS community docs do not need to “answer” every Lix claim on this page; they define their own teams, moderation, and RFC path on [nixos.org/community](https://nixos.org/community/). For a neutral reading path: implementation facts → implementation leaf; org structure → Foundation / community / Lix governance docs; dated events → [Timeline](timeline.md).

## Examples

**Which binary is on `PATH`?** Fork vs upstream is an install choice; version output differs:

```bash
nix --version
which nix
```

CppNix typically reports as `nix (Nix) …`. Lix documents output containing `Lix` (exact wording changes by release)—see [Lix](../13-implementations/nix-evaluator/lix.md).

**Where to look next (by question):**

| Question | Prefer |
|----------|--------|
| CLI flags, experimental features, NixOS default | [CppNix](../13-implementations/nix-evaluator/cpp-nix.md) |
| Lix install, deltas, Flakes stance | [Lix](../13-implementations/nix-evaluator/lix.md) |
| Shared community teams / Foundation | [nixos.org/community](https://nixos.org/community/), [NixOS Foundation](nixos-foundation.md) |
| Lix decision-making | [Lix governance](https://lix.systems/governance/) |
| Dated history of splits | [Timeline](timeline.md) |

## References

- [Lix homepage](https://lix.systems/) — project positioning and ecosystem overview
- [About Lix](https://lix.systems/about/) — fork from CppNix 2.18; stated goals, community posture, technical differences
- [Lix governance](https://lix.systems/governance/) — core team, community team, committers
- [NixOS/nix](https://github.com/NixOS/nix) — official CppNix source
- [NixOS community](https://nixos.org/community/) — Foundation, Steering Committee, teams, moderation

## See also

- [Timeline](timeline.md) — chronological history of the ecosystem
- [NixOS Foundation](nixos-foundation.md) — Foundation role and infrastructure support
- [RFC process](rfc-process.md) — shared proposal path for Nix / Nixpkgs / NixOS
- [CppNix](../13-implementations/nix-evaluator/cpp-nix.md) — reference C++ implementation
- [Lix](../13-implementations/nix-evaluator/lix.md) — CppNix-lineage fork
- [Nix evaluator implementations](../13-implementations/nix-evaluator/README.md) — CppNix, Lix, Tvix, Snix index
