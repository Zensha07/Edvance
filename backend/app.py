import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Absolute path pointing to the database file in the same folder as app.py
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'sponsor'))
        )
    ''')
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    # TODO: Hash passwords before production use

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (email, password, role)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'message': 'Email already registered'}), 400
    conn.close()
    return jsonify({'message': 'User signed up successfully'})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'message': 'Login successful', 'role': user['role']})
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


if __name__ == '__main__':
    init_db()
    print("Database initialized and users table created.")
    app.run(debug=True)

