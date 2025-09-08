import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sponsors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            companyName TEXT NOT NULL,
            gstNumber TEXT NOT NULL,
            annualTurnover INTEGER NOT NULL,
            taxRegistration BLOB NOT NULL,
            studentPercentage TEXT,
            studentGender TEXT,
            location TEXT,
            financialCondition TEXT,
            physicalDisability TEXT
        )
    ''')

    conn.commit()
    conn.close()


@app.route('/sponsor_profile/<int:sponsor_id>', methods=['GET'])
def get_sponsor_profile(sponsor_id):
    conn = get_db_connection()
    sponsor = conn.execute('SELECT * FROM sponsors WHERE id = ?', (sponsor_id,)).fetchone()
    conn.close()
    if sponsor is None:
        return jsonify({'message': 'Sponsor not found'}), 404
    data = {key: sponsor[key] for key in sponsor.keys() if key != 'taxRegistration'}
    return jsonify(data)


@app.route('/sponsor_profile/<int:sponsor_id>', methods=['POST'])
def update_sponsor_profile(sponsor_id):
    if 'taxRegistration' not in request.files:
        return jsonify({'message': 'Tax Registration PDF is required'}), 400
    tax_file = request.files['taxRegistration']
    if tax_file.filename == '' or tax_file.content_type != 'application/pdf':
        return jsonify({'message': 'Valid PDF required'}), 400

    name = request.form.get('name')
    companyName = request.form.get('companyName')
    gstNumber = request.form.get('gstNumber')
    annualTurnover = request.form.get('annualTurnover')

    if not all([name, companyName, gstNumber, annualTurnover]):
        return jsonify({'message': 'All fields are required'}), 400

    tax_data = tax_file.read()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM sponsors WHERE id = ?', (sponsor_id,))
    if cursor.fetchone():
        cursor.execute('''
            UPDATE sponsors SET
            name = ?, companyName = ?, gstNumber = ?, annualTurnover = ?, taxRegistration = ?
            WHERE id = ?
        ''', (name, companyName, gstNumber, annualTurnover, tax_data, sponsor_id))
    else:
        cursor.execute('''
            INSERT INTO sponsors (id, name, companyName, gstNumber, annualTurnover, taxRegistration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sponsor_id, name, companyName, gstNumber, annualTurnover, tax_data))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Sponsor profile updated successfully!'})


if __name__ == '__main__':
    init_db()
    print("Database initialized and tables created.")
    app.run(debug=True)
import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lastClassPercentage REAL NOT NULL,
            gender TEXT NOT NULL,
            location TEXT NOT NULL,
            financialCondition TEXT NOT NULL,
            physicalDisability TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/student_profile/<int:student_id>', methods=['GET'])
def get_student_profile(student_id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    if student is None:
        return jsonify({'message': 'Student not found'}), 404
    data = {key: student[key] for key in student.keys()}
    return jsonify(data)

@app.route('/student_profile/<int:student_id>', methods=['POST'])
def update_student_profile(student_id):
    # Using form data here for easy integration
    name = request.form.get('name')
    lastClassPercentage = request.form.get('lastClassPercentage')
    gender = request.form.get('gender')
    location = request.form.get('location')
    financialCondition = request.form.get('financialCondition')
    physicalDisability = request.form.get('physicalDisability')

    if not all([name, lastClassPercentage, gender, location, financialCondition, physicalDisability]):
        return jsonify({'message': 'All fields are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM students WHERE id = ?', (student_id,))
    if cursor.fetchone():
        cursor.execute('''
            UPDATE students SET name=?, lastClassPercentage=?, gender=?, location=?, financialCondition=?, physicalDisability=?
            WHERE id=?
        ''', (name, lastClassPercentage, gender, location, financialCondition, physicalDisability, student_id))
    else:
        cursor.execute('''
            INSERT INTO students (id, name, lastClassPercentage, gender, location, financialCondition, physicalDisability)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, lastClassPercentage, gender, location, financialCondition, physicalDisability))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Student profile saved successfully'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lastClassPercentage REAL NOT NULL,
            gender TEXT NOT NULL,
            location TEXT NOT NULL,
            financialCondition TEXT NOT NULL,
            physicalDisability TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/student_profile/<int:student_id>', methods=['GET'])
def get_student_profile(student_id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    if student is None:
        return jsonify({'message': 'Student not found'}), 404
    data = {key: student[key] for key in student.keys()}
    return jsonify(data)

@app.route('/student_profile/<int:student_id>', methods=['POST'])
def update_student_profile(student_id):
    # Using form data here for easy integration
    name = request.form.get('name')
    lastClassPercentage = request.form.get('lastClassPercentage')
    gender = request.form.get('gender')
    location = request.form.get('location')
    financialCondition = request.form.get('financialCondition')
    physicalDisability = request.form.get('physicalDisability')

    if not all([name, lastClassPercentage, gender, location, financialCondition, physicalDisability]):
        return jsonify({'message': 'All fields are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM students WHERE id = ?', (student_id,))
    if cursor.fetchone():
        cursor.execute('''
            UPDATE students SET name=?, lastClassPercentage=?, gender=?, location=?, financialCondition=?, physicalDisability=?
            WHERE id=?
        ''', (name, lastClassPercentage, gender, location, financialCondition, physicalDisability, student_id))
    else:
        cursor.execute('''
            INSERT INTO students (id, name, lastClassPercentage, gender, location, financialCondition, physicalDisability)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, lastClassPercentage, gender, location, financialCondition, physicalDisability))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Student profile saved successfully'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

