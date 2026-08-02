---
status: active
---

# Release / freshness checklist

Operational checklist for ongoing freshness (Phase 5.1 cadence). Run on each cadence trigger below so release facts, experimental flags, CLI stamps, mesh/Clan notes, and evaluator maturity do not rot.

This is a meta process doc, not a subject article. Pair with [research-method.md](research-method.md) when rewriting leaves and [quality-checklist.md](quality-checklist.md) when reaffirming `complete`.

## Triggers (when to run)

| Trigger | Primary focus |
|---------|----------------|
| Each **NixOS** release | Experimental hub; release cadence; installer/download/channel cites |
| Each **major Nix** release | CLI cheatsheet; feature flags; modern CLI leaves; store/protocol notes |
| **Quarterly** | Clan/mesh; evaluator landscape; adjacent tools |
| **As noticed** | Renames, forks, dead projects, broken upstream URLs |

Pick the matching section; always finish with [After every refresh](#after-every-refresh).

## Each NixOS release

- [ ] Re-stamp [08-experimental-features/tracking-stabilization.md](../08-experimental-features/tracking-stabilization.md) and [experimental-backlog.md](../08-experimental-features/experimental-backlog.md) against the Nix experimental-features manual and NixOS/Nix release notes (see [References](#references)).
- [ ] Update [15-history-and-governance/release-cadence.md](../15-history-and-governance/release-cadence.md) with current schedule / channel naming if changed.
- [ ] Spot-check download and channel facts against [nixos.org/download](https://nixos.org/download/) and [channels.nixos.org](https://channels.nixos.org/); skim [status.nixos.org](https://status.nixos.org/) for channel health context.
- [ ] Version-stamp installer / ops cites that mention a NixOS release number (search leaves that hard-code `YY.MM`).
- [ ] Set or refresh `last-checked: YYYY-MM` on churny experimental / release leaves when conventions allow.

## Each major Nix release

- [ ] Refresh [cheatsheets/cli.md](../cheatsheets/cli.md) for new, renamed, or removed commands and flags.
- [ ] Walk [05-cli-and-tooling/](../05-cli-and-tooling/README.md) leaves that mention experimental or unstable CLI (`nix-command`, flakes-related flags, store ops); version-stamp against the releasing Nix version.
- [ ] Diff experimental feature list vs [tracking-stabilization.md](../08-experimental-features/tracking-stabilization.md) / [experimental-backlog.md](../08-experimental-features/experimental-backlog.md) (stabilize / remove / rename).
- [ ] Note store or protocol behavior changes only where this wiki already covers them; do not invent new APIs.

## Quarterly (Clan / mesh, evaluators, adjacent tools)

- [ ] Refresh [12-deployment-and-infra/clan-and-mesh.md](../12-deployment-and-infra/clan-and-mesh.md) and concept cousin [02-concepts/machine-mesh.md](../02-concepts/machine-mesh.md) against current Clan/mesh docs (names, scope, trust boundaries).
- [ ] Update evaluator maturity / last-checked on [13-implementations/nix-evaluator/](../13-implementations/nix-evaluator/README.md): [CppNix](../13-implementations/nix-evaluator/cpp-nix.md), [Lix](../13-implementations/nix-evaluator/lix.md), [Tvix](../13-implementations/nix-evaluator/tvix.md), [Snix](../13-implementations/nix-evaluator/snix.md).
- [ ] Skim [05-cli-and-tooling/adjacent-tools/](../05-cli-and-tooling/adjacent-tools/README.md) for renamed tools, abandoned projects, or stale install advice.
- [ ] Set `last-checked: YYYY-MM` on mesh, evaluator, and adjacent-tool leaves that changed.

## As noticed (renames / forks / dead projects)

- [ ] Fix rename or fork callouts (e.g. Snix/Tvix/Lix) on the affected leaf; add a short “former name / status” note if readers will search the old term.
- [ ] Mark abandoned or misleading projects clearly; prefer primary-source confirmation over Discord lore.
- [ ] Fix or remove dead upstream URLs; sync [sources.md](sources.md) when a canonical row changes.

## After every refresh

- [ ] Run `node meta/audit/broken-links.mjs` from the repo root; fix any broken relative links introduced or exposed by the pass.
- [ ] Update [sources.md](sources.md) rows if recurring canonical URLs changed or were added.
- [ ] Leave subject `status` alone unless the leaf was rewritten enough to need [quality-checklist.md](quality-checklist.md) again.

## See also

- [todo-coverage.md](todo-coverage.md) — remaining work and historical campaign checkoffs
- [quality-checklist.md](quality-checklist.md) — complete-pass rubric (`last-checked`, examples, refs)
- [research-method.md](research-method.md) — pack → write → verify loop
- [conventions.md](conventions.md) — status values and linking rules
- [sources.md](sources.md) — canonical upstream URL table

## References

- [Nix experimental features (stable manual)](https://nix.dev/manual/nix/stable/development/experimental-features.html)
- [NixOS download](https://nixos.org/download/)
- [NixOS channel status](https://status.nixos.org/)
- [Nix channels](https://channels.nixos.org/)
