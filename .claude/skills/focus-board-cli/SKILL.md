---
description: Run Focus Board CLI commands to start/stop the server and export/import tasks as Markdown
---

# Focus Board CLI

All commands run from `C:\Users\vicen\Dev\todo\` using `python cli.py <command>`.

## Start the server

```powershell
python cli.py start
```

Launches Flask in the background and writes a `tasks.pid` file to track the process.
Open http://127.0.0.1:5000 in a browser.

If already running, reports the existing PID instead of launching a second instance.

## Stop the server

```powershell
python cli.py stop
```

Reads `tasks.pid`, kills the process, and removes the file.
Safe to run if the server crashed — cleans up the stale PID file automatically.

## Export tasks to Markdown

```powershell
# Default filename: focus-board-YYYY-MM-DD.md
python cli.py export

# Custom filename
python cli.py export backup.md
python cli.py export "C:\Users\vicen\Documents\tasks.md"
```

Writes all tasks grouped by quadrant. The server does not need to be running.

Output format:

```markdown
# Focus Board

## Q1 · Do First — Urgent & Important
- [ ] Fix critical bug | work | due:2026-05-30
- [x] Deploy hotfix | work

## Q2 · Plan — Important, Not Urgent
- [ ] Write documentation | personal
```

Each task line: `- [x] Title | category | due:YYYY-MM-DD`
- `[x]` = completed, `[ ]` = incomplete
- `category` is always included
- `due:` field is omitted if no due date is set

## Import tasks from Markdown

```powershell
# Append imported tasks to existing ones
python cli.py import backup.md

# Wipe all tasks first, then import
python cli.py import backup.md --replace
```

The server does not need to be running. If the server is running while you import,
reload the browser page to see the changes.

Parse rules:
- `## Q1` / `## Q2` / `## Q3` / `## Q4` anywhere in a heading sets the current quadrant
- `- [ ] Title | category | due:YYYY-MM-DD` → new incomplete task
- `- [x] Title | category` → new completed task
- `category` defaults to `personal` if omitted
- `due:` field is optional
- All other lines (blank lines, `#` headings, freeform text) are ignored

## Typical workflows

**Daily backup:**
```powershell
python cli.py export
```

**Restore from backup:**
```powershell
python cli.py import focus-board-2026-05-25.md --replace
```

**Bulk-edit tasks outside the app:**
1. `python cli.py export tasks.md`
2. Edit `tasks.md` in any text editor — add, remove, or reorganise tasks
3. `python cli.py import tasks.md --replace`
4. Reload the browser

**Start fresh session:**
```powershell
python cli.py start
# ... work in browser ...
python cli.py stop
```
