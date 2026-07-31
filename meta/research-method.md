---
status: active
---

# Research method

Repeatable loop for filling stubs and complete passes. Matches [EXPAND-PLAN.md](../EXPAND-PLAN.md) and [AGENTS.md](../AGENTS.md). Historical draft weeks: [ATTACK-PLAN.md](../ATTACK-PLAN.md).

## Loop

1. **Pick** — next item from [todo-coverage.md](todo-coverage.md) **Remaining work** or the active phase in [EXPAND-PLAN.md](../EXPAND-PLAN.md) (not historical week lists; those are done).
2. **Research pack** (before writing) — collect into notes (chat or scratch):
   - 3–8 factual bullets (what / why / main behaviors)
   - 1–3 canonical URLs from [sources.md](sources.md) or manuals found via that list
   - Optional: one real-world config link or a tiny invented example outline
3. **Write** — fill or deepen existing headings (`Overview`, `Details`, `Examples`, `References`). Folder `README.md` files stay index-only.
4. **Link** — relative paths to cousin wiki pages; verify targets exist (see coverage [Audit hook](todo-coverage.md#audit-hook)).
5. **Status** — new leaves: frontmatter `status: draft`; deepen passes keep or reaffirm `complete` only after [quality-checklist.md](quality-checklist.md).
6. **Verify** — mentally or in a throwaway flake/REPL; version-stamp unstable flags; update coverage checkboxes.
7. **Meta** — add new recurring canonical URLs to [sources.md](sources.md).

```mermaid
flowchart LR
  pick[Pick remaining work]
  pack[Research pack]
  write[Write draft]
  verify[Verify]
  meta[Update coverage and sources]
  pick --> pack --> write --> verify --> meta
```

## Research pack template

```text
Topic: path/to/page.md
Facts:
- …
Canonical:
- https://…
Optional example / config:
- …
Wiki links to add:
- ../02-concepts/….md
```

## Source priority

1. Nix / Nixpkgs / NixOS manuals and RFCs ([sources.md](sources.md))
2. Project first-party docs (Home Manager, Lix, flake-parts, …)
3. Code when docs lag (`nixpkgs` modules, Nix/`nix.conf` feature lists)
4. Public configs for **patterns** only (minimal snippets; strip secrets)
5. Discourse / issues for FAQ angles — confirm behavior in (1)–(3) before stating as fact

## Do not

- Paste upstream manuals wholesale
- Invent options, builtins, or CLI flags
- Mark `status: complete` from memory or blogs alone
- Scatter half-finished drafts across unrelated domains in one session

## Subagents

When parallelizing: one agent per leaf file; parent pastes the research pack into the prompt; child edits only that path and must include References + verified relative links.
