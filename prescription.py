import sqlite3
import os

db_name = 'prescription.db'


def create_prescription_table(patient_id):
    # Connect to patient.db
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    table_name = f'prescription_patient_{patient_id}'

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER,
            medication_name TEXT,
            quantity INTEGER,
            refills INTEGER,
            frequency TEXT,
            timing TEXT,
            additional_instructions TEXT,
            doctor_id INTEGER,
            patient_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()