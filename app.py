import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from database import create_database, create_tables
from prescription import create_prescription_table
# from healthcare_db import create_health_tables,add_prescription,get_all_prescriptions, delete_prescription,get_prescription_by_patient
from patient import create_patient_database, create_medical_records_table, create_appointment_table

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create database and table when application starts
conn = create_database()
create_tables(conn)
conn.close()
# create-health_tables()



conn_patient = create_patient_database()
create_medical_records_table(conn_patient)
create_appointment_table(conn_patient)
conn_patient.commit()
conn_patient.close()
create_patient_database()


users = []

@app.route('/')
def home():
    return render_template('Login/login.html')

def calculate_age(dob_str):
    """Calculate age from dob string (YYYY-MM-DD)."""
    birth_date = datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract form data
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        gender = request.form.get('gender')
        bio = request.form.get('bio')
        address = request.form.get('address')
        dob = request.form.get('dob')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Validations
        if not all([full_name, username, phone_number, gender, address, dob, email, password, role]):
            flash('All fields are required')
            return redirect(url_for('register'))

        if '@' not in email or '.' not in email:
            flash('Invalid email format')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long')
            return redirect(url_for('register'))

        if role not in ['doctor', 'patient']:
            flash('Invalid role')
            return redirect(url_for('register'))

        if gender not in ['male', 'female', 'transgender']:
            flash('Invalid Gender')
            return redirect(url_for('register'))

        # DB operations
        conn = create_database()
        cursor = conn.cursor()

        existing = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('Email already registered')
            conn.close()
            return redirect(url_for('register'))

        # Insert user
        cursor.execute('''
            INSERT INTO users (full_name, username, phone_number, gender, address, dob, email, password, role, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, username, phone_number, gender, address, dob, email, password, role, bio))
        
        user_id = cursor.lastrowid

        # Insert into role-specific table
        if role == 'doctor':
            cursor.execute('INSERT INTO doctor (user_id,full_name) VALUES (?,?)', (user_id,full_name,))
        elif role == 'patient':
            age = calculate_age(dob)
            cursor.execute('INSERT INTO patient (user_id,full_name,age) VALUES (?,?,?)', (user_id,full_name,age,))
            create_prescription_table(user_id)

        conn.commit()
        conn.close()

        flash('Registration successful!')
        return redirect(url_for('login'))

    return render_template('Login/register.html')

        
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = create_database()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if not user or user['password'] != password:
            flash('Invalid email or password')
            return redirect(url_for('login'))

        # Store user data in session
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['phone_number'] = user['phone_number']
        session['gender'] = user['gender']
        session['bio'] = user['bio']
        session['address'] = user['address']
        session['dob'] = user['dob']
        session['role'] = user['role']

        # Redirect based on role
        if user['role'] == 'doctor':
            return redirect(url_for('doctor_home'))
        elif user['role'] == 'patient':
            return redirect(url_for('patient_home'))
        else:
            flash('Invalid role in user data')
            return redirect(url_for('login'))

    return render_template('Login/login.html')




@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        flash("Please log in to update profile")
        return redirect(url_for('login'))

    # Extract updated data
    user_id = session['user_id']
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    dob = request.form.get('dob')
    gender = request.form.get('gender')
    address = request.form.get('address')
    bio = request.form.get('bio')

    conn = create_database()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET
            full_name = ?, email = ?, phone_number = ?,
            dob = ?, gender = ?, address = ?, bio = ?
        WHERE id = ?
    ''', (full_name, email, phone_number, dob, gender, address, bio, user_id))
    conn.commit()
    conn.close()

    # Update session data
    session['full_name'] = full_name
    session['email'] = email
    session['phone_number'] = phone_number
    session['dob'] = dob
    session['gender'] = gender
    session['address'] = address
    session['bio'] = bio

    flash('Profile updated successfully!', 'success')
    return redirect('doctor_Profile_Management' if session['role'] == 'doctor' else 'Patient_Setting')




@app.route('/doctor_Home')
def doctor_home():
    if session['role'] != 'doctor':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    return render_template('Doctor/doctor_home.html', full_name=session['full_name'], email=session['email'])

@app.route('/doctor_Appointments')
def doctor_appointments():
    if session.get('role') != 'doctor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))
    
    doctor_id = session.get('user_id')

    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Attach the user-related database (containing the patient table)
    cur.execute("ATTACH DATABASE 'database.db' AS db")
    
    # Now join using db.patient
    cur.execute('''
        SELECT a.id,
               a.appointment_date,
               a.appointment_time,
               a.status,
               db.patient.full_name AS patient_name
        FROM appointments a
        JOIN db.patient ON a.patient_id = db.patient.user_id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    ''', (doctor_id,))

    appointments = cur.fetchall()
    conn.close()

    return render_template("Doctor/doctor_appointments.html",
                           appointments=appointments,
                           full_name=session['full_name'],
                           specialization=session.get('specialization'), email=session['email'])


@app.route('/doctor_Patient_List')
def doctor_patient_list():
    if session.get('role') != 'doctor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    doctor_id = session.get('user_id')

    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("ATTACH DATABASE 'database.db' AS db")

    cur.execute('''
            SELECT 
                p.patient_id, 
                p.patient_name, 
                db.patient.age, 
                MAX(p.appointment_date) AS last_visit
            FROM appointments p
            JOIN db.patient ON p.patient_id = db.patient.user_id
            WHERE p.doctor_id = ?
            AND p.status = 'Approved'
            GROUP BY p.patient_id
        ''', (doctor_id,))

    patients = cur.fetchall()
    conn.close()

    return render_template("Doctor/doctor_patient_list.html",
                           patients=patients,
                           full_name=session.get('full_name'),
                           email=session.get('email'))

@app.route('/doctor_Medical_Records', methods=['GET', 'POST'])
def doctor_medical_records():
    if session.get('role') != 'doctor':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))

    doctor_id = session.get('user_id')

    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

     # Get medical records created by this doctor
    cursor.execute("""
        SELECT mr.*, mr.patient_name
        FROM medical_records mr
        WHERE mr.doctor_id = ?
        GROUP BY mr.patient_id
        ORDER BY mr.date DESC
    """, (doctor_id,))
    medical_records = cursor.fetchall()

    cursor.execute("ATTACH DATABASE 'database.db' AS db")

    # Get approved patients for this doctor
    cursor.execute('''
            SELECT 
                p.patient_id, 
                p.patient_name 
            FROM appointments p
            JOIN db.patient ON p.patient_id = db.patient.user_id
            WHERE p.doctor_id = ?
            GROUP BY p.patient_id
        ''', (doctor_id,))
    patients = cursor.fetchall()

    conn.close()

    return render_template(
        'Doctor/doctor_medical_records.html',
        medical_records=medical_records,
        patients=patients,
        full_name=session['full_name'],
        email=session['email']
    )

def get_patient_id_from_record(record_id):
    import sqlite3
    conn = sqlite3.connect("patient.db")
    cursor = conn.cursor()

    cursor.execute("SELECT patient_id FROM medical_records WHERE  id = ?", (record_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]  # patient_id
    else:
        return None

@app.route('/add_prescription', methods=['POST'])
def add_prescription():
    record_id = request.form.get("record_id")
    medication_names = request.form.getlist("medication_name[]")
    quantities = request.form.getlist("quantity[]")
    refills = request.form.getlist("refills[]")
    frequencies = request.form.getlist("frequency[]")
    timings = request.form.getlist("timing[]")
    instructions = request.form.getlist("instructions[]")
    doctor_id = session.get("user_id")

    # Get patient_id from record_id or session (this depends on your system)
    patient_id = get_patient_id_from_record(record_id)  # You must implement this

    table_name = f"prescription_patient_{patient_id}"

    conn = sqlite3.connect("prescription.db")
    cursor = conn.cursor()


    for i in range(len(medication_names)):
        cursor.execute(f"""
            INSERT INTO {table_name} (record_id, medication_name, quantity, refills, frequency, timing, additional_instructions,doctor_id,patient_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_id,
            medication_names[i],
            quantities[i],
            int(refills[i]) if refills[i].isdigit() else 0,
            frequencies[i],
            timings[i],
            instructions[i],
            doctor_id,
            patient_id
        ))

    conn.commit()
    conn.close()

    flash("Prescription added successfully!")
    return redirect(url_for("doctor_medical_records"))  # Replace with actual view


@app.route("/prescription/<int:patient_id>/<int:record_id>")
def view_prescription(patient_id, record_id):
    conn = sqlite3.connect("prescription.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    table_name = f"prescription_patient_{patient_id}"

    try:
        cursor.execute(f"""
            SELECT medication_name, MAX(quantity) AS quantity, MAX(refills) AS refills,
                MAX(frequency) AS frequency, MAX(timing) AS timing, MAX(additional_instructions) AS additional_instructions,
                MAX(created_at) AS created_at,doctor_id
            FROM {table_name}
            WHERE record_id = ?
            GROUP BY medication_name
        """, (record_id,))

        prescriptions = cursor.fetchall()
        doctor_id = prescriptions[0]["doctor_id"] if prescriptions else None
        date = prescriptions[0]["created_at"] if prescriptions else None
    except sqlite3.OperationalError:
        return "Prescription table not found", 404
    finally:
        conn.close()

    patient_conn = sqlite3.connect("database.db")
    patient_conn.row_factory = sqlite3.Row
    patient_cursor = patient_conn.cursor()
    patient_cursor.execute("SELECT * FROM users WHERE id = ?", (patient_id,))
    patient_details = patient_cursor.fetchone()


    patient_cursor.execute("SELECT full_name FROM users WHERE id = ?",(doctor_id,))
    doctor_details = patient_cursor.fetchone()
    patient_conn.close()

    return render_template("Doctor/doctor_prescription.html",date = date, doctor=doctor_details, patient = patient_details, prescriptions=prescriptions)




# @app.route('/doctor_Prescription_Management')
# def doctor_prescriptions_management():
#     if session['role'] != 'doctor':
#         flash('You are not authorized to access this page')
#         return redirect(url_for('login'))
#     return render_template('Doctor/doctor_prescriptions_management.html', full_name=session['full_name'], email=session['email'])

@app.route('/doctor_Profile_Management')
def doctor_profile_management():
    if session['role'] != 'doctor':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    return render_template('Doctor/doctor_profile_management.html', email=session['email'], full_name=session['full_name'], phone_number=session['phone_number'], gender = session['gender'], bio = session['bio'] , address=session['address'], dob=session['dob']) 


@app.route('/Patient_home')
def patient_home(): 
    if session['role'] != 'patient':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    return render_template('Patient/patient_home.html', full_name=session['full_name'], email=session['email'])

@app.route('/Patient_All_Doctors')
def patient_all_doctors():
    if session.get('role') != 'patient':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            users.full_name,
            users.bio,
            doctor.specialization,
            doctor.experience
        FROM users
        JOIN doctor ON users.id = doctor.user_id
        WHERE users.role = 'doctor'
    """)

    rows = cursor.fetchall()
    conn.close()

    doctors = [dict(row) for row in rows]


    return render_template('Patient/Patient_All_Doctors.html', doctors=doctors, full_name=session['full_name'], email=session['email'])

@app.route('/Patient_Booking', methods=['GET'])
def patient_booking():
    if session.get('role') != 'patient':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    patient_user_id = session.get('user_id')

    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Attach users and doctor info from database.db
    cur.execute("ATTACH DATABASE 'database.db' AS db")

    cur.execute('''
        SELECT 
            a.id,
            a.appointment_date,
            a.appointment_time,
            a.approved_time,
            a.status,
            db.doctor.full_name AS doctor_name,
            db.doctor.specialization
        FROM appointments a
        JOIN db.doctor ON a.doctor_id = db.doctor.user_id
        WHERE a.patient_id = ?
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    ''', (patient_user_id,))

    appointments = cur.fetchall()

    # ✅ Fetch list of all doctors
    cur.execute('''
        SELECT user_id, full_name 
        FROM db.doctor
    ''')
    doctors = cur.fetchall()

    conn.close()

    return render_template('Patient/Patient_Booking.html',
                           appointments=appointments,
                           doctors=doctors,
                           full_name=session['full_name'], 
                           email=session['email'])






@app.route('/Patient_Medical_History')
def patient_medical_history():
    if session['role'] != 'patient':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM medical_records WHERE patient_id = ?", (session['user_id'],))
    medical_records = cursor.fetchall()
    
    doctor_id = medical_records[0]["doctor_id"] if medical_records else None
    conn.close()

    doctor_conn = sqlite3.connect("database.db")
    doctor_conn.row_factory = sqlite3.Row
    doctor_cursor = doctor_conn.cursor()
    doctor_cursor.execute("SELECT full_name FROM users WHERE id = ?", (doctor_id,))
    doctor = doctor_cursor.fetchone()
    doctor_conn.close()
    return render_template('Patient/Patient_Medical_History.html', doctor = doctor, medical = medical_records, full_name=session['full_name'], email=session['email'])

@app.route('/Patient_Prescription_view/')
def patient_prescription_view():
    if session['role'] != 'patient':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    
    patient_id = session['user_id']
    table_name = f"prescription_patient_{patient_id}"

    try:
        # Fetch prescription details
        conn = sqlite3.connect("prescription.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT medication_name, MAX(quantity) AS quantity, MAX(refills) AS refills,
                   MAX(frequency) AS frequency, MAX(timing) AS timing, MAX(additional_instructions) AS additional_instructions,
                   MAX(doctor_id) AS doctor_id, MAX(created_at) AS created_at
            FROM {table_name}
            WHERE patient_id = ?
            GROUP BY medication_name
        """, (patient_id,))
        prescriptions = cursor.fetchall()

        # Get the date from one record (any one, as all belong to same prescription)
        cursor.execute(f"SELECT MAX(created_at) as created_at, MAX(doctor_id) as doctor_id , patient_id FROM {table_name} WHERE patient_id = ?", (patient_id,))
        meta_data = cursor.fetchone()
        date = meta_data["created_at"]
        patientId = meta_data["patient_id"]
        doctor_id = meta_data["doctor_id"]

    except sqlite3.OperationalError:
        return "Prescription table not found.", 404
    finally:
        conn.close()

    # Fetch doctor details
    doctor_conn = sqlite3.connect("database.db")
    doctor_conn.row_factory = sqlite3.Row
    doctor_cursor = doctor_conn.cursor()
    doctor_cursor.execute("SELECT full_name, phone_number FROM users WHERE id = ?", (doctor_id,))
    doctor = doctor_cursor.fetchone()
    doctor_conn.close()

    # Get patient details for completeness
    patient_conn = sqlite3.connect("database.db")
    patient_conn.row_factory = sqlite3.Row
    patient_cursor = patient_conn.cursor()
    patient_cursor.execute("SELECT * FROM users WHERE id = ?", (patient_id,))
    patient = patient_cursor.fetchone()
    patient_conn.close()

    return render_template('Patient/Patient_Prescription_view.html', prescriptions=prescriptions, patientId=patientId, doctor=doctor, date=date, patient=patient, full_name=session['full_name'], email=session['email'])

@app.route('/Patient_Setting')
def patient_setting():
    if session['role'] != 'patient':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    return render_template('Patient/Patient_Setting.html', email=session['email'], full_name=session['full_name'], phone_number=session['phone_number'], gender = session['gender'], bio = session['bio'] , address=session['address'], dob=session['dob'])

        

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return render_template('Login/login.html')

# @app.route("/add_prescription", methods=["POST"])
# def api_add_prescription():
#     data = request.json
#     add_prescription(
#         patient=data["patient"],
#         medicine=data["medicine"],
#         dosage=data["dosage"],
#         instructions=data["instructions"]
#     )
#     return jsonify({"message": "Prescription saved successfully"}), 201
    

# @app.route("/get_prescriptions")
# def api_get_prescriptions():
#     patient = request.args.get('patient', '')
#     if patient:
#         prescriptions = get_prescription_by_patient(patient)
#     else:
#         prescriptions = get_all_prescriptions()
#     return jsonify(prescriptions)


# @app.route('/delete_prescription/<int:prescription_id>', methods=['DELETE'])
# def handle_delete_prescription(prescription_id):
#     try:
#         delete_prescription(prescription_id)
#         return jsonify({'success': True}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/add_medical_record", methods=["POST"])
def submit_medical_record():
    if session['role'] != 'doctor':
        flash('Unauthorized access')
        return redirect(url_for('login'))
    
    patient_id = request.form["patient_id"]
    diagnosis = request.form["diagnosis"]
    doctor_id = session.get('user_id')
    document_path = None
    
    conn = sqlite3.connect("patient.db")
    cursor = conn.cursor()

    cursor.execute("SELECT patient_name FROM appointments WHERE patient_id = ?", (patient_id,))
    patient_row = cursor.fetchone()

    if not patient_row:
        flash("Patient not found.")
        conn.close()
        return redirect(url_for("doctor_medical_records"))
    patient_name = patient_row[0]
    # Insert medical record
    cursor.execute("""
        INSERT INTO medical_records 
        (patient_id, patient_name, doctor_id, diagnosis, date,  document_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        patient_name,
        doctor_id,
        diagnosis,
        datetime.now().strftime("%Y-%m-%d"),
        document_path  # This will be NULL if no file uploaded
    ))
    conn.commit()
    conn.close()

    return redirect(url_for("doctor_medical_records"))

@app.route("/submit_appointment", methods=["POST"])
def submit_appointment():
    if session['role'] != 'patient':
        flash('Unauthorized access')
        return redirect(url_for('login'))

    patient_name = session.get("full_name")
    patient_id = session.get("user_id")
    doctor_id = request.form["doctor_id"]
    appointment_date = request.form["appointment_date"]
    appointment_time = request.form["appointment_time"]

    conn = sqlite3.connect("patient.db")
    cursor = conn.cursor()

    cursor.execute("ATTACH DATABASE 'database.db' AS db")

    # Fetch doctor_name from db.doctor
    cursor.execute("SELECT full_name FROM db.doctor WHERE user_id = ?", (doctor_id,))
    doctor_row = cursor.fetchone()
    if doctor_row:
        doctor_name = doctor_row[0]
    else:
        flash("Selected doctor not found.")
        return redirect(url_for("patient_booking"))
    

    cursor.execute("""
        INSERT INTO appointments (patient_id, patient_name, doctor_id, doctor_name, appointment_date, appointment_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_id, patient_name, doctor_id, doctor_name, appointment_date, appointment_time))


    conn.commit()
    conn.close()

    flash("Appointment request submitted!")
    return redirect(url_for("patient_booking"))


@app.route('/approve_appointment', methods=['POST'])
def approve_appointment():
    if session.get('role') != 'doctor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    appointment_id = request.form.get('appointment_id')
    approved_time = request.form.get('approved_time')
    doctor_id = session.get('user_id')

    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Attach main user database
    cur.execute("ATTACH DATABASE 'database.db' AS db")

    # Fetch patient from appointment
    cur.execute('''
        SELECT a.patient_id, a.doctor_id
        FROM appointments a
        WHERE a.id = ?
    ''', (appointment_id,))
    appointment = cur.fetchone()

    if not appointment:
        flash("Appointment not found.")
        conn.close()
        return redirect(url_for('doctor_appointments'))

    patient_id = appointment['patient_id']

    # Approve appointment
    cur.execute('''
        UPDATE appointments
        SET status = 'Approved', approved_time = ?
        WHERE id = ?
    ''', (approved_time, appointment_id))

    # Add to doctor-patient table if not already present
    cur.execute('''
        SELECT 1 FROM doctor_patients
        WHERE doctor_id = ? AND patient_id = ?
    ''', (doctor_id, patient_id))

    if not cur.fetchone():
        cur.execute('''
            INSERT INTO doctor_patients (doctor_id, patient_id, added_date)
            VALUES (?, ?, DATE('now'))
        ''', (doctor_id, patient_id))

    conn.commit()
    conn.close()
    flash("Appointment approved and patient added.")
    return redirect(url_for('doctor_appointments'))



@app.route('/view_appointments')
def view_appointments():
    if session.get('role') != 'doctor':
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            a.id,
            p.name AS patient_name,
            a.appointment_date,
            a.appointment_time,
            a.status
        FROM appointments a
        JOIN patient p ON a.patient_id = p.id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date, a.appointment_time
    """, (session['user_id'],))  # Ensure doctor ID is stored in session
    appointments = cur.fetchall()
    conn.close()

    return render_template("Doctor/view_appointments.html", appointments=appointments)



@app.route("/reject_appointment/<int:id>")
def reject_appointment(id):
    if session['role'] != 'doctor':
        return redirect(url_for('login'))

    con = sqlite3.connect("patient.db")
    cur = con.cursor()
    cur.execute("UPDATE appointments SET status = 'Rejected' WHERE id = ?", (id,))
    con.commit()
    con.close()
    flash("Appointment rejected.")
    return redirect(url_for('doctor_appointments'))




# @app.route('/api/patients', methods=['GET'])
# def api_get_patients():
#     conn = create_patient_database()
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name, gender, age, condition, status, last_visit FROM patient")
#     patients = cursor.fetchall()
#     conn.close()
#     return jsonify([dict(p) for p in patients])

# @app.route('/api/add_patient', methods=['POST'])
# def api_add_patient():
#     data = request.json
#     name = data.get('name')
#     gender = data.get('gender')
#     age = data.get('age')
#     condition = data.get('condition')
#     status = data.get('status')
#     last_visit = data.get('last_visit')

#     conn = create_patient_database()
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO patient (name, gender, age, condition, status, last_visit)
#         VALUES (?, ?, ?, ?, ?, ?)
#     """, (name,gender, age, condition, status, last_visit))
#     conn.commit()
#     conn.close()

#     return jsonify({"success": True})

# @app.route('/api/deletePatient/<int:added_patient_id>', methods=['DELETE'])
# def api_deletePatient(added_patient_id):
#     try: 
#         conn = create_patient_database()
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM patient WHERE id = ?", (added_patient_id,))
#         conn.commit()
#         conn.close()
#         return jsonify({"success": True})
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)})




# @app.route('/api/patientsList', methods=['GET'])
# def api_get_patientsList():
#     conn = create_patient_database()
#     cur = conn.cursor()
#     cur.execute("SELECT id, name FROM patient")
#     patients = cur.fetchall()
#     conn.close()
#     return jsonify([dict(p) for p in patients])

# @app.route('/api/medical_records', methods=['GET'])
# def api_get_medical_records():
#     conn = create_patient_database()
#     conn.row_factory = sqlite3.Row  # Enables dictionary-style access
#     cursor = conn.cursor()
#     records = cursor.execute("""
#         SELECT mr.id, p.name as patient_name, mr.diagnosis, mr.treatment, mr.date
#         FROM medical_records mr
#         JOIN patient p ON mr.patient_id = p.id
#         ORDER BY mr.date DESC
#     """).fetchall()
#     conn.close()
#     return jsonify([dict(r) for r in records])


# @app.route('/api/add_medical_record', methods=['POST'])
# def api_add_medical_record():
#     try:
#         data = request.get_json()
#         patient_id = data.get('patient_id')
#         diagnosis = data.get('diagnosis')
#         treatment = data.get('treatment')
#         date = datetime.datetime.now()

#         # Validate data
#         if not patient_id or not diagnosis or not treatment:
#             return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

#         # Insert into database
#         cursor = sqlite3.connect('patient.db').cursor()
#         cursor.execute("INSERT INTO medical_records (patient_id, diagnosis, treatment, date) VALUES (?, ?, ?, ?)",
#                        (patient_id, diagnosis, treatment,date))
#         cursor.connection.commit()

#         return jsonify({'success': True, 'message': 'Record added successfully.'})

#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'success': False, 'message': 'Something went wrong.'}), 500



# @app.route('/api/delete_medical_record/<int:record_id>', methods=['DELETE'])
# def delete_medical_record(record_id):
#     try:
#         conn = create_patient_database()
#         conn.row_factory
#         c = conn.cursor()
#         c.execute("DELETE FROM medical_records WHERE id = ?", (record_id,))
#         conn.commit()
#         conn.close()
#         return jsonify({'success': True})
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)})


# AI Chatbot Integration
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=gemini_api_key)

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_message = request.json.get("message")
    
    # Create model
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Add a system instruction so AI always responds like a doctor
    system_prompt = """
        You are an AI-powered Medical Assistant for a hospital. Follow these rules:

        1. **Greetings:**  
        - If the user greets you (hi, hello, good morning), respond warmly and naturally.  
        - Example: "Hello! How can I help you today?"  

        2. **Medical queries (diseases, symptoms, or medicine requests):**  
        - Provide simple general medical information.  
        - Give **commonly used general medicine names** for the symptom or disease.  
            - Examples:  
            - Fever → Paracetamol, Ibuprofen  
            - Headache → Ibuprofen, Paracetamol  
            - Cold → Cetirizine  
            - Acidity → Antacid (like Ranitidine)  
            - Dehydration → ORS  
        - List 1–3 common medicines.  
        - **Do NOT start with a greeting**; answer directly.  
        - Always remind the user that these are **general medicines** and they must consult a doctor for proper dosage and treatment.  

        3. **Hospital services queries (appointments, visiting hours, facilities):**  
        - Answer clearly and directly.  

        4. **Restrictions:**  
        - Never give exact dosages or personalized prescriptions.  
        - Never refuse to give a general medicine name when asked.  
        - Keep a professional, friendly, and supportive tone.
        """
    response = model.generate_content(system_prompt + "\n\nPatient: " + user_message + "\nDoctor AI:")
    reply = response.text if response else "Sorry, I couldn't generate a response."
    
    return jsonify({"reply": reply})

@app.route("/doctor_Chatbot")
def doctor_chatbot():
    if session['role'] != 'doctor':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    return render_template("AI_chatbot/aichatbot_doctor.html", full_name=session['full_name'], email=session['email'])

@app.route("/patient_Chatbot")
def patient_chatbot():
    if session['role'] != 'patient':
        flash('You are not authorized to access this page')
        return redirect(url_for('login'))
    return render_template("AI_chatbot/aichatbot_patient.html", full_name=session['full_name'], email=session['email'])

# # for offline in local pc
# if __name__ == '__main__':
#     app.run(debug=True)

# for online hosting and deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)