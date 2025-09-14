# 🏥 Hospital Management System

A web-based Hospital Management System built with **Flask**, **SQLite3**, **Tailwind CSS**, and **JavaScript** to help manage hospital workflows including appointments, patients, medical records, prescriptions, and AI-assisted medical guidance.

---

## 📌 Features

### 🔐 Authentication & Security
- Role-based login system (Doctor, Patient)
- Secure session management
- Password validations and profile updates

### 🩺 Doctor Dashboard
- View and manage patient list
- Approve or reject appointments
- Add and view medical records
- Write and view prescriptions
- Profile management
- AI Chatbot assistance for medical queries

### 👨‍⚕️ Patient Dashboard
- Book appointments with doctors
- View medical history and prescriptions
- Browse doctors with specialization and experience
- Update profile and personal settings
- AI Chatbot for general medical advice

### 🧠 AI Chatbot
- Integrated with Google Gemini AI
- Provides general medical guidance
- Suggests common medicines (non-prescriptive)
- Answers hospital service queries


### 📝 Prescription Management
- Doctors can add prescriptions per patient record
- Patients can view prescriptions with doctor details and timestamps
- Dynamic prescription tables per patient

---

## 📁 Project Structure

#### Hospital-Management-System/

- ├── .venv/ # Python virtual environment
- ├── static/ # Static files (CSS, JS, images, etc.)
- │ └── (static assets)
- ├── templates/ # HTML templates
- │ ├── AI_chatbot/ # AI Chatbot related HTML templates
- │ │ ├── aichatbot_doctor.html
- │ │ └── aichatbot_patient.html
- │ ├── Doctor/ # Doctor-specific HTML templates
- │ │ ├── doctor_appointments.html
- │ │ ├── doctor_home.html
- │ │ ├── doctor_medical_records.html
- │ │ ├── doctor_patient_list.html
- │ │ ├── doctor_prescription.html
- │ │ └── doctor_profile_management.html
- │ ├── Login/ # Login and registration HTML templates
- │ │ ├── login.html
- │ │ └── register.html
- │ └── Patient/ # Patient-specific HTML templates
- │ ├── Patient_All_Doctors.html
- │ ├── Patient_Booking.html
- │ ├── Patient_home.html
- │ ├── Patient_Medical_History.html
- │ ├── Patient_Prescription_view.html
- │ └── Patient_Setting.html
- ├── .env # Environment variables
- ├── app.py # Main Flask application
- ├── database.db # SQLite database file for general data
- ├── database.py # Database connection and setup logic
- ├── database.sqbpro # SQLiteBrowser project file (for database.db)
- ├── patient.db # SQLite database file patient-specific data
- ├── patient.py # Patient related database logic and operations
- ├── prescription.db # SQLite database file for prescription-specific data
- ├── prescription.py # Prescription database logic and operations
- ├── README.md # Project README file
- └── requirements.txt # Python dependencies

---

## ⚙️ How to Run Locally

### 1. Clone the Repository
```bash
git clone 
cd Hospital_Management_System
2. Create Virtual Environment
bash
Copy code
python -m venv venv
# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
4. Run the App
bash
Copy code
python app.py
5. Access in Browser
cpp
Copy code
http://127.0.0.1:5000

```

Get your API key For Gemini AI from Google and paste in .env file
```

GEMINI_API_KEY=your_api_key;
```

📦 Requirements
```
Flask==2.3.3
gunicorn==23.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
python-dotenv==1.0.1
Werkzeug==2.3.7
google-generativeai==0.2.0
```
SQLite3 is part of the Python Standard Library, so no separate installation is needed.

## 🚧 Upcoming Features
We plan to expand the Hospital Management System with the following enhancements:

### 🧾 Billing & Invoices
Automatically generate bills for appointments, treatments, and prescriptions.

### 📅 Advanced Appointment Scheduling
Enable patients to view available time slots and schedule/reschedule appointments in real time.

### 📊 Admin Dashboard
Add an admin panel to manage doctors, patients, appointments, and system analytics.

### 💬 Secure Messaging System
Enable direct communication between patients and doctors within the platform.

### 📁 Upload Medical Reports
Doctors and patients can upload and access medical documents securely.

### 🔔 Email/SMS Notifications
Alerts for upcoming appointments, prescription refills, and system updates.


Stay tuned for regular updates and improvements! 😊

## 🙋‍♂️ Author
**Mahesh Phalke**

📫 Reach out to collaborate or connect:

💼 LinkedIn: [LinkedIn](https://www.linkedin.com/in/mahesh-phalke159/)

💌 Email: phalkemm159@gmail.com