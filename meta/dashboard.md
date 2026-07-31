---
status: active
---

# Status dashboard

Every note carries a `status` in its YAML frontmatter (`stub` / `draft` /
`complete` for leaves, `index` for folder READMEs, `active` / `superseded` for
meta and plan docs — see [conventions.md](conventions.md)). GitHub renders that
frontmatter as a table at the top of each file, but it cannot run live queries,
so browse status with search instead of a Dataview view.

## Browse by status on GitHub

Use GitHub code search (the search box on the repo, or
[github.com/search](https://github.com/search)) scoped to this repo:

- Drafts: `status: draft path:*.md`
- Stubs: `status: stub path:*.md`
- Folder indexes: `status: index path:*.md`
- Anything not yet complete: search `status: draft` and `status: stub`.

## Browse by status locally

From a clone, [ripgrep](https://github.com/BurntSushi/ripgrep) gives the same
counts the old Dataview tables did:

```bash
# Count notes per status
rg -N '^status:' -g '*.md' | sed 's/.*status: *//' | sort | uniq -c | sort -rn

# List every leaf that is not complete yet
rg -l '^status: (stub|draft)$' -g '*.md'
```

The ground-truth checklist and last audit numbers live in
[todo-coverage.md](todo-coverage.md).

## See also

- [github.md](github.md) — how the wiki renders on GitHub
- [todo-coverage.md](todo-coverage.md) — campaign checklist / audit hook
- [conventions.md](conventions.md) — frontmatter `status` values
