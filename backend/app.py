from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'teacher_profiles.db'

# Initialize DB and create table if not exists
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS teacher_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            qualification TEXT NOT NULL,
            teaching_where TEXT NOT NULL,
            since_when TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        qualification = request.form.get('qualification')
        teaching_where = request.form.get('teachingWhere')
        since_when = request.form.get('sinceWhen')

        # Store in DB
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        # Assuming one profile, replace if exists
        c.execute('DELETE FROM teacher_profile')
        c.execute('''
            INSERT INTO teacher_profile (name, qualification, teaching_where, since_when)
            VALUES (?, ?, ?, ?)
        ''', (name, qualification, teaching_where, since_when))
        conn.commit()
        conn.close()

        return redirect(url_for('profile'))

    return render_template('form.html')


@app.route('/profile')
def profile():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT name, qualification, teaching_where, since_when FROM teacher_profile LIMIT 1')
    row = c.fetchone()
    conn.close()

    if not row:
        return redirect(url_for('index'))

    name, qualification, teaching_where, since_when = row
    # Format date for display
    try:
        since_when_formatted = datetime.strptime(since_when, '%Y-%m-%d').strftime('%B %d, %Y')
    except:
        since_when_formatted = since_when

    return render_template('profile.html', 
                           name=name, 
                           qualification=qualification,
                           teaching_where=teaching_where,
                           since_when=since_when_formatted)


if __name__ == '__main__':
    app.run(debug=True)
