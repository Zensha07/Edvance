from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DATABASE = 'teacher_profiles.db'
STUDENT_DATABASE = 'student_profiles.db'

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
            standard TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            standard TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            video_type TEXT NOT NULL,
            file_path TEXT,
            video_url TEXT,
            file_name TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_sponsor_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sponsor_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company_name TEXT NOT NULL,
            gst_number TEXT NOT NULL,
            annual_turnover REAL NOT NULL,
            tax_registration_file TEXT,
            tax_registration_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_scholarship_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sponsor_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'INR',
            gender_criteria TEXT,
            family_income_max REAL,
            location_type TEXT,
            min_academic_percentage REAL,
            application_deadline DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sponsor_id) REFERENCES sponsor_profiles (id)
        )
    ''')
    conn.commit()
    conn.close()

def init_scholarship_applications_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scholarship_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_id INTEGER NOT NULL,
            student_data TEXT NOT NULL,
            application_message TEXT,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            FOREIGN KEY (scholarship_id) REFERENCES scholarships (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()
init_student_db()
init_notes_db()
init_videos_db()
init_sponsor_db()
init_scholarship_db()
init_scholarship_applications_db()

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
def get_notes():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, standard, subject, topic, file_name, uploaded_at FROM uploaded_notes ORDER BY uploaded_at DESC')
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
            INSERT INTO uploaded_notes (standard, subject, topic, file_path, file_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (standard, subject, topic, file_path, file.filename))
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
def get_videos():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, standard, subject, topic, video_type, file_path, video_url, file_name, uploaded_at FROM uploaded_videos ORDER BY uploaded_at DESC')
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
                INSERT INTO uploaded_videos (standard, subject, topic, video_type, file_path, file_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (standard, subject, topic, video_type, file_path, file.filename))
            
        else:  # video_type == 'link'
            video_url = request.form.get('video_url')
            if not video_url:
                return jsonify({'success': False, 'message': 'Video URL is required'}), 400
            
            # Save to database
            c.execute('''
                INSERT INTO uploaded_videos (standard, subject, topic, video_type, video_url, file_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (standard, subject, topic, video_type, video_url, 'External Video'))
        
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

@app.route('/api/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    import os
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Get video details before deleting
        c.execute('SELECT file_path, video_type FROM uploaded_videos WHERE id = ?', (video_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'success': False, 'message': 'Video not found'}), 404
        
        file_path, video_type = row
        
        # Delete from database
        c.execute('DELETE FROM uploaded_videos WHERE id = ?', (video_id,))
        conn.commit()
        conn.close()
        
        # Delete physical file if it exists and is a file upload
        if video_type == 'file' and file_path:
            try:
                # Convert to absolute path
                if not os.path.isabs(file_path):
                    file_path = os.path.join(os.path.dirname(__file__), file_path)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not delete file {file_path}: {e}")
        
        return jsonify({'success': True, 'message': 'Video deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Study Materials API endpoints for students
@app.route('/api/study-materials', methods=['GET'])
def get_study_materials():
    standard = request.args.get('standard')
    subject = request.args.get('subject')
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Build query based on filters
        notes_query = 'SELECT id, standard, subject, topic, file_name, uploaded_at, "notes" as type FROM uploaded_notes'
        videos_query = 'SELECT id, standard, subject, topic, file_name, uploaded_at, video_type as type FROM uploaded_videos'
        
        notes_params = []
        videos_params = []
        
        if standard:
            notes_query += ' WHERE standard = ?'
            videos_query += ' WHERE standard = ?'
            notes_params.append(standard)
            videos_params.append(standard)
            
            if subject:
                notes_query += ' AND subject = ?'
                videos_query += ' AND subject = ?'
                notes_params.append(subject)
                videos_params.append(subject)
        elif subject:
            notes_query += ' WHERE subject = ?'
            videos_query += ' WHERE subject = ?'
            notes_params.append(subject)
            videos_params.append(subject)
        
        notes_query += ' ORDER BY uploaded_at DESC'
        videos_query += ' ORDER BY uploaded_at DESC'
        
        # Get notes
        c.execute(notes_query, notes_params)
        notes = c.fetchall()
        
        # Get videos
        c.execute(videos_query, videos_params)
        videos = c.fetchall()
        
        conn.close()
        
        # Combine and format results
        materials = []
        
        for note in notes:
            materials.append({
                'id': note[0],
                'standard': note[1],
                'subject': note[2],
                'topic': note[3],
                'file_name': note[4],
                'uploaded_at': note[5],
                'type': 'notes',
                'download_url': f'/api/notes/{note[0]}/download'
            })
        
        for video in videos:
            materials.append({
                'id': video[0],
                'standard': video[1],
                'subject': video[2],
                'topic': video[3],
                'file_name': video[4],
                'uploaded_at': video[5],
                'type': 'videos',
                'stream_url': f'/api/videos/{video[0]}/stream'
            })
        
        # Sort by upload date (newest first)
        materials.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        return jsonify({'materials': materials})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/study-materials/filters', methods=['GET'])
def get_study_filters():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Get unique standards and subjects
        c.execute('SELECT DISTINCT standard FROM uploaded_notes UNION SELECT DISTINCT standard FROM uploaded_videos ORDER BY standard')
        standards = [row[0] for row in c.fetchall()]
        
        c.execute('SELECT DISTINCT subject FROM uploaded_notes UNION SELECT DISTINCT subject FROM uploaded_videos ORDER BY subject')
        subjects = [row[0] for row in c.fetchall()]
        
        conn.close()
        
        return jsonify({
            'standards': standards,
            'subjects': subjects
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sponsor Profile API endpoints
@app.route('/api/sponsor/profile', methods=['GET', 'POST', 'PUT'])
def sponsor_profile():
    import os
    from werkzeug.utils import secure_filename
    
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('SELECT * FROM sponsor_profiles ORDER BY updated_at DESC LIMIT 1')
            row = c.fetchone()
            conn.close()
            
            if row:
                return jsonify({
                    'success': True,
                    'profile': {
                        'id': row[0],
                        'name': row[1],
                        'company_name': row[2],
                        'gst_number': row[3],
                        'annual_turnover': row[4],
                        'tax_registration_file': row[5],
                        'tax_registration_path': row[6],
                        'created_at': row[7],
                        'updated_at': row[8]
                    }
                })
            else:
                return jsonify({'success': True, 'profile': None})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method in ['POST', 'PUT']:
        try:
            # Get form data
            name = request.form.get('name')
            company_name = request.form.get('companyName')
            gst_number = request.form.get('gstNumber')
            annual_turnover = request.form.get('annualTurnover')
            
            # Validate required fields
            if not all([name, company_name, gst_number, annual_turnover]):
                return jsonify({'success': False, 'message': 'All fields are required'}), 400
            
            # Handle file upload
            tax_file = request.files.get('taxRegistration')
            tax_file_path = None
            tax_file_name = None
            
            if tax_file and tax_file.filename:
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'sponsors')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                filename = secure_filename(tax_file.filename)
                tax_file_path = os.path.join(upload_dir, filename)
                tax_file.save(tax_file_path)
                tax_file_name = filename
            
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            if request.method == 'POST':
                # Insert new profile
                c.execute('''
                    INSERT INTO sponsor_profiles 
                    (name, company_name, gst_number, annual_turnover, tax_registration_file, tax_registration_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, company_name, gst_number, annual_turnover, tax_file_name, tax_file_path))
            else:
                # Update existing profile
                c.execute('''
                    UPDATE sponsor_profiles SET 
                    name = ?, company_name = ?, gst_number = ?, annual_turnover = ?, 
                    tax_registration_file = ?, tax_registration_path = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = (SELECT id FROM sponsor_profiles ORDER BY updated_at DESC LIMIT 1)
                ''', (name, company_name, gst_number, annual_turnover, tax_file_name, tax_file_path))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Profile saved successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sponsor/tax-document/<int:profile_id>')
def download_tax_document(profile_id):
    import os
    from flask import send_file
    
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT tax_registration_path, tax_registration_file FROM sponsor_profiles WHERE id = ?', (profile_id,))
        row = c.fetchone()
        conn.close()
        
        if not row or not row[0]:
            return jsonify({'error': 'Document not found'}), 404
        
        file_path = row[0]
        file_name = row[1]
        
        # Convert to absolute path
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.path.dirname(__file__), file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=file_name, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Scholarship API endpoints
@app.route('/api/scholarships', methods=['GET', 'POST'])
def scholarships():
    if request.method == 'GET':
        # Get all active scholarships
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('''
                SELECT s.*, sp.name as sponsor_name, sp.company_name 
                FROM scholarships s 
                JOIN sponsor_profiles sp ON s.sponsor_id = sp.id 
                WHERE s.is_active = 1
                ORDER BY s.created_at DESC
            ''')
            scholarships = []
            for row in c.fetchall():
                scholarships.append({
                    'id': row[0],
                    'sponsor_id': row[1],
                    'title': row[2],
                    'description': row[3],
                    'amount': row[4],
                    'currency': row[5],
                    'gender_criteria': row[6],
                    'family_income_max': row[7],
                    'location_type': row[8],
                    'min_academic_percentage': row[9],
                    'application_deadline': row[10],
                    'is_active': row[11],
                    'created_at': row[12],
                    'updated_at': row[13],
                    'sponsor_name': row[14],
                    'company_name': row[15]
                })
            conn.close()
            return jsonify({'success': True, 'scholarships': scholarships})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'POST':
        # Create new scholarship
        try:
            data = request.get_json()
            
            # Get the first sponsor profile (for now, we'll use sponsor_id = 1)
            # In a real app, this would be based on authentication
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('SELECT id FROM sponsor_profiles LIMIT 1')
            sponsor_row = c.fetchone()
            if not sponsor_row:
                conn.close()
                return jsonify({'success': False, 'message': 'No sponsor profile found'}), 400
            
            sponsor_id = sponsor_row[0]
            
            c.execute('''
                INSERT INTO scholarships (
                    sponsor_id, title, description, amount, currency,
                    gender_criteria, family_income_max, location_type,
                    min_academic_percentage, application_deadline
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sponsor_id,
                data.get('title'),
                data.get('description'),
                data.get('amount'),
                data.get('currency', 'INR'),
                data.get('gender_criteria'),
                data.get('family_income_max'),
                data.get('location_type'),
                data.get('min_academic_percentage'),
                data.get('application_deadline')
            ))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Scholarship created successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/scholarships/eligible', methods=['POST'])
def get_eligible_scholarships():
    # Get scholarships that match student criteria
    try:
        data = request.get_json()
        student_gender = data.get('gender')
        student_family_income = data.get('family_income')
        student_location_type = data.get('location_type')
        student_academic_percentage = data.get('academic_percentage')
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Build query with criteria matching
        query = '''
            SELECT s.*, sp.name as sponsor_name, sp.company_name 
            FROM scholarships s 
            JOIN sponsor_profiles sp ON s.sponsor_id = sp.id 
            WHERE s.is_active = 1
        '''
        params = []
        
        # Add criteria filters
        if student_gender and student_gender != 'Any':
            query += ' AND (s.gender_criteria IS NULL OR s.gender_criteria = ? OR s.gender_criteria = "Any")'
            params.append(student_gender)
        
        if student_family_income is not None:
            query += ' AND (s.family_income_max IS NULL OR s.family_income_max >= ?)'
            params.append(student_family_income)
        
        if student_location_type:
            query += ' AND (s.location_type IS NULL OR s.location_type = ? OR s.location_type = "Any")'
            params.append(student_location_type)
        
        if student_academic_percentage is not None:
            query += ' AND (s.min_academic_percentage IS NULL OR s.min_academic_percentage <= ?)'
            params.append(student_academic_percentage)
        
        query += ' ORDER BY s.amount DESC'
        
        c.execute(query, params)
        scholarships = []
        for row in c.fetchall():
            scholarships.append({
                'id': row[0],
                'sponsor_id': row[1],
                'title': row[2],
                'description': row[3],
                'amount': row[4],
                'currency': row[5],
                'gender_criteria': row[6],
                'family_income_max': row[7],
                'location_type': row[8],
                'min_academic_percentage': row[9],
                'application_deadline': row[10],
                'is_active': row[11],
                'created_at': row[12],
                'updated_at': row[13],
                'sponsor_name': row[14],
                'company_name': row[15]
            })
        conn.close()
        
        return jsonify({'success': True, 'scholarships': scholarships})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Scholarship Applications API endpoints
@app.route('/api/scholarship-applications', methods=['POST'])
def apply_for_scholarship():
    try:
        data = request.get_json()
        scholarship_id = data.get('scholarship_id')
        student_data = data.get('student_data')
        application_message = data.get('application_message', '')
        
        if not scholarship_id:
            return jsonify({'success': False, 'message': 'Missing scholarship ID'}), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if scholarship exists and is active
        c.execute('SELECT id FROM scholarships WHERE id = ? AND is_active = 1', (scholarship_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Scholarship not found or inactive'}), 404
        
        # Insert application
        c.execute('''
            INSERT INTO scholarship_applications (scholarship_id, student_data, application_message)
            VALUES (?, ?, ?)
        ''', (scholarship_id, json.dumps(student_data), application_message))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Application submitted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/scholarship-applications', methods=['GET'])
def get_scholarship_applications():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Get all applications with scholarship and sponsor details
        c.execute('''
            SELECT sa.*, s.title as scholarship_title, s.amount, s.currency,
                   sp.name as sponsor_name, sp.company_name
            FROM scholarship_applications sa
            JOIN scholarships s ON sa.scholarship_id = s.id
            JOIN sponsor_profiles sp ON s.sponsor_id = sp.id
            ORDER BY sa.applied_at DESC
        ''')
        
        applications = []
        for row in c.fetchall():
            student_data = json.loads(row[2]) if row[2] else {}
            applications.append({
                'id': row[0],
                'scholarship_id': row[1],
                'student_data': student_data,
                'application_message': row[3],
                'status': row[4],
                'applied_at': row[5],
                'reviewed_at': row[6],
                'scholarship_title': row[7],
                'amount': row[8],
                'currency': row[9],
                'sponsor_name': row[10],
                'company_name': row[11]
            })
        
        conn.close()
        return jsonify({'success': True, 'applications': applications})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/scholarship-applications/<int:application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['accepted', 'rejected', 'pending']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Update application status
        c.execute('''
            UPDATE scholarship_applications 
            SET status = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, application_id))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Application {status} successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
