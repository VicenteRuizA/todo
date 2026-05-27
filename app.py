from flask import Flask, jsonify, request, render_template
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'tasks.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                quadrant   INTEGER NOT NULL CHECK(quadrant IN (1,2,3,4)),
                category   TEXT    DEFAULT 'personal',
                completed  INTEGER DEFAULT 0,
                created_at TEXT    DEFAULT (datetime('now')),
                due_date   TEXT    DEFAULT NULL
            )
        ''')
        try:
            conn.execute('ALTER TABLE tasks ADD COLUMN due_date TEXT DEFAULT NULL')
        except sqlite3.OperationalError:
            pass  # Column already exists in older DB
        try:
            conn.execute('ALTER TABLE tasks ADD COLUMN position INTEGER DEFAULT NULL')
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.execute('UPDATE tasks SET position = id WHERE position IS NULL')
        conn.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    with get_db() as conn:
        tasks = conn.execute(
            'SELECT * FROM tasks ORDER BY completed ASC, position ASC, created_at DESC'
        ).fetchall()
    return jsonify([dict(t) for t in tasks])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = (data.get('title') or '').strip()
    quadrant = int(data.get('quadrant', 1))
    category = data.get('category', 'personal')
    due_date = data.get('due_date') or None
    if not title or quadrant not in (1, 2, 3, 4):
        return jsonify({'error': 'Invalid input'}), 400
    with get_db() as conn:
        max_pos = conn.execute(
            'SELECT MAX(position) FROM tasks WHERE quadrant = ?', (quadrant,)
        ).fetchone()[0]
        position = (max_pos or 0) + 1
        cur = conn.execute(
            'INSERT INTO tasks (title, quadrant, category, due_date, position) VALUES (?, ?, ?, ?, ?)',
            (title, quadrant, category, due_date, position)
        )
        conn.commit()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (cur.lastrowid,)).fetchone()
    return jsonify(dict(task)), 201


@app.route('/api/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    data = request.get_json()
    fields, values = [], []
    if 'title' in data:
        t = (data['title'] or '').strip()
        if not t:
            return jsonify({'error': 'Title cannot be empty'}), 400
        fields.append('title = ?')
        values.append(t)
    if 'completed' in data:
        fields.append('completed = ?')
        values.append(1 if data['completed'] else 0)
    if 'quadrant' in data:
        q = int(data['quadrant'])
        if q not in (1, 2, 3, 4):
            return jsonify({'error': 'Invalid quadrant'}), 400
        fields.append('quadrant = ?')
        values.append(q)
    if 'due_date' in data:
        fields.append('due_date = ?')
        values.append(data['due_date'] or None)
    if 'position' in data:
        fields.append('position = ?')
        values.append(int(data['position']))
    if not fields:
        return jsonify({'error': 'Nothing to update'}), 400
    values.append(task_id)
    with get_db() as conn:
        conn.execute(f'UPDATE tasks SET {", ".join(fields)} WHERE id = ?', values)
        conn.commit()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(task))


@app.route('/api/tasks/reorder', methods=['POST'])
def reorder_tasks():
    data = request.get_json()
    id_a, id_b = int(data['id_a']), int(data['id_b'])
    with get_db() as conn:
        pos_a = conn.execute('SELECT position FROM tasks WHERE id = ?', (id_a,)).fetchone()
        pos_b = conn.execute('SELECT position FROM tasks WHERE id = ?', (id_b,)).fetchone()
        if not pos_a or not pos_b:
            return jsonify({'error': 'Not found'}), 404
        conn.execute('UPDATE tasks SET position = ? WHERE id = ?', (pos_b['position'], id_a))
        conn.execute('UPDATE tasks SET position = ? WHERE id = ?', (pos_a['position'], id_b))
        conn.commit()
    return '', 204


@app.route('/api/tasks', methods=['DELETE'])
def delete_all_tasks():
    with get_db() as conn:
        conn.execute('DELETE FROM tasks')
        conn.commit()
    return '', 204


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    with get_db() as conn:
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
    return '', 204


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
