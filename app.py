from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'notes_devops.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute(
        '''CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )'''
    )
    db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
        db.commit()
        return redirect(url_for('index'))
    notes = db.execute('SELECT * FROM notes ORDER BY id DESC').fetchall()
    return render_template('index.html', notes=notes)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete(note_id):
    db = get_db()
    db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000)
