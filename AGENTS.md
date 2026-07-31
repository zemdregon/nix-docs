---
status: active
---

# AGENTS.md

Guidance for AI agents working in this repository.

## What this repo is

Plain-Markdown knowledge base for the full Nix stack (philosophy → language → store → nixpkgs → NixOS → flakes → experimental features → tooling → implementations). No site generator yet.

Expand plan (current): [EXPAND-PLAN.md](EXPAND-PLAN.md)  
Historical draft campaign pointer: [ATTACK-PLAN.md](ATTACK-PLAN.md)  
Conventions: [meta/conventions.md](meta/conventions.md)  
Sources: [meta/sources.md](meta/sources.md)  
Coverage: [meta/todo-coverage.md](meta/todo-coverage.md)  
Nav map: [README.md](README.md)

## Before you write

1. Read [meta/conventions.md](meta/conventions.md) and the relevant section of [EXPAND-PLAN.md](EXPAND-PLAN.md).
2. Prefer the priority tiers in the expand plan and [meta/todo-coverage.md](meta/todo-coverage.md) over random stubs.
3. Build a **research pack** before filling a page: 3–8 facts, 1–3 canonical URLs, optional real-world config link.
4. Verify relative link targets exist in this tree before linking.

## Research rules

- **Synthesize, don’t mirror** — never paste upstream manuals wholesale.
- **Primary over secondary** — Nix / Nixpkgs / NixOS manuals and RFCs beat blogs; use blogs only for examples or common pitfalls.
- Confirm behavior in manuals or source (`nixpkgs`, Nix/Lix) before stating facts.
- Version-stamp experimental features and unstable CLI flags.
- Real-world configs are for **patterns**; strip secrets; keep examples minimal (5–20 lines) or invent a tiny illustrative snippet.
- Do not treat Discord/forum lore as fact without manual/code confirmation.

## Writing rules

- One leaf topic = one `.md` file. Keep folder `README.md` as a short purpose + **Contents** list only (no deep teaching).
- Fill existing headings where present (`Overview`, `Details`, `Examples`, `References`). Add `## See also` with relative links when useful.
- Status lifecycle (YAML frontmatter): `stub` → `draft` → `complete` (see conventions for the quality bar).
- Use relative links between wiki pages. Put stable upstream URLs under `## References` and add new canonical sources to [meta/sources.md](meta/sources.md).
- Keep Markdown link syntax with `.md` targets (GitHub resolves relative `.md` paths — see [meta/github.md](meta/github.md)); do not introduce `[[wikilinks]]`.
- Keep concept pages (`02-concepts/…`) separate from deep dives (`07-flakes/…`, etc.).
- Be concise. No emojis. No marketing tone.

## Do not

- Scrape or vendor full upstream docs into this repo.
- Add MkDocs / mdBook / Hugo until the wiki is mostly draft (unless the user explicitly asks).
- Mark `complete` from memory or blogs alone.
- Invent Nix/NixOS APIs, options, or flags.
- Expand scope beyond the files you were asked to edit.
- Commit, push, or force-push unless the user explicitly asks.
- Edit [EXPAND-PLAN.md](EXPAND-PLAN.md), [ATTACK-PLAN.md](ATTACK-PLAN.md), or plan files in `.cursor/plans/` unless the user asks to update the plan.

## Subagent pattern

**Always use subagents** for leaf drafts and other bounded research/write work to keep the parent context lean. Prefer one subagent per leaf over filling many pages in the parent thread.

When parallelizing content fills:

- One subagent **per leaf file** (or one clearly named file).
- Prompt must say: edit **only** that path; verify links exist; set frontmatter `status: draft`; include References.
- Parent supplies the research pack (URLs + bullets) in the prompt so children don’t invent APIs.
- **When all subagents for a batch have returned, automatically run a full parent review**—do not wait to be asked. Skim the new drafts together, fix factual conflicts and broken relative links, align cross-links and tone, update [meta/todo-coverage.md](meta/todo-coverage.md) checkboxes, and add any new recurring canonical URLs to [meta/sources.md](meta/sources.md).

## Suggested session shapes

| User ask | Agent action |
|----------|----------------|
| “Do week 0 / bootstrap meta” | Fill concrete URLs in `meta/sources.md`; week-keyed checklist in `meta/todo-coverage.md`; add `meta/research-method.md` if missing |
| “Draft domain N” | Research pack → fill leaf stubs in that domain to `draft`; leave unrelated domains alone |
| “Complete pass on X” | Verify examples/refs; set `complete`; check off coverage |
| “One file: path” | Edit only that file |
| “Subagent per file in dir” | Launch one restricted agent per `.md` as above |

## Definition of done (article)

**Draft:** accurate Overview + main Details; ≥1 wiki-relative link; ≥1 upstream Reference; frontmatter `status: draft`.

**Complete:** verified minimal example (or version-noted); no uncited absolute claims; coverage TODO updated; frontmatter `status: complete`.

## Cursor Cloud specific instructions

This repo is a **plain-Markdown knowledge base viewed natively on GitHub** — there is no build system, package manager, automated test suite, or CI, and this is intentional (site generator deferred; see [meta/conventions.md](meta/conventions.md) "What does not belong yet"). Nothing needs installing to work here; Node 22 and Python 3.12 are preinstalled. GitHub is the reference renderer: folder `README.md` files auto-render as their directory's landing page, relative `.md` links are clickable, and YAML frontmatter shows as a table. See [meta/github.md](meta/github.md).

- **Lint/test (the real quality gate):** the tracked invariant is "0 broken relative `.md` links" (see [README.md](README.md)). Validate by confirming every inline Markdown link whose target ends in `.md` resolves to an existing file, and that every `.md` starts with `status:` frontmatter. A stdlib-only Python script (no dependencies) can scan all `.md` files for this; there is intentionally no committed checker.
  - Known false positives: the [glossary.md](glossary.md) uses bold-term pseudo-anchors like `#cppnix`/`#lix`/`#tvix`/`#snix` that are not real headings. A strict heading-anchor checker flags ~8 of these, but they are **not** broken relative `.md` links and must not be "fixed" (out of scope).
- **Build/run (preview):** there is no site generator; GitHub renders the repo natively, so the simplest preview is to push a branch and view it on github.com. For a local preview with GitHub styling and working relative links, use [`grip`](https://github.com/joeyespo/grip) (`pip install --break-system-packages grip`, then `grip . 6419`); it renders through GitHub's API (unauthenticated use is rate-limited). See [meta/github.md](meta/github.md). Do **not** commit a generator (MkDocs/mdBook/Hugo) or its config into the repo — see the "Do not" section above.
- **Authoring:** the core workflow is editing interlinked leaf `.md` files with relative links; after edits, re-run the relative-link check to keep the invariant at zero broken links.
