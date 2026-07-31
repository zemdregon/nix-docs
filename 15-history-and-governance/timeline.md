---
status: complete
---

# Timeline

## Overview

The Nix stack grew from a research deployment model into a package collection, a Linux distribution, and a multi-implementation ecosystem. This page is a **milestone map**, not a full institutional history: prefer primary announcements, theses, release notes, and RFCs over secondary retellings.

Dates below are pinned to primary sources where possible. Items marked **approximate** are early or poorly dated in public archives (imports, prototypes, informal starts). Governance drama and fork politics belong on [Forks and governance splits](forks-and-governance-splits.md); this page only notes when alternative implementations became public facts.

Project home and current product surface: [nixos.org](https://nixos.org/).

## Details

### Research origins (≈2003–2006)

- **≈2003 — Nix begins.** The C++ lineage now called [CppNix](../13-implementations/nix-evaluator/cpp-nix.md) starts as research software at Utrecht University under Eelco Dolstra (with Eelco Visser and collaborators). The Git history of [NixOS/nix](https://github.com/NixOS/nix) retains an early import dated **2003-03-13** (“Initial version of nix”); treat that as an approximate start of recorded source, not a product launch.
- **2004 — Early papers and Nixpkgs releases.** The LISA ’04 paper *Nix: A Safe and Policy-Free System for Software Deployment* describes the model. A **2004-11-14** nix-dev announcement ships **Nix 0.6** together with a **Nix Packages** (Nixpkgs) 0.6 tarball—evidence that the package collection already existed as a named release by late 2004.
- **2006-01-18 — PhD thesis defended.** Dolstra defends *The Purely Functional Software Deployment Model* at Utrecht University (title page: public defense **2006-01-18**; nixos.org blog posts a short note on **2006-02-18**). The thesis is the canonical design document for the store, Nix expressions, and transparent source/binary deployment.

### Nixpkgs and NixOS (2006–2013)

- **2006 — NixOS as a research OS.** Armijn Hemel’s Master’s thesis *NixOS: The Nix Based Operating System* (2006) describes applying Nix to a whole Linux system. Public blog progress reports and ISOs become frequent in **2007** (x86_64 ISO, desktop experiments, HotOS XI paper). Wikipedia’s “initial release 2006-06-03” is widely repeated but not mirrored by a clear nixos.org announcement of that day—treat mid-2006 as **approximate** for “first runnable NixOS,” and use 2007 blog posts for verified public demos.
- **2006-03-03 — Nixpkgs 0.9** announced on the project blog (earlier 0.6 already existed in 2004; 0.9 is a convenient early blog-dated milestone).
- **2011–2013 — GitHub and monorepo.** Migration from Subversion toward the NixOS GitHub org is announced **2011-11-28**. On **2013-10-10** / blog **2013-11-10**, the NixOS Git tree is merged into Nixpkgs (`nixos/` subdirectory)—the layout still used today.
- **2013-10-31 / 2013-12-01 — First stable NixOS branch.** Eelco Dolstra announces the **13.10** (“Aardvark”) stable branch on nix-dev (**2013-10-31**); the project blog posts “NixOS 13.10 released” on **2013-12-01**. This is the start of the stable-channel model; cadence details: [Release cadence](release-cadence.md).

### Foundation, Nix 2.x, and flakes (2015–2021+)

- **2015-06 / 2015-07 — NixOS Foundation.** Board members announce that the foundation “came to life” the previous month (nix-dev, **2015-07**). Role and continuity: [NixOS Foundation](nixos-foundation.md).
- **2018-02-22 — Nix 2.0.** Official release introduces the new `nix` CLI intended to replace many `nix-*` tools (still evolving afterward). Release notes and blog both date **2018-02-22**.
- **2019-07 — Flakes proposed (RFC 49).** [RFC 0049](https://github.com/NixOS/rfcs/pull/49) opened **2019-07-15** proposing flakes as composable, lockable Nix projects. The RFC was later **withdrawn** (`status: withdrawn`); flakes shipped anyway as an **experimental** feature. Process context: [RFC process](rfc-process.md) and [github.com/NixOS/rfcs](https://github.com/NixOS/rfcs).
- **2021-11-01 — Nix 2.4.** Release notes introduce flakes and selective `experimental-features` gating; flakes and the new CLI remain marked experimental. As of **Nix 2.34** (mid-2026) they are still gated behind `experimental-features` in CppNix—do not treat “widely used” as “stabilized.”

### Multiple implementations (2024–)

- **≈2024-02 — Lix work begins.** The [Lix 2.90 announcement](https://lix.systems/blog/2024-07-10-lix-2.90-release/) states the project began in **late February 2024**, forking from CppNix **2.18**.
- **2024-05 — Public Lix discussion.** Discourse thread *Lix: an independent variant of the Nix package manager* appears **2024-05-06** (community notice, not the project’s own release post)—treat as approximate public-awareness, not a release date.
- **2024-07-10 — Lix 2.90.** First numbered Lix release (“Vanilla Ice Cream”), positioned as a compatible C++-lineage alternative focused on reliability and UX. Broader fork/governance map: [Forks and governance splits](forks-and-governance-splits.md); evaluator page: [Lix](../13-implementations/nix-evaluator/lix.md); project site: [lix.systems](https://lix.systems/).

Other evaluators (Tvix, Snix, Determinate Nix as a distribution, etc.) are out of scope here except as pointers from the implementations domain.

## Examples

**Compact milestone table** (years only; see Details for day-level citations):

| Year | Milestone | Certainty |
|------|-----------|-----------|
| ≈2003 | Nix source history begins | Approximate (git import) |
| 2004 | Nix / Nixpkgs 0.6 announced | Verified (nix-dev) |
| 2006 | Dolstra PhD; NixOS research OS | Verified thesis / thesis year |
| 2007 | Public NixOS desktop / HotOS | Verified (blog) |
| 2013 | NixOS⊂nixpkgs; stable 13.10 | Verified (blog / nix-dev) |
| 2015 | NixOS Foundation | Verified (nix-dev) |
| 2018 | Nix 2.0 | Verified (release notes) |
| 2019 | Flakes RFC 49 opened | Verified (RFC) |
| 2021 | Nix 2.4; flakes experimental | Verified (release notes) |
| 2024 | Lix fork era / 2.90 | Verified (Lix blog) |

**Check a claim against primary text** before repeating it:

```bash
# Which Nix implementation / version am I on?
nix --version

# Flakes / nix-command still gated? (CppNix ≥2.4; needs experimental nix-command)
nix config show 2>/dev/null | grep -E '^experimental-features' || true
```

For historical announcements, prefer the [nixos.org blog/announcements index](https://nixos.org/blog/announcements/) and versioned [Nix release notes](https://nix.dev/manual/nix/stable/release-notes/) over wiki mirrors.

## References

- [The Purely Functional Software Deployment Model](https://edolstra.github.io/pubs/phd-thesis.pdf) — Dolstra PhD thesis (defended 2006-01-18)
- [PhD thesis defended](https://nixos.org/blog/announcements/2006/phd-thesis-defended-2006/) — nixos.org blog note (2006-02-18)
- [Nix & NixOS](https://nixos.org/) — project homepage
- [Blog / Announcements](https://nixos.org/blog/announcements/) — dated primary project news
- [Nix 2.0 released](https://nixos.org/blog/announcements/2018/nix-20/) — 2018-02-22
- [Release 2.0 (2018-02-22)](https://nix.dev/manual/nix/stable/release-notes/rl-2.0.html) — Nix 2.0 release notes
- [Release 2.4 (2021-11-01)](https://nix.dev/manual/nix/stable/release-notes/rl-2.4.html) — flakes + experimental-features
- [NixOS 13.10 released](https://nixos.org/blog/announcements/2013/nixos-1310/) — first stable branch (blog 2013-12-01)
- [NixOS sources merged into Nixpkgs](https://nixos.org/blog/announcements/2013/nixos-sources-merged-into-nixpkgs-2013/) — 2013-11-10
- [NixOS RFCs](https://github.com/NixOS/rfcs) — RFC repository
- [RFC 0049 Flakes (PR)](https://github.com/NixOS/rfcs/pull/49) — flakes proposal (opened 2019-07-15; later withdrawn)
- [Lix](https://lix.systems/) — Lix project homepage
- [Announcing Lix 2.90](https://lix.systems/blog/2024-07-10-lix-2.90-release/) — first Lix release; notes late-Feb 2024 start, fork from 2.18

## See also

- [NixOS Foundation](nixos-foundation.md) — legal/funding entity (from 2015)
- [RFC process](rfc-process.md) — how RFCs relate to shipped features
- [Release cadence](release-cadence.md) — NixOS stable branch schedule
- [Forks and governance splits](forks-and-governance-splits.md) — governance and implementation forks
- [CppNix](../13-implementations/nix-evaluator/cpp-nix.md) — reference C++ Nix implementation
- [Lix](../13-implementations/nix-evaluator/lix.md) — CppNix-lineage fork (from 2024)
