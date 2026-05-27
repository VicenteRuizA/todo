# Focus Board

Eisenhower Matrix task manager — a local web app built with Python and Flask.

## Setup

**Requirements:** Python 3.8+

```bash
git clone <repo-url>
cd todo
pip3 install -r requirements.txt
```

## Run

**Background (recommended):**
```bash
python3 cli.py start   # starts server, prints PID
python3 cli.py stop    # stops server
```

**Foreground:**
```bash
python3 app.py         # Ctrl+C to stop
```

Then open **http://127.0.0.1:5000** in your browser.

The database (`tasks.db`) is created automatically on first run — no setup needed.

## CLI

```bash
python3 cli.py export              # export tasks to Markdown
python3 cli.py export my-tasks.md  # export to specific file
python3 cli.py import my-tasks.md  # import tasks from Markdown
python3 cli.py import my-tasks.md --replace  # replace all existing tasks
```
