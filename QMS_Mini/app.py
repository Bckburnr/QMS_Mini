from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'qmsmini.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'Open',
                is_deleted INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id INTEGER,
                action TEXT,
                timestamp TEXT,
                details TEXT,
                FOREIGN KEY(issue_id) REFERENCES issues(id)
            )
        ''')

@app.route('/')
def index():
    with get_db() as conn:
        issues = conn.execute('SELECT * FROM issues WHERE is_deleted=0').fetchall()
    return render_template('index.html', issues=issues)

@app.route('/issue/new', methods=['GET', 'POST'])
def issue_new():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO issues (title, description, status) VALUES (?, ?, ?)',
                        (title, description, status))
            issue_id = cur.lastrowid
            conn.execute('INSERT INTO audit_log (issue_id, action, timestamp, details) VALUES (?, ?, ?, ?)',
                         (issue_id, 'Created', datetime.now(), f'Title: {title}, Status: {status}'))
            flash('Issue created!', 'success')
        return redirect(url_for('index'))
    return render_template('issue_form.html', issue=None)

@app.route('/issue/<int:issue_id>')
def issue_detail(issue_id):
    with get_db() as conn:
        issue = conn.execute('SELECT * FROM issues WHERE id=?', (issue_id,)).fetchone()
        audit = conn.execute('SELECT * FROM audit_log WHERE issue_id=? ORDER BY timestamp DESC', (issue_id,)).fetchall()
    return render_template('issue_detail.html', issue=issue, audit=audit)

@app.route('/issue/<int:issue_id>/edit', methods=['GET', 'POST'])
def issue_edit(issue_id):
    with get_db() as conn:
        issue = conn.execute('SELECT * FROM issues WHERE id=?', (issue_id,)).fetchone()
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            status = request.form['status']
            conn.execute('UPDATE issues SET title=?, description=?, status=? WHERE id=?',
                         (title, description, status, issue_id))
            conn.execute('INSERT INTO audit_log (issue_id, action, timestamp, details) VALUES (?, ?, ?, ?)',
                         (issue_id, 'Updated', datetime.now(), f'New Status: {status}'))
            flash('Issue updated!', 'success')
            return redirect(url_for('issue_detail', issue_id=issue_id))
    return render_template('issue_form.html', issue=issue)

@app.route('/issue/<int:issue_id>/close', methods=['POST'])
def issue_close(issue_id):
    with get_db() as conn:
        conn.execute('UPDATE issues SET status="Closed" WHERE id=?', (issue_id,))
        conn.execute('INSERT INTO audit_log (issue_id, action, timestamp, details) VALUES (?, ?, ?, ?)',
                     (issue_id, 'Closed', datetime.now(), 'Issue closed'))
    flash('Issue closed.', 'info')
    return redirect(url_for('issue_detail', issue_id=issue_id))

@app.route('/issue/<int:issue_id>/delete', methods=['POST'])
def issue_delete(issue_id):
    with get_db() as conn:
        conn.execute('UPDATE issues SET is_deleted=1 WHERE id=?', (issue_id,))
        conn.execute('INSERT INTO audit_log (issue_id, action, timestamp, details) VALUES (?, ?, ?, ?)',
                     (issue_id, 'Deleted', datetime.now(), 'Issue soft-deleted'))
    flash('Issue deleted (soft delete).', 'warning')
    return redirect(url_for('index'))

@app.route('/audit')
def audit_log():
    with get_db() as conn:
        logs = conn.execute('SELECT * FROM audit_log ORDER BY timestamp DESC').fetchall()
    return render_template('audit_log.html', logs=logs)

# ----- DB INIT ALWAYS -----
init_db()
# --------------------------

if __name__ == '__main__':
    app.run(debug=True)
