from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
import hashlib
import secrets

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production
DATABASE = 'teacher_profiles.db'
STUDENT_DATABASE = 'student_profiles.db'

# Initialize DB and create table if not exists
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Teacher authentication table
    c.execute('''
        CREATE TABLE IF NOT EXISTS teacher_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Teacher profile table (now user-specific)
    c.execute('''
        CREATE TABLE IF NOT EXISTS teacher_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            qualification TEXT NOT NULL,
            teaching_where TEXT NOT NULL,
            since_when TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teacher_auth (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def init_student_db():
    conn = sqlite3.connect(STUDENT_DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personal_data TEXT NOT NULL,
            academic_data TEXT NOT NULL,
            residential_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_notes_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            standard TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teacher_auth (id)
        )
    ''')
    conn.commit()
    conn.close()

def init_videos_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            standard TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            video_type TEXT NOT NULL,
            file_path TEXT,
            video_url TEXT,
            file_name TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teacher_auth (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()
init_student_db()
init_notes_db()
init_videos_db()

# Authentication helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_current_teacher_id():
    return session.get('teacher_id')

# Authentication API endpoints
@app.route('/api/teacher/register', methods=['POST'])
def teacher_register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not all([email, password, name]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if email already exists
        c.execute('SELECT id FROM teacher_auth WHERE email = ?', (email,))
        if c.fetchone():
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create new teacher
        password_hash = hash_password(password)
        c.execute('''
            INSERT INTO teacher_auth (email, password_hash, name)
            VALUES (?, ?, ?)
        ''', (email, password_hash, name))
        
        teacher_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Teacher registered successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/teacher/login', methods=['POST'])
def teacher_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Find teacher by email
        c.execute('SELECT id, password_hash, name FROM teacher_auth WHERE email = ?', (email,))
        teacher = c.fetchone()
        
        if not teacher or not verify_password(password, teacher[1]):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        teacher_id, _, name = teacher
        
        # Set session
        session['teacher_id'] = teacher_id
        session['teacher_name'] = name
        session['teacher_email'] = email
        
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'teacher': {
                'id': teacher_id,
                'name': name,
                'email': email
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/teacher/logout', methods=['POST'])
def teacher_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/teacher/me', methods=['GET'])
def get_current_teacher():
    if 'teacher_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'teacher': {
            'id': session['teacher_id'],
            'name': session['teacher_name'],
            'email': session['teacher_email']
        }
    })

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
    if 'teacher_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT name, qualification, teaching_where, since_when FROM teacher_profile WHERE teacher_id = ? LIMIT 1', (session['teacher_id'],))
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

# Teacher Profile API (user-specific)
@app.route('/api/teacher/profile', methods=['GET'])
@require_auth
def get_teacher_profile():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT name, qualification, teaching_where, since_when FROM teacher_profile WHERE teacher_id = ? LIMIT 1', (get_current_teacher_id(),))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'profile': None})
    
    name, qualification, teaching_where, since_when = row
    return jsonify({
        'profile': {
            'name': name,
            'qualification': qualification,
            'teaching_where': teaching_where,
            'since_when': since_when
        }
    })

@app.route('/api/teacher/profile', methods=['POST'])
@require_auth
def save_teacher_profile():
    data = request.get_json()
    name = data.get('name')
    qualification = data.get('qualification')
    teaching_where = data.get('teaching_where')
    since_when = data.get('since_when')
    
    if not all([name, qualification, teaching_where, since_when]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Delete existing profile for this teacher
        c.execute('DELETE FROM teacher_profile WHERE teacher_id = ?', (get_current_teacher_id(),))
        
        # Insert new profile
        c.execute('''
            INSERT INTO teacher_profile (teacher_id, name, qualification, teaching_where, since_when)
            VALUES (?, ?, ?, ?, ?)
        ''', (get_current_teacher_id(), name, qualification, teaching_where, since_when))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Profile saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Student Profile API endpoints
@app.route('/api/student/profile', methods=['GET'])
def get_student_profile():
    conn = sqlite3.connect(STUDENT_DATABASE)
    c = conn.cursor()
    c.execute('SELECT personal_data, academic_data, residential_data FROM student_profile ORDER BY created_at DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'profile': None})
    
    personal_data = json.loads(row[0])
    academic_data = json.loads(row[1])
    residential_data = json.loads(row[2])
    
    return jsonify({
        'profile': {
            'personal': personal_data,
            'academic': academic_data,
            'residential': residential_data
        }
    })

@app.route('/api/student/profile', methods=['POST'])
def save_student_profile():
    data = request.get_json()
    
    if not data or not all(key in data for key in ['personal', 'academic', 'residential']):
        return jsonify({'success': False, 'message': 'Invalid data format'}), 400
    
    try:
        conn = sqlite3.connect(STUDENT_DATABASE)
        c = conn.cursor()
        
        # Delete existing data (for demo, only one profile stored)
        c.execute('DELETE FROM student_profile')
        
        # Insert new data
        c.execute('''
            INSERT INTO student_profile (personal_data, academic_data, residential_data)
            VALUES (?, ?, ?)
        ''', (
            json.dumps(data['personal']),
            json.dumps(data['academic']),
            json.dumps(data['residential'])
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Notes API endpoints
@app.route('/api/notes', methods=['GET'])
@require_auth
def get_notes():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, standard, subject, topic, file_name, uploaded_at FROM uploaded_notes WHERE teacher_id = ? ORDER BY uploaded_at DESC', (get_current_teacher_id(),))
    rows = c.fetchall()
    conn.close()
    
    notes = []
    for row in rows:
        notes.append({
            'id': row[0],
            'standard': row[1],
            'subject': row[2],
            'topic': row[3],
            'file_name': row[4],
            'uploaded_at': row[5]
        })
    
    return jsonify({'notes': notes})

@app.route('/api/notes', methods=['POST'])
@require_auth
def upload_notes():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Only PDF files are allowed'}), 400
    
    standard = request.form.get('standard')
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    
    if not all([standard, subject, topic]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        # Save file
        import os
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        filename = f"{int(datetime.now().timestamp())}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Save to database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO uploaded_notes (teacher_id, standard, subject, topic, file_path, file_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (get_current_teacher_id(), standard, subject, topic, file_path, file.filename))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Notes uploaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notes/<int:note_id>/download')
def download_note(note_id):
    import os
    from flask import send_file
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT file_path, file_name FROM uploaded_notes WHERE id = ?', (note_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': 'Note not found'}), 404
    
    file_path, file_name = row
    
    # Convert to absolute path
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.path.dirname(__file__), file_path)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=file_name,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'Error serving file: {str(e)}'}), 500

# Videos API endpoints
@app.route('/api/videos', methods=['GET'])
@require_auth
def get_videos():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, standard, subject, topic, video_type, file_path, video_url, file_name, uploaded_at FROM uploaded_videos WHERE teacher_id = ? ORDER BY uploaded_at DESC', (get_current_teacher_id(),))
    rows = c.fetchall()
    conn.close()
    
    videos = []
    for row in rows:
        videos.append({
            'id': row[0],
            'standard': row[1],
            'subject': row[2],
            'topic': row[3],
            'video_type': row[4],
            'file_path': row[5],
            'video_url': row[6],
            'file_name': row[7],
            'uploaded_at': row[8]
        })
    
    return jsonify({'videos': videos})

@app.route('/api/videos', methods=['POST'])
@require_auth
def upload_video():
    standard = request.form.get('standard')
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    video_type = request.form.get('video_type')  # 'file' or 'link'
    
    if not all([standard, subject, topic, video_type]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        if video_type == 'file':
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'}), 400
            
            if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm')):
                return jsonify({'success': False, 'message': 'Only video files are allowed'}), 400
            
            # Save file
            import os
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'videos')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            filename = f"{int(datetime.now().timestamp())}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Save to database
            c.execute('''
                INSERT INTO uploaded_videos (teacher_id, standard, subject, topic, video_type, file_path, file_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (get_current_teacher_id(), standard, subject, topic, video_type, file_path, file.filename))
            
        else:  # video_type == 'link'
            video_url = request.form.get('video_url')
            if not video_url:
                return jsonify({'success': False, 'message': 'Video URL is required'}), 400
            
            # Save to database
            c.execute('''
                INSERT INTO uploaded_videos (teacher_id, standard, subject, topic, video_type, video_url, file_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (get_current_teacher_id(), standard, subject, topic, video_type, video_url, 'External Video'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Video uploaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/videos/<int:video_id>/stream')
def stream_video(video_id):
    import os
    from flask import send_file
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT file_path, file_name, video_type FROM uploaded_videos WHERE id = ?', (video_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': 'Video not found'}), 404
    
    file_path, file_name, video_type = row
    
    if video_type != 'file':
        return jsonify({'error': 'This is not a file video'}), 400
    
    # Convert to absolute path
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.path.dirname(__file__), file_path)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    try:
        return send_file(file_path, mimetype='video/mp4')
    except Exception as e:
        return jsonify({'error': f'Error streaming video: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
