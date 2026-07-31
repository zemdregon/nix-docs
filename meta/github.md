---
status: active
---

# GitHub-native viewing

This repo is a plain-Markdown knowledge base that renders directly on
[github.com](https://github.com/) — no site generator, no editor plugins, no
build step. Browse it in the GitHub web UI (or any Git forge) by clicking
through folders and links.

## How it renders on GitHub

- **Folder READMEs auto-render.** Opening any directory on GitHub shows its
  `README.md` below the file list, so each domain's index is the landing page
  for that folder.
- **Relative links are clickable.** Links use relative paths with a `.md`
  target (for example `[flake](../02-concepts/flake.md)`); GitHub resolves them
  to the rendered file, so navigation works page-to-page.
- **Frontmatter renders as a table.** The YAML block at the top of each note
  (`status: …`) is shown by GitHub as a small key/value table, so `status`
  stays visible without any plugin.
- **Tables, fenced code, and task lists** use GitHub-Flavored Markdown and
  render as-is.

## Authoring rules that keep GitHub happy

- Use **relative** Markdown links with a `.md` target (or a `#heading` anchor on
  the same page). Link a folder via its `README.md`, not a bare directory path.
- Do **not** use `[[wikilinks]]` — GitHub does not resolve them in repository
  Markdown. See [conventions.md](conventions.md).
- Duplicate basenames exist (`README.md` in every domain; two `nix-darwin.md`
  leaves). Relative paths disambiguate; shortest-name links do not.
- Put images/attachments under [attachments/](attachments/) and reference them
  with relative paths.
- Anchor slugs follow GitHub's rules (lowercase, spaces → `-`, punctuation
  stripped); check a `#heading` link against the target's actual headings.

## Local preview (optional)

GitHub itself is the reference renderer, so the simplest preview is to push a
branch and view it on github.com. To preview locally with GitHub styling and
working relative links, use [`grip`](https://github.com/joeyespo/grip) (renders
Markdown through GitHub's API):

```bash
pip install --break-system-packages grip
grip . 6419        # serve the repo at http://localhost:6419/
```

Open `http://localhost:6419/` and click through the same relative links you
would on GitHub. (Grip calls GitHub's API; unauthenticated use is rate-limited.)

## See also

- [conventions.md](conventions.md) — naming, stubs, cross-link rules
- [dashboard.md](dashboard.md) — browsing notes by `status`
- [Root README](../README.md)
