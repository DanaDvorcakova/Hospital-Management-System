from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,time

db = SQLAlchemy()

# -------------------------------
# User
# -------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / doctor / patient

    # Relationships
    doctor_profile = db.relationship("Doctor", backref="user", uselist=False)
    patient_profile = db.relationship("Patient", backref="user", uselist=False)

# -------------------------------
# Doctor
# -------------------------------
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)

    appointments = db.relationship("Appointment", backref="doctor", lazy=True)

# -------------------------------
# Patient
# -------------------------------
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=True)

    appointments = db.relationship("Appointment", backref="patient", lazy=True)

# -------------------------------
# Appointment
# -------------------------------
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)           # <- Change from String to Date
    time = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Pending")

    medical_record = db.relationship("MedicalRecord", backref="appointment", uselist=False)

# -------------------------------
# Medical Record
# -------------------------------
class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)


appointment = db.relationship('Appointment', backref='medical_records', lazy=True)

# -------------------------------
# Audit Log
# ------------------------------
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # ForeignKey to User model
    username = db.Column(db.String(80))
    role = db.Column(db.String(50))
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Establish relationship with User
    user = db.relationship('User', backref='audit_logs', lazy=True)

 
