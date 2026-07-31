---
status: active
---

# Vault dashboard

Dataview overview of wiki note `status` frontmatter. Open in Obsidian (Live Preview or Reading) after enabling the Dataview plugin.

## Counts by status

```dataview
TABLE length(rows) AS count
FROM ""
WHERE status
GROUP BY status
SORT length(rows) DESC
```

## Indexes (folder READMEs)

```dataview
LIST
FROM ""
WHERE status = "index"
SORT file.path ASC
```

## Draft / stub / active meta

```dataview
TABLE status, file.folder AS folder
FROM ""
WHERE status = "draft" OR status = "stub" OR status = "active" OR status = "superseded"
SORT status ASC, file.path ASC
```

## Leaves still not complete

```dataview
TABLE status, file.folder AS folder
FROM ""
WHERE status AND status != "complete" AND status != "index"
SORT status ASC, file.path ASC
```

## See also

- [obsidian.md](obsidian.md) — vault plugins and link settings
- [todo-coverage.md](todo-coverage.md) — campaign checklist / audit hook
- [conventions.md](conventions.md) — frontmatter `status` values
