---
status: active
---

# Quality checklist (complete pass)

Short verify rubric before setting frontmatter `status: complete`. See also [research-method.md](research-method.md) and [todo-coverage.md](todo-coverage.md).

## Must pass

- [ ] Overview + Details accurate against primary sources (manual / RFC / upstream README)
- [ ] Minimal example (5–20 lines) verified or explicitly noted why it cannot run offline
- [ ] No invented options, flags, or APIs
- [ ] Experimental / unstable CLI stamped with Nix or NixOS version where relevant
- [ ] ≥1 wiki-relative link with existing target; useful `## See also` (2–6) when cousins exist
- [ ] ≥1 stable upstream URL under `## References`
- [ ] Absolute claims cited or softened; no Discord-only lore as fact
- [ ] Tone matches gold pages (e.g. `01-philosophy/why-nix.md`): concise, no marketing, no emoji

## Complete+ (optional deepen bar)

Use after a leaf is already `complete` when calibrating toward runbook-grade density. Not required for baseline `complete` status.

- [ ] **Lifecycle or decision artifact** — mermaid diagram, comparison table, or decision tree where the topic has stages or choices
- [ ] **Boundaries** — short “what this page is not” (or equivalent scope note) on concept and operator leaves
- [ ] **Failure mode** — at least one “what goes wrong” bullet or table row on operator/contributor leaves
- [ ] **Example corpus link** — when a fixture exists under [meta/examples/](examples/README.md), cite it from `## Examples`
- [ ] **Worked-config link** — when a multi-file walkthrough belongs under [16-configuration-examples](../16-configuration-examples/README.md), prefer linking that leaf over inventing a second full tree
- [ ] **`last-checked: YYYY-MM`** frontmatter on high-churn leaves (experimental, implementations, adjacent tools, deploy/mesh)
- [ ] **Inbound links** — high-traffic leaves appear from cheatsheet, FAQ, or glossary where relevant

## Mesh / inter-trust extras (Phase M)

- [ ] Distinguish daemon `trusted-users` from multi-machine inter-trust
- [ ] Do not conflate Colmena/Digga “hive” with network mesh / Clan
- [ ] Link the six axes when relevant: reachability, build, binary, deploy, secret, supply-chain

## After edit

- [ ] Update [todo-coverage.md](todo-coverage.md) complete-pass checklist for that leaf
- [ ] Add new recurring canonical URLs to [sources.md](sources.md)
