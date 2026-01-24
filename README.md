# Hospital-Management-System
# MedicalCare
Hospital Management System 

Author: Dana Dvorcakova
Date:   25/01/2026
Link Render:   https://hospital-management-system-2-zpum.onrender.com
Link Github:   https://danadvorcakova.github.io/Hospital-Management-System/


OVERVIEW
The Small Clinic Management System is designed to help clinics efficiently manage doctors, patients, and appointments in a centralized digital platform. It enables administrators to oversee clinic operations, doctors to manage consultations and medical records, and patients to book appointments and access their treatment information. The system improves organization, reduces paperwork, and enhances the overall quality of patient care.


FEATURES 
Role-based access: Admin / Doctor / Patient
CRUD operations for doctors, patients, appointments, and medical records
Audit logging for key actions
Paginated views for large datasets

JavaScript:
Live table search (rows hide/show as typing)
Highlighted search terms
Column-base filtering with dropdowns
Dynamic appointment status chart 
Confirmation modals to delete/cancel actions
Auto-dismiss flash messages


DATABASE

Database Usage:
SQLite is used for local development and testing.
PostgreSQL is used in production when deployed on Render.com.


PERSONAS
Admin
Doctors
Patients

ENTITIES and DATABASE DESIGN:
Admin
Doctor
Patient
Appointment
Medical Record
Diagnosis
Prescription
Audit Log

Entities and Attributes
1.	User
id (PK)
username
password
role (admin, doctor, patient)
2.	Doctor
id (PK)
user_id (FK → User.id)
name
specialization
phone
3.	Patient
id (PK)
user_id (FK → User.id)
name
age
gender
phone
4. Appointment
id (PK)
patient_id (FK → Patient.id)
doctor_id (FK → Doctor.id)
date
time
status (Pending, Completed)
5.	MedicalRecord
id (PK)
appointment_id (FK → Appointment.id)
diagnosis
prescription
6.	AuditLog
id (PK)
user_id (FK → user.id)
username
role
action 
timestamp


USER STORIES:

AUTHENTICATION & ACCESS
1. User Login

As a user (Admin/Doctor/Patient)
I want to log in using my username and password
So that I can securely access the system based on my role.

2. User Logout

As a logged-in user
I want to log out of the system
So that my account remains secure.



ADMIN USER STORIES
3. View Doctors

As an Admin
I want to view the list of all doctors
So that I can manage clinic staff.

4. Add Doctor

As an Admin
I want to add a doctor to the system
So that patients can book appointments with them.

5. Update Doctor Information

As an Admin
I want to update doctor details
So that information remains accurate.

6. Delete Doctor

As an Admin
I want to delete a doctor from the system
So that inactive or resigned doctors are removed.

7. View Patients

As an Admin
I want to view all registered patients
So that I can monitor clinic activity.

8. Update Patients Information

As an Admin
I want to update patient details
So that information remains accurate.

9. Delete Patient

As an Admin
I want to delete a patient account
So that inactive or duplicate patient records are removed.

10. View Dashboard

As an Admin
I want to view a dashboard with key statistics
So that I can quickly monitor system activity.

11. View Audit Log

As an Admin
I want to view a paginated list of audit logs
So that I can review all relevant details.

12. Delete Audit Log

As an Admin
I want to delete audit log records
So that I can remove old unnecessary details.



DOCTOR USER STORIES
13. View Appointments

As a Doctor
I want to view my scheduled appointments
So that I can manage my daily consultations.

14. View Patient Details

As a Doctor
I want to view patient details for an appointment
So that I can understand the patient’s medical background.

15. Add Medical Record

As a Doctor
I want to add diagnosis and prescription
So that patient treatment is properly documented.

16. Edit Medical Record

As a Doctor
I want to edit diagnosis and prescription
So that patient treatment is properly documented.

17. View Medical History

As a Doctor
I want to view a patient’s medical history
So that I can provide better treatment.


PATIENT USER STORIES
18. Patient Registration

As a Patient
I want to register an account
So that I can access clinic services online.

19. Book Appointment

As a Patient
I want to book an appointment with a doctor
So that I can receive medical consultation

20. View Appointment Status

As a Patient
I want to view my appointment status
So that I know whether it is pending or completed.

21. View Medical Records

As a Patient
I want to view my diagnosis and prescription
So that I can follow the doctor’s advice.

22. Update Profile

As a Patient
I want to update my personal information
So that my records stay current.

23. Cancel Appointment

As a Patient
I want to cancel my appointment
So that I can reschedule if needed.


SECURITY & SYSTEM STORIES
24. Role-Based Access Control

As a system
I want to restrict access based on user roles
So that sensitive data is protected.

25. Data Validation

As a system
I want to validate all inputs
So that incorrect or malicious data is prevented.



RELATIONSHIPS

User → Doctor: 1:1 (a user can be a doctor)
User → Patient: 1:1 (a user can be a patient)
Admin (User with role=admin) → Doctor: 1:N (manages multiple doctors)
Doctor → Appointment: 1:N (a doctor has many appointments)
Patient → Appointment: 1:N (a patient books many appointments)
Appointment → MedicalRecord: 1:1 (each appointment has one medical record)
Doctor → MedicalRecord: 1:N (a doctor creates/updates multiple records)
Doctor/Patient → MedicalRecord via Appointment (indirect relationship)
User → AuditLog: 1:N (tracks all actions performed by users)


ER Diagrams
static/image/erd1.png
static/image/erd2.png


TEST CREDENTIAL (admin, doctor, patient)
User
•	Username: admin
•	Password: admin123
Patients
•	Username: bob
•	Password: 123
•	Username: ella
•	Password: 123
Doctor DR. Smith
•	Username: dr_smith
•	Password: 123
•	Username: dr_walsh
•	Password: 123


PROJECT FOLDER STRUCTURE

HOSPITAL-MANAGEMENT-SYSTEM/
│
├── __pycache__/                      # Python cache files (auto-generated)
├── .venv/                            # Virtual environment directory
├── instance/                         # Instance folder for config & database
│   ├── hospital.db                   # SQLite database file
│   └── requirements.txt              # Python dependencies
│
├── static/                           # Static files (CSS, images, JavaScript)
│   ├── css/
│   │   └── style.css                 # Stylesheet for the application
│   ├── image/
│   │   ├── clinic.jpg                # Clinic image
│   │   ├── erd1.png                  # ER diagram image 1
│   │   └── erd2.png                  # ER diagram image 2
│   └── js/
│       └── main.js                   # JavaScript for client-side functionality
│
├── templates/                        # HTML templates for rendering views
│   ├── admin_audit.html              # Admin audit log view
│   ├── admin_doctors.html            # Admin doctors management view
│   ├── admin_patient_edit.html       # Edit patient info (admin)
│   ├── admin_patients.html           # Admin patients management view
│   ├── appointment_edit.html         # Appointment editing view
│   ├── appointment_new.html          # New appointment creation view
│   ├── base.html                     # Base template with common layout
│   ├── doctor_appointments.html      # Doctor's appointments overview
│   ├── doctor_edit.html              # Doctor profile editing view
│   ├── doctor_new.html               # New doctor registration
│   ├── doctor_patient_detail.html    # Details of patient for doctor
│   ├── doctor_patients.html          # List of patients for doctor
│   ├── doctor_records.html           # Doctor's medical records view
│   ├── index.html                    # Homepage or landing page
│   ├── login.html                    # User login page
│   ├── pagination.html               # Pagination controls for lists
│   ├── patient_appointments.html     # Patient's appointments view
│   ├── patient_profile.html          # Patient profile view
│   ├── patient_records.html          # Patient medical records view
│   ├── record_edit.html              # Edit medical record view
│   ├── record_new.html               # New medical record creation view
│   └── register.html                 # User registration page
│
├── app.py                            # Main Flask application file
├── config.py                         # Configuration settings for the app
├── models.py                         # Database models using SQLAlchemy
├── README.md                         # Project documentation
└── ER Diagrams.docx                  # Entity-Relationship diagrams for DB design


Instructions on how to deploy and access the web app on Render.com
1.	Go to https://render.com and create an account
2.	Sign up or log in
3.	Push the project to a GitHub repository
4.	On Render, click New + → Web Service
5.	Choose Build from a Git Repository and select your repos
6.	Fill in the service details:
•	Environment: Python
•	Build Command: pip install -r requirements.txt
•	Start Command: gunicorn app:app
7.	Click Deploy
8.	After deployment completes, Render will generate a public URL: https://hospital-management-system-2-zpum.onrender.com


Setup and Installation instructions
1. Clone the repository:
git clone < https://github.com/DanaDvorcakova/Hospital-Management-System.git>   
cd Hospital-Management-System

2. Create a virtual environment:
python -m venv .venv
source On Windows:  .venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt

4. Initialize the database:
flask shell
- from models import db
- db.create_all()
- exit()

5. Run the app locally:
py app.py
Running on http://127.0.0.1:8080


TECHNOLOGY

Python 3.13.9  
Flask  
Flask-SQLAlchemy (ORM)  
SQLite (local development)  
PostgreSQL (production deployment on Render)  
HTML, CSS, JavaScript  
draw.io  

Note: SQLite is used for local development and testing. PostgreSQL is used in production when deployed on Render.com.


LIST OF SOURCES
Image – google.com
Logo and the other icons – google.com
Inspirations – google.com
Udemy
YouTube
w3schools
github.com
Class Material
