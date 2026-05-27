# Mac Setup

## Prerequisites

- Python 3 (check with `python3 --version`; if missing, install via [brew](https://brew.sh): `brew install python3`)
- Git (comes with macOS Xcode tools; if prompted, install them)

---

## 1. Clone the repo

```bash
git clone git@github.com:VicenteRuizA/todo.git
cd todo
```

> If you haven't set up SSH on this Mac yet, use HTTPS instead:
> `git clone https://github.com/VicenteRuizA/todo.git`

---

## 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

---

## 3. Run

**Background (recommended):**
```bash
python3 cli.py start   # starts server, prints PID
python3 cli.py stop    # stops server
```

**Foreground (simpler):**
```bash
python3 app.py         # Ctrl+C to stop
```

Open **http://127.0.0.1:5000** in your browser.

The database (`tasks.db`) is created automatically on first run — nothing to configure.

---

## CLI commands

```bash
python3 cli.py export                        # export tasks to focus-board-YYYY-MM-DD.md
python3 cli.py export my-tasks.md            # export to a specific file
python3 cli.py import my-tasks.md            # import tasks (appends)
python3 cli.py import my-tasks.md --replace  # import tasks (replaces all)
```
