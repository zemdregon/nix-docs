---
status: complete
---

# RFC Process

## Overview

**NixRFCs** are the community design process for *substantial* changes across the Nix ecosystem—language semantics and syntax, Nixpkgs structure and scope, and major new interfaces—not for routine package bumps or non-breaking bug fixes. Proposals live as Markdown under [`rfcs/`](https://github.com/NixOS/rfcs/tree/master/rfcs) in the [NixOS/rfcs](https://github.com/NixOS/rfcs) repository; an accepted RFC is a merged document there, not a guarantee that code lands on any schedule.

Ordinary GitHub PRs remain the path for most work. Substantial PRs without a linked RFC may be closed. RFCs and experimental feature flags are orthogonal: an RFC records design consensus; a flag gates an implementation—see [Tracking stabilization](../08-experimental-features/tracking-stabilization.md).

## Details

**When an RFC is expected.** Norms evolve, but typical triggers include:

- Semantic or syntactic language changes that are not bug fixes; removing language features
- Large Nixpkgs restructuring, or expanding Nixpkgs scope (new architectures, major subprojects)
- New interfaces or functions with broad impact

**Usually not an RFC:** adding/updating/removing packages; security and bug fixes that do not break interfaces.

**Roles (from the process docs / RFC 36).**

| Role | Job |
|------|-----|
| **RFC Steering Committee (RFCSC)** | Nominate and assign a Shepherd Team (unanimously; process docs target about a week after PR open); supervise process; merge accepted or close rejected RFCs. No special authority over *content*—they weigh in like anyone else. Current members: [nixos.org team page](https://nixos.org/community/teams/rfc-steering-committee). |
| **Shepherd Team** | 3–4 people familiar with the touched area; author cannot serve; at most half may be RFCSC. Guide discussion, summarize state, and move for Final Comment Period (FCP). Decide accept/reject after FCP. |
| **Shepherd Leader** | Keeps the process moving for that RFC; does not break Shepherd deadlocks alone. |

**Lifecycle (creation → merge).**

1. Draft the RFC (motivation, design, drawbacks, alternatives). Optional: Discourse [pre-RFC](https://discourse.nixos.org/c/dev/rfc-steering-committee/33); optional prototype for technical proposals.
2. Open a PR against [NixOS/rfcs](https://github.com/NixOS/rfcs). Community nominates Shepherds (self or others).
3. RFCSC assigns Shepherds and a leader. Iterate in the PR thread; keep edits as new commits (no squash/rebase once history is public on the PR).
4. Shepherds motion for **FCP** with a disposition (usually merge or close) once tradeoffs are clear enough—not requiring unanimous community consensus, but without a strong consensus *against* the disposition outside the team. All Shepherds must sign off.
5. FCP is announced (notably [Discourse RFC announcements](https://discourse.nixos.org/c/announcements/rfc-announcements/22)) and lasts **ten calendar days** from that announcement. Substantial new arguments can cancel FCP and return the RFC to discussion.
6. On accept, RFCSC merges; on reject (or stuck idea-without-consensus), the PR is closed. Authors may withdraw; “on hold” uses GitHub Draft + `status: on hold`. Lack of Shepherds after roughly two months can close as insufficient interest (reopenable).

**After acceptance.** The merged Markdown is a decision snapshot (closer to a Matrix Spec Proposal than an IETF normative RFC)—not a priority assignment and not a promise someone else will implement. Implementation usually follows in Nix, Nixpkgs, or related repos; acceptance means major stakeholders agreed in principle, but merge of code can still fail on technical grounds. Substantial later changes need a new RFC; only tiny amendments go back to the original document.

**Operational note (2025).** With lower repository activity, the RFCSC shifted to an **on-demand** workflow: ping `@NixOS/rfc-steering-committee` on GitHub for shepherd assignment or FCP/merge requests; the committee may not meet weekly. See the [2025-05-26 meeting notes](https://discourse.nixos.org/t/rfcsc-meeting-2025-05-26/64791). The documented roles and FCP rules above still apply; cadence of committee meetings does not.

## Examples

**Illustrative “needs an RFC” vs “normal PR”:**

| Change | Path |
|--------|------|
| New `pname`/`version` packaging convention | Historical: [RFC 0035](https://github.com/NixOS/rfcs/blob/master/rfcs/0035-package-naming.md) |
| Bump `hello` in nixpkgs | Ordinary PR |
| Language syntax addition (e.g. pipe operator discussions) | RFC PR under `NixOS/rfcs` |
| Security fix with unchanged interfaces | Ordinary PR |

**Minimal author checklist:**

1. Write motivation, design, alternatives, and drawbacks in the RFC template under `rfcs/`.
2. Optionally gather early feedback on Discourse; open the GitHub PR when ready for review.
3. Help recruit Shepherd nominations; respond to review with additional commits.
4. After accept, implement (or coordinate implementation) in the relevant repo—do not assume automatic pickup.

## References

- [NixOS/rfcs](https://github.com/NixOS/rfcs) — canonical process README, templates, and accepted RFCs
- [RFC 0036 (process / Shepherd amendment)](https://github.com/NixOS/rfcs/blob/master/rfcs/0036-rfc-process-team-amendment.md)
- [RFC Steering Committee (nixos.org)](https://nixos.org/community/teams/rfc-steering-committee)
- [RFCSC meeting 2025-05-26 (on-demand workflow)](https://discourse.nixos.org/t/rfcsc-meeting-2025-05-26/64791)
- [Discourse: RFC announcements](https://discourse.nixos.org/c/announcements/rfc-announcements/22)

## See also

- [NixOS Foundation](nixos-foundation.md)
- [Timeline](timeline.md)
- [Release cadence](release-cadence.md)
- [Tracking stabilization](../08-experimental-features/tracking-stabilization.md)
