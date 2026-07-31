---
status: complete
---

# NixOS Foundation

## Overview

The **NixOS Foundation** (Dutch: *Stichting NixOS Foundation*) is a registered Dutch non-profit (Kamer van Koophandel number `63520583`; [impressum](https://github.com/NixOS/foundation/blob/master/impressum.md)). Its mission is to support infrastructure and projects that implement the purely functional deployment model—especially Nix, Nixpkgs, and NixOS.

The Foundation is one of two top-level leadership bodies for the Nix community (alongside the elected [Steering Committee](https://nixos.org/governance/)). The board focuses on legal, financial, and partnership work; technical and day-to-day community direction sits with the Steering Committee and the many volunteer teams listed on the [community](https://nixos.org/community/) site.

## Details

### Mission and operations

Per the community site, the Foundation supports the ecosystem’s infrastructure and related projects. In particular it operates or funds:

| Asset / activity | Role |
|------------------|------|
| [cache.nixos.org](https://cache.nixos.org) | Official binary cache (community page cites 120TB+ of prebuilt packages). |
| [hydra.nixos.org](https://hydra.nixos.org) | Official Hydra build farm (hundreds of macOS / x86_64 / aarch64 cores; community page cites 350k+ builds per week). |
| Event funding | Fiscal support for community events and related efforts. |

Contact: `foundation@nixos.org`.

### Board vs Steering Committee

Official governance pages describe a partnership:

- **Foundation board** — administrative and legal ownership; interface to corporate, governmental, and financial actors; trademarks; external relationships, partnerships, and donations; grants; payments for tooling, meetups, and infrastructure; credentials and permissions; fiscal planning and funding envelopes for events and efforts. Both board and Steering Committee approve certain foundation policies (for example sponsorship eligibility and trademark policy).
- **Steering Committee (SC)** — elected technical and social community leadership; project direction; final escalation for community matters; within Foundation funding envelopes, the SC sets priorities for events and efforts.

The [Nix Governance Constitution](https://github.com/NixOS/org/blob/main/doc/constitution.md) (linked from [nixos.org/governance](https://nixos.org/governance/)) defines each body’s responsibilities and how the SC is elected. Current board members are listed on the [community](https://nixos.org/community/) and [foundation board](https://nixos.org/community/teams/foundation-board/) pages.

### Funding

Infrastructure, development support, and events are funded by users and sponsors. Official channels include:

- **[Open Collective](https://opencollective.com/nixos)** — single or recurring card donations; finances are public.
- **Organizational sponsorship** — tiers and benefits on the [sponsorship](https://nixos.org/sponsorship/) page.
- **SEPA bank transfer** — to *Stichting NixOS Foundation* (details on the [donate](https://nixos.org/donate/) page); large annual amounts should go through `foundation@nixos.org` for tax handling.
- Merchandise sales (shop linked from the donate page).

The donate page emphasizes that the build farm and binary cache are expensive to run and depend on ongoing support.

### Events and community stewardship

The Foundation’s public community materials emphasize inclusive participation and a welcoming environment. Official spaces (Discourse, Matrix, GitHub) are moderated by the Moderation Team; moderation reports go to `moderation@nixos.org`.

**NixCon** is the annual community conference, organized by the NixCon Team (not the board day-to-day). Past and upcoming editions are listed under [Community → NixCon](https://nixos.org/community/). Local meetups and official calendars are also linked from that page. The board’s role is fiscal and organizational support (funding envelopes, payments), not replacing the NixCon or meetup organizers.

Related process: the community [RFC process](rfc-process.md) is the controlled path for major language, packaging, and OS changes; RFCs are community/SC territory, not Foundation board product decisions.

## Examples

**What the Foundation is for (official framing):**

- Paying for and operating shared infrastructure (`cache.nixos.org`, `hydra.nixos.org`).
- Handling donations, sponsorships, grants, and legal/trademark matters.
- Funding envelopes for events and community efforts; the SC prioritizes within those envelopes.

**What it is not (per the same split):**

- Day-to-day package or Nix evaluator maintainership — teams and the SC.
- Writing or accepting RFCs — RFC shepherds / RFC Steering Committee.
- Moderating chat rooms — Moderation Team (with Foundation-backed community standards).

**Find current people and money routes:**

1. Board roster and team list → [nixos.org/community](https://nixos.org/community/)
2. Donate / sponsor → [nixos.org/donate](https://nixos.org/donate/), [nixos.org/sponsorship](https://nixos.org/sponsorship/)
3. Governance constitution and SC elections → [nixos.org/governance](https://nixos.org/governance/)

## References

- [Community](https://nixos.org/community/) — Foundation mission, board listing, teams, NixCon, calendars
- [Nix & NixOS home](https://nixos.org/) — project landing page
- [Governance](https://nixos.org/governance/) — Foundation board vs Steering Committee; constitution links
- [Foundation board team](https://nixos.org/community/teams/foundation-board/) — board responsibilities in detail
- [Nix Governance Constitution](https://github.com/NixOS/org/blob/main/doc/constitution.md) — formal board/SC scopes and SC elections
- [Donate](https://nixos.org/donate/) — Open Collective, SEPA, sponsorship pointer
- [Sponsorship](https://nixos.org/sponsorship/) — organizational sponsorship tiers
- [Foundation impressum](https://github.com/NixOS/foundation/blob/master/impressum.md) — KvK, VAT, registered address

## See also

- [Timeline](timeline.md) — historical milestones for Nix / NixOS
- [RFC process](rfc-process.md) — how major technical changes are proposed and decided
- [Forks and governance splits](forks-and-governance-splits.md) — alternate implementations and governance divergences
- [Release cadence](release-cadence.md) — NixOS twice-yearly releases (Release Team)
