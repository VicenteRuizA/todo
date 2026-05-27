#!/usr/bin/env python3
"""Focus Board CLI — start/stop the server and export/import tasks."""

import argparse
import os
import re
import sqlite3
import subprocess
import sys
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'tasks.db')
PID_FILE = os.path.join(BASE_DIR, 'tasks.pid')

Q_LABELS = {
    1: 'Q1 · Do First — Urgent & Important',
    2: 'Q2 · Plan — Important, Not Urgent',
    3: 'Q3 · Delegate — Urgent, Not Important',
    4: 'Q4 · Eliminate — Not Urgent, Not Important',
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _pid_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


# ── start ──────────────────────────────────────────────────────────────────

def cmd_start(_args):
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        if _pid_running(pid):
            print(f'Server already running (PID {pid}) at http://127.0.0.1:5000')
            return
        os.remove(PID_FILE)  # stale PID

    kwargs = {}
    if sys.platform == 'win32':
        kwargs['creationflags'] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs['start_new_session'] = True

    proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, 'app.py')],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **kwargs,
    )
    with open(PID_FILE, 'w') as f:
        f.write(str(proc.pid))
    print(f'Server started (PID {proc.pid}) at http://127.0.0.1:5000')


# ── stop ───────────────────────────────────────────────────────────────────

def cmd_stop(_args):
    if not os.path.exists(PID_FILE):
        print('No PID file found — is the server running?')
        return
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    try:
        if sys.platform == 'win32':
            subprocess.run(
                ['taskkill', '/F', '/PID', str(pid)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
        print(f'Server stopped (PID {pid}).')
    except (OSError, subprocess.CalledProcessError):
        print(f'Process {pid} not found — already stopped?')
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


# ── export ─────────────────────────────────────────────────────────────────

def cmd_export(args):
    out = args.output or f'focus-board-{date.today().isoformat()}.md'
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM tasks ORDER BY completed ASC, position ASC, created_at DESC'
        ).fetchall()
    tasks = [dict(r) for r in rows]

    lines = ['# Focus Board']
    for q in range(1, 5):
        qt = sorted(
            [t for t in tasks if t['quadrant'] == q],
            key=lambda t: (t['position'] is None, t['position'] or 0),
        )
        lines.append(f'\n## {Q_LABELS[q]}')
        for t in qt:
            cb = '[x]' if t['completed'] else '[ ]'
            line = f"- {cb} {t['title']} | {t['category'] or 'personal'}"
            if t['due_date']:
                line += f" | due:{t['due_date']}"
            lines.append(line)

    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'Exported {len(tasks)} task(s) to {out}')


# ── import ─────────────────────────────────────────────────────────────────

def _parse_markdown(text):
    tasks, quadrant = [], 1
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r'^##\s+Q([1-4])', line, re.IGNORECASE)
        if m:
            quadrant = int(m.group(1))
            continue
        m = re.match(r'^- \[(x| )\] (.+)', line, re.IGNORECASE)
        if not m:
            continue
        completed = m.group(1).lower() == 'x'
        parts = [p.strip() for p in m.group(2).split('|')]
        title = parts[0]
        if not title:
            continue
        category, due_date = 'personal', None
        for part in parts[1:]:
            if part.startswith('due:'):
                due_date = part[4:].strip() or None
            elif part:
                category = part
        tasks.append({
            'title': title, 'quadrant': quadrant,
            'category': category, 'completed': completed, 'due_date': due_date,
        })
    return tasks


def cmd_import(args):
    with open(args.file, encoding='utf-8') as f:
        text = f.read()
    tasks = _parse_markdown(text)
    if not tasks:
        print('No tasks found in file.')
        return

    with get_db() as conn:
        if args.replace:
            conn.execute('DELETE FROM tasks')
            conn.commit()
        for t in tasks:
            max_pos = conn.execute(
                'SELECT MAX(position) FROM tasks WHERE quadrant = ?', (t['quadrant'],)
            ).fetchone()[0]
            position = (max_pos or 0) + 1
            conn.execute(
                'INSERT INTO tasks (title, quadrant, category, due_date, position, completed) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (t['title'], t['quadrant'], t['category'],
                 t['due_date'], position, 1 if t['completed'] else 0),
            )
        conn.commit()

    mode = 'replaced all tasks with' if args.replace else 'appended'
    print(f'Imported {len(tasks)} task(s) ({mode}) from {args.file}')


# ── entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog='python cli.py',
        description='Focus Board CLI',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('start', help='Start the Flask server in the background')
    sub.add_parser('stop', help='Stop the running Flask server')

    p_exp = sub.add_parser('export', help='Export all tasks to a Markdown file')
    p_exp.add_argument('output', nargs='?', metavar='FILE',
                       help='Output path (default: focus-board-YYYY-MM-DD.md)')

    p_imp = sub.add_parser('import', help='Import tasks from a Markdown file')
    p_imp.add_argument('file', metavar='FILE', help='Markdown file to import')
    p_imp.add_argument('--replace', action='store_true',
                       help='Delete all existing tasks before importing')

    args = parser.parse_args()
    {'start': cmd_start, 'stop': cmd_stop,
     'export': cmd_export, 'import': cmd_import}[args.command](args)


if __name__ == '__main__':
    main()
