## Summary

<!-- What changed and why (1–3 sentences). Cite upstream sources if facts changed. -->

## Scope

<!-- One leaf, a small related cluster, or meta/tooling only. -->

- [ ] Single leaf or tight cluster (not a wide unrelated sweep)
- [ ] Relative `.md` link targets verified

## Checks

- [ ] `node meta/audit/broken-links.mjs` (from repo root)
- [ ] `node meta/audit/quality-audit.mjs`
- [ ] `node meta/examples/validate.mjs` (if `meta/examples/` changed and Nix available)

## Meta updates (if applicable)

- [ ] [meta/sources.md](../meta/sources.md) — new recurring canonical URLs
- [ ] [meta/todo-coverage.md](../meta/todo-coverage.md) — coverage checkbox or remaining-work note
- [ ] Frontmatter `status` set appropriately (`draft` / `complete` per [quality checklist](../meta/quality-checklist.md))

## Preview (optional)

<!-- If you ran `mkdocs serve`, note anything worth a reviewer glance. -->
