import sqlite3
import datetime
import os


DB_NAME = 'patient.db'

def create_patient_database():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn


def create_doctor_patient_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctor_patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            patient_id INTEGER,
            added_date TEXT,
            UNIQUE(doctor_id, patient_id),
            FOREIGN KEY (doctor_id) REFERENCES users(id),
            FOREIGN KEY (patient_id) REFERENCES patient(id)
        )
    ''')
    conn.commit()



def create_medical_records_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            patient_name TEXT,
            doctor_id INTEGER,
            diagnosis TEXT,
            document_path TEXT,
            date TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patient(id),
            FOREIGN KEY(doctor_id) REFERENCES users(id)
        )
    ''')
    conn.commit()


def create_appointment_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            patient_name TEXT,
            doctor_id INTEGER,
            doctor_name TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            approved_time TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (patient_id) REFERENCES patient(id),
            FOREIGN KEY (doctor_id) REFERENCES users(id)
        )
    ''')
    conn.commit()




conn = create_patient_database()
create_doctor_patient_table(conn)
