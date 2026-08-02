# Contributing to Nix Docs

Thank you for helping improve this wiki. This file is about **this repository** — layout, research, quality, and pull requests.

If you want to learn how to contribute to **Nixpkgs or NixOS upstream**, start with the [Contributor roadmap](00-roadmap/contributor.md) and [nixpkgs contribution](06-nixpkgs/contribution/README.md) pages instead.

**Published site:** [https://zemdregon.github.io/nix-docs/](https://zemdregon.github.io/nix-docs/) — build notes in [meta/site.md](meta/site.md).

## What belongs here

Nix Docs is a plain-Markdown knowledge base: synthesized articles with relative wiki links and upstream references. It is **not** a mirror of the Nix, Nixpkgs, or NixOS manuals.

Good contributions:

- Fix factual errors, stale version stamps, or broken links
- Deepen an existing leaf (examples, failure modes, cross-links)
- Fill a gap called out in [meta/todo-coverage.md](meta/todo-coverage.md) **Remaining work**
- Add or update `.nix` fixtures under [meta/examples/](meta/examples/README.md) when they support an article
- Refresh high-churn topics per [meta/release-checklist.md](meta/release-checklist.md)

Avoid:

- Pasting or vendoring upstream manuals
- Inventing options, CLI flags, or APIs
- Large unrelated edits across many domains in one PR
- New top-level campaign plan files (`*PLAN.md`); track work in [meta/todo-coverage.md](meta/todo-coverage.md)

## Before you write

1. Read [meta/conventions.md](meta/conventions.md) — layout, naming, linking, frontmatter.
2. Skim [meta/research-method.md](meta/research-method.md) — the pack → write → verify loop.
3. Pick a scoped target (one leaf, or a small related set). Check [meta/todo-coverage.md](meta/todo-coverage.md) for open work.
4. Build a **research pack** before drafting:
   - 3–8 factual bullets (what / why / main behaviors)
   - 1–3 canonical URLs from [meta/sources.md](meta/sources.md) or official manuals
   - Optional: a minimal example outline or a public config used only as a **pattern** (strip secrets)
5. Verify relative link targets exist in this tree before opening a PR.

**Source priority:** Nix / Nixpkgs / NixOS manuals and RFCs → project first-party docs → source when docs lag → public configs for patterns only. Confirm Discourse or issue anecdotes against primary sources before stating them as fact.

## Article shape

- **One topic = one `.md` file** in the numbered domain folders (`00-` … `16-`).
- Folder `README.md` files are **indexes** (`status: index`): one-line purpose + **Contents** list — not full tutorials.
- Use existing headings where present: `Overview`, `Details`, `Examples`, `References`. Add `## See also` with **relative** `.md` links when useful.
- **Linking:** always include the `.md` extension; no `[[wikilinks]]`. Link folders via their `README.md`.
- **Filenames:** kebab-case (`fixed-output-derivation.md`). Keep concept pages (`02-concepts/…`) separate from deep dives (`07-flakes/…`, etc.).

### Status lifecycle

Set YAML frontmatter `status` on every article:

| Status | Meaning |
|--------|---------|
| `stub` | Outline only; no real prose yet |
| `draft` | Accurate overview + main details; references present |
| `complete` | Passed [meta/quality-checklist.md](meta/quality-checklist.md) |
| `index` | Folder README (navigation only) |

**Draft bar:** accurate Overview + Details; ≥1 wiki-relative link; ≥1 upstream Reference.

**Complete bar:** verified minimal example (or explicit note why not); no invented APIs; experimental/unstable behavior version-stamped; tone concise and neutral (see gold pages like [01-philosophy/why-nix.md](01-philosophy/why-nix.md)).

Use optional `last-checked: YYYY-MM` on high-churn leaves (experimental features, implementations, deploy tools).

## Local checks

From the repo root (Node 20+):

```bash
node meta/audit/broken-links.mjs
node meta/audit/quality-audit.mjs
```

CI runs both on every pull request ([`.github/workflows/docs-audit.yml`](.github/workflows/docs-audit.yml)).

If you change files under [meta/examples/](meta/examples/README.md) and have Nix with flakes enabled:

```bash
node meta/examples/validate.mjs
```

### Preview the site

```bash
bash meta/prepare-docs-dir.sh
pip install -r requirements-docs.txt
mkdocs serve    # http://127.0.0.1:8000
```

Do not commit generated `docs/` or `site/` directories.

## Pull requests

1. **Scope small** — one leaf or a tight cluster (e.g. one domain README + its new child).
2. **Describe the why** — what gap or error you address; cite upstream sources in the PR text when facts changed.
3. **Run local audits** before pushing.
4. **Update meta when appropriate:**
   - New recurring canonical URLs → [meta/sources.md](meta/sources.md)
   - Finished or started coverage items → [meta/todo-coverage.md](meta/todo-coverage.md)
5. **Frontmatter** — set `status: draft` for new substantive leaves; only use `complete` after the quality checklist.

We do not require a particular commit message format; clear, complete sentences are enough.

By contributing, you agree that your contributions are licensed under the [CC BY 4.0](LICENSE) license. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## For AI-assisted edits

[AGENTS.md](AGENTS.md) is maintainer guidance for automated agents (research packs, subagent patterns, definition of done). Human contributors can ignore it unless you are driving an agent in this repo.

## See also

- [README.md](README.md) — domain map and navigation
- [meta/README.md](meta/README.md) — index of conventions, coverage, and tooling
- [meta/conventions.md](meta/conventions.md) — layout and linking rules
- [meta/research-method.md](meta/research-method.md) — research loop
- [meta/quality-checklist.md](meta/quality-checklist.md) — complete-pass rubric
- [meta/release-checklist.md](meta/release-checklist.md) — freshness cadence after Nix/NixOS releases
- [00-roadmap/contributor.md](00-roadmap/contributor.md) — learning path for upstream Nix contribution (not this repo)
