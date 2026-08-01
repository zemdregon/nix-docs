---
status: complete
---

# Getting Help and Community

## Overview

Official Nix / NixOS support and discussion live on [Discourse](https://discourse.nixos.org/) (async forum), the [Matrix space](https://matrix.to/#/#space:nixos.org) (real-time chat), and [GitHub](https://github.com/NixOS/) (issues and PRs). The [community page](https://nixos.org/community/) is the index of moderated spaces, teams, calendars, and meetups. This wiki synthesizes manuals and patterns; it is not live support—search manuals and prior threads before posting.

## Details

### Read first

Before opening a thread or chat:

1. Manuals and [search.nixos.org](https://search.nixos.org/) for your channel or flake pin — see [Reading manuals and search](../00-roadmap/reading-manuals-and-search.md).
2. Common failure modes — [FAQ: common errors](../cheatsheets/faq-common-errors.md) and [Troubleshooting](../09-nixos/operations/troubleshooting.md).
3. Discourse search (and Matrix room history if you already chat there) for the same error string or option name.

### Where to go

| Channel | Use for | Prefer when |
|---------|---------|-------------|
| **Discourse** ([discourse.nixos.org](https://discourse.nixos.org/)) | Help questions, longer debugging, design discussion, announcements | You want searchable answers, can wait hours–days, or need a durable thread |
| **Matrix** ([`#space:nixos.org`](https://matrix.to/#/#space:nixos.org)) | Real-time help, development chat, off-topic | Quick clarification; room list and culture live under the space linked from the [community page](https://nixos.org/community/)—do not invent room names |
| **GitHub issues** ([NixOS org](https://github.com/NixOS/)) | Bugs and actionable defects in a specific repo | Package/module bug → [nixpkgs](https://github.com/NixOS/nixpkgs/issues); Nix CLI/evaluator → [nix](https://github.com/NixOS/nix/issues); include a minimal repro |
| **RFCs** ([NixOS/rfcs](https://github.com/NixOS/rfcs)) | Substantial design that needs ecosystem consensus | Large language/Nixpkgs/OS interface changes — see [RFC process](rfc-process.md) |
| **This wiki** | Vocabulary, architecture, cross-links | Learning structure; not incident support |

Discourse categories change over time; useful entry points include **Help** (`/c/learn`), **Development** (subcategories such as Nix and Nixpkgs Architecture), **Announcements**, **Guides**, and language-specific Help subforums. Pick the closest category and search it before posting.

Official spaces on the community page are moderated by the NixOS Moderation Team. Report abuse to `moderation@nixos.org`. Unofficial spaces (meetups, third-party chats) may use different rules—the community page labels them separately.

Governance context (foundation, boards, forks): [NixOS Foundation](nixos-foundation.md), [Forks and governance splits](forks-and-governance-splits.md).

### Norms for asking well

- State the goal in one sentence, then the failure (exact error text).
- Give versions: `nix --version`; on NixOS, the release or generation; whether you use **flakes** or **channels**/`NIX_PATH`.
- Minimal reproduction: smallest `flake.nix` / `configuration.nix` / expression that fails—not a full private config.
- For evaluation failures, retry with `--show-trace` and paste the relevant tail (not megabytes of logs).
- Redact secrets: tokens, private keys, `sops`/`agenix` material, personal hostnames if needed.
- Prefer Discourse for anything others will search for later; use Matrix for short back-and-forth, then summarize the fix on Discourse if it is generally useful.

## Examples

### Checklist before posting (Discourse Help)

```text
1. Searched Discourse + manuals for the error / option name
2. nix --version  →  …
3. NixOS release or flake inputs (nixpkgs rev / channel)  →  …
4. Flakes? yes/no
5. Command that fails (exact)
6. Minimal config / expression (5–20 lines)
7. Error output (trimmed); used --show-trace if eval failed
8. No secrets in the paste
```

### Choosing the venue (examples)

- “`services.nginx` option missing after upgrade” → manuals/search first, then Discourse Help (or nixpkgs issue if you confirmed a packaging/module regression).
- “How do I structure a flake with multiple hosts?” → Discourse or Matrix; wiki [config-repo patterns](../07-flakes/workflows/config-repo-layout.md) for synthesis.
- “Package `foo` fails to build on `x86_64-linux`” → nixpkgs issue with `nix-build`/`nix build` log and platform.
- “Proposal: change default NixOS release schedule” → [RFC process](rfc-process.md), not a Help thread alone.

## References

- [NixOS community](https://nixos.org/community/) — official spaces, Matrix space, teams, moderation contact
- [NixOS Discourse](https://discourse.nixos.org/) — primary async forum
- [NixOS Matrix space](https://matrix.to/#/#space:nixos.org) — entry point linked from the community page
- [NixOS on GitHub](https://github.com/NixOS/) — nix, nixpkgs, and related repos
- [NixOS/rfcs](https://github.com/NixOS/rfcs) — RFC repository

## See also

- [Reading manuals and search](../00-roadmap/reading-manuals-and-search.md)
- [FAQ: common errors](../cheatsheets/faq-common-errors.md)
- [Troubleshooting](../09-nixos/operations/troubleshooting.md)
- [RFC process](rfc-process.md)
- [NixOS Foundation](nixos-foundation.md)
- [Forks and governance splits](forks-and-governance-splits.md)
- [Glossary](../glossary.md)
