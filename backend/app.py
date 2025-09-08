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
import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create sponsors table to store submitted sponsor details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sponsors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            companyName TEXT NOT NULL,
            gstNumber TEXT NOT NULL,
            studentPercentage TEXT NOT NULL,
            studentGender TEXT NOT NULL,
            location TEXT NOT NULL,
            financialCondition TEXT NOT NULL,
            physicalDisability TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/submit_sponsor_details', methods=['POST'])
def submit_sponsor_details():
    data = request.json
    required_fields = ['companyName', 'gstNumber', 'studentPercentage', 'studentGender',
                       'location', 'financialCondition', 'physicalDisability']

    # Basic validation
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'message': f'Missing or empty field: {field}'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO sponsors 
            (companyName, gstNumber, studentPercentage, studentGender, location, financialCondition, physicalDisability)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['companyName'],
            data['gstNumber'],
            data['studentPercentage'],
            data['studentGender'],
            data['location'],
            data['financialCondition'],
            data['physicalDisability']
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'message': 'Failed to save data', 'error': str(e)}), 500

    conn.close()
    return jsonify({'message': 'Sponsor details saved successfully'}), 201

if __name__ == '__main__':
    init_db()
    print("Sponsor details table created or already exists.")
    app.run(debug=True)
