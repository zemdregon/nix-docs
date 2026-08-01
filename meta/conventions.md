---
status: active
---

# Conventions

Rules for growing this wiki. Subject articles stay stubs until a dedicated content pass.

## Layout

- Top-level dirs are **domains**, numbered for reading order (`00-` … `16-`).
- Cross-cutting material sits at the root: `glossary.md`, `comparisons/`, `cheatsheets/`, `meta/`.
- Each leaf topic is one `.md` file. Related topics share a folder with a short `README.md`.
- `16-configuration-examples/` holds **worked, multi-file config walkthroughs** that compose teaching pages from `00`–`15`. Tiny parseable `.nix` fixtures stay under [examples/](examples/README.md)—do not duplicate that corpus as a second fixture tree.

## Stub style

Every unfinished topic file should look like:

```markdown
---
status: stub
---

# Title

## Overview

## Details

## Examples

## References
```

- Frontmatter `status: stub` until real prose exists; then use `status: draft` or `status: complete`.
- Folder `README.md` files are **indexes**, not articles: use `status: index` (not `stub`/`draft`/`complete`). One-line purpose plus a **Contents** list of children (title + one-line purpose). No deep teaching in READMEs.
- Optional `## See also` with relative links only.
- Empty outline headings are fine; do not invent tutorial body in the structure phase.
- Allowed `status` values: `stub`, `draft`, `complete`, `index`, `active` (meta/plan docs), `superseded` (retired plans).

## Naming

- Prefer kebab-case filenames: `fixed-output-derivation.md`.
- Match CLI or option names when the file is about a specific tool: `nix-env.md`, `mkIf-mkMerge-mkOrder.md`.
- Keep concept docs (`02-concepts/flake.md`) separate from deep dives (`07-flakes/`).

## Linking

- Use relative Markdown links between sibling and cousin topics (path includes `.md`). Do **not** use `[[wikilinks]]`.
- Always include the `.md` extension in wiki targets. Link a folder via its `README.md`, not a bare directory URL.
- Avoid absolute URLs in stubs; add them in the content phase and record canonical sources in [sources.md](sources.md).
- Prefer linking to a domain `README.md` when pointing at a whole area.
- Several notes share basenames (`README.md`, two `nix-darwin.md` files). Relative paths keep links unambiguous on Git forges and the published site.

## Publishing

- GitHub Pages via MkDocs Material: root [mkdocs.yml](../mkdocs.yml), deps [requirements-docs.txt](../requirements-docs.txt), stage script [prepare-docs-dir.sh](prepare-docs-dir.sh), notes [site.md](site.md).
- Keep writing in plain Markdown with relative `.md` links; do not structure articles for a theme.
- Do not vendor a second copy of the tree under `docs/`.

## What does not belong

- Scraped or mirrored upstream manuals.
- Extra site generators alongside MkDocs (unless replacing it deliberately).
- Long explanatory prose invented without a research pack (fill stubs in dedicated passes).

## Research and coverage

- Filling stubs: follow [research-method.md](research-method.md) (pack → write → verify).
- Track gaps and week order in [todo-coverage.md](todo-coverage.md).
- Cite upstream from [sources.md](sources.md).
