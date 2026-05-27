---
description: Markdown format spec for Focus Board task import files
---

# Focus Board Import Format

## File structure

```markdown
# Focus Board

## Q1 · Do First — Urgent & Important
- [ ] Task title | category | due:YYYY-MM-DD
- [x] Completed task | work

## Q2 · Plan — Important, Not Urgent
- [ ] Another task | personal

## Q3 · Delegate — Urgent, Not Important
- [ ] Delegated task | work | due:2026-06-01

## Q4 · Eliminate — Not Urgent, Not Important
- [ ] Low priority task | personal
```

## Task line format

```
- [checkbox] Title | category | due:YYYY-MM-DD
```

| Part | Required | Values |
|---|---|---|
| `[ ]` | yes | incomplete task |
| `[x]` or `[X]` | yes | completed task |
| `Title` | yes | any text, no pipes |
| `category` | no | any word (defaults to `personal`) |
| `due:YYYY-MM-DD` | no | e.g. `due:2026-05-30` |

Fields after the title are separated by `|` and can appear in any order as long as `due:` starts with `due:`.

## Quadrant headings

The heading sets which quadrant all tasks below it belong to until the next heading.

| Heading | Quadrant |
|---|---|
| `## Q1` | Do First — Urgent & Important |
| `## Q2` | Plan — Important, Not Urgent |
| `## Q3` | Delegate — Urgent, Not Important |
| `## Q4` | Eliminate — Not Urgent, Not Important |

Only `Q1`–`Q4` in the heading matters — the rest of the label text is ignored and can be anything or omitted entirely.

## Minimal valid examples

```markdown
## Q1
- [ ] Fix the login bug
- [x] Ship hotfix | work

## Q2
- [ ] Refactor auth module | work | due:2026-06-15
```

## Rules

- The `# Focus Board` title line is optional — the parser ignores it
- Blank lines and any line that isn't a `##` heading or `- [ ]` / `- [x]` task are silently skipped
- Task order in the file becomes task order in the quadrant after import
- If no quadrant heading appears before the first task, it defaults to Q1
- Titles must not contain `|` (it is used as the field separator)
- `due:` date must be `YYYY-MM-DD`; invalid formats are stored as-is and may not display correctly in the app
