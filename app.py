
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from models import User, Doctor, Patient, Appointment, MedicalRecord, AuditLog, db
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time, date


# ===========================
# Flask App Setup
# ===========================
app = Flask(__name__)
app.config.from_object("config")
app.secret_key = "supersecretkey"
db.init_app(app)


# ===========================
# Database Seeding
# ===========================
def seed_db_if_needed():
    """Seeds the database with default admin, doctors, patients, appointments, and medical records."""
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin")
        db.session.add(admin)
        db.session.commit()

        

    # --- Doctors ---
    doctors_to_seed = [
        {"username": "dr_smith", "name": "Dr. Smith", "specialization": "Cardiology", "phone": "1234567890"},
        {"username": "dr_jones", "name": "Dr. Jones", "specialization": "Neurology", "phone": "0987654321"},
    ]
    for doc in doctors_to_seed:
        if not User.query.filter_by(username=doc["username"]).first():
            user = User(
                username=doc["username"],
                password=generate_password_hash("123"),
                role="doctor")
            db.session.add(user)
            db.session.commit()

            doctor = Doctor(
                user_id=user.id,
                name=doc["name"],
                specialization=doc["specialization"],
                phone=doc["phone"])
            db.session.add(doctor)
            db.session.commit()

    # --- Patients ---
    patients_to_seed = [
        {"username": "alice", "name": "Alice", "age": 30, "gender": "Female", "phone": "0822547896"},
        {"username": "bob", "name": "Bob", "age": 40, "gender": "Male", "phone": "0248796558"},
    ]
    for pat in patients_to_seed:
        if not User.query.filter_by(username=pat["username"]).first():
            user = User(
                username=pat["username"],
                password=generate_password_hash("123"),
                role="patient")
            db.session.add(user)
            db.session.commit()

            patient = Patient(
                user_id=user.id,
                name=pat["name"],
                age=pat["age"],
                gender=pat["gender"],
                phone=pat["phone"])
            db.session.add(patient)
            db.session.commit()

            

    # --- Appointments ---
    if Appointment.query.count() == 0:
        doc1 = Doctor.query.filter_by(name="Dr. Smith").first()
        doc2 = Doctor.query.filter_by(name="Dr. Jones").first()
        pat1 = Patient.query.filter_by(name="Alice").first()
        pat2 = Patient.query.filter_by(name="Bob").first()

        appt1 = Appointment(
            patient_id=pat1.id,
            doctor_id=doc1.id,
            date=datetime(2026, 1, 15).date(),
            time=time(10, 30),
            status="Pending")
        
        appt2 = Appointment(
            patient_id=pat2.id,
            doctor_id=doc2.id,
            date=datetime(2026, 1, 20).date(),
            time=time(11, 30),
            status="Pending")
        db.session.add_all([appt1, appt2])
        db.session.commit()  # Commit the appointments to the database

        # --- Medical Records (after appointments are committed) ---
        record1 = MedicalRecord(
            appointment_id=appt1.id,
            diagnosis="Hypertension",
            prescription="Indapamide")
        
        record2 = MedicalRecord(
            appointment_id=appt2.id,
            diagnosis="Migraine",
            prescription="Tricyclic")
        db.session.add_all([record1, record2])
        db.session.commit()



# ===========================9
# Context Processor for Year
# ===========================
@app.context_processor
def inject_now():
    """Injects the current year into all templates as 'current_year'."""
    return {'current_year': datetime.now().year}

# ===========================
# Role-Based Access Decorator
# ===========================
def role_required(role):
    """Decorator to restrict access to users with a specific role.

    Args:
        role (str): Role required to access the route.

    Returns:
        function: Wrapped function that checks session role.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "role" not in session or session["role"] != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ===========================
# Logging Function
# ===========================
def log_action(user, action_desc):
    """Logs an action to the AuditLog table.
      Args:
        user (User or None): User performing the action. If None, logs as 'System'.
        action_desc (str): Description of the action performed."""
    log_entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "System",
        role=user.role if user else None,
        action=str(action_desc).strip()
    )
    db.session.add(log_entry)
    db.session.commit()

# ===========================
# Helper Functions
# ===========================
def get_user(role):
    """Returns the current user's model instance based on role.

    Args:
        role (str): 'doctor' or 'patient'

    Returns:
        Doctor or Patient instance, or None if not found."""
    if role == "doctor":
        return Doctor.query.filter_by(user_id=session["user_id"]).first()
    elif role == "patient":
        return Patient.query.filter_by(user_id=session["user_id"]).first()
    return None

def paginate_query(query, page, per_page=10):
    """Paginates a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object.
        page (int): Page number.
        per_page (int): Items per page.

    Returns:
        Pagination object."""
    return query.paginate(page=page, per_page=per_page, error_out=False)

def validate_appointment_date_time(date_str, time_str):
    """Validates appointment date and time.

    Args:
        date_str (str): Date string in YYYY-MM-DD format.
        time_str (str): Time string in HH:MM format.

    Returns:
        tuple(bool, str or None): (is_valid, error_message)"""
    try:
        appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Invalid date format."
    
    if appt_date < date.today():
        return False, "Cannot select a past date."
    
    try:
        appt_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return False, "Invalid time format."
    
    return True, None

# ===========================
# AUTH ROUTES
# ===========================
@app.route("/", methods=["GET", "POST"])
def login():
    """Handles user login and starts a session if credentials are valid."""
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            
            return redirect(url_for("index"))
        
        flash("Invalid credentials", "danger")  
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Logs out the user by clearing session and redirects to login."""
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

@app.route("/index")
def index():
    """Redirects users to their dashboard based on role."""
    if "role" not in session:
        return redirect(url_for("login"))   
    if session["role"] == "admin":
        return redirect(url_for("admin_index"))  
    elif session["role"] == "doctor":
        return redirect(url_for("doctor_appointments"))
    elif session["role"] == "patient":
        return redirect(url_for("patient_appointments"))
    
    return "Invalid role"

# ===========================
# ADMIN ROUTES
# ===========================
@app.route("/admin/index")
@role_required("admin")
def admin_index():
    """Renders admin dashboard with statistics and recent appointments."""
    today = datetime.now().strftime("%A, %B %d")
    total_appointments = Appointment.query.count()
    completed_appointments = Appointment.query.filter_by(status="Completed").count()
    pending_appointments = total_appointments - completed_appointments
    stats = {
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "appointments": total_appointments,
        "completed": completed_appointments,
        "pending": pending_appointments
    }
    recent_appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).limit(5).all()
    return render_template("index.html", today=today, stats=stats, recent_appointments=recent_appointments)

@app.route("/admin/doctors")
@role_required("admin")
def admin_doctors():
    """Renders a paginated list of doctors."""
    page = request.args.get('page', 1, type=int)  
    doctors = paginate_query(Doctor.query, page)
    
    return render_template("admin_doctors.html", doctors=doctors)

@app.route("/admin/doctor/new", methods=["GET", "POST"])
@role_required("admin")
def new_doctor():
    """Adds a new doctor to the system with a linked user account."""
    if request.method == "POST":
        username = request.form["username"].strip()
        if User.query.filter_by(username=username).first():
            flash(f"Doctor with username '{username}' already exists", "danger")
            return render_template("doctor_new.html")

        user = User(
            username=username,
            password=generate_password_hash(request.form["password"]),
            role="doctor")
        db.session.add(user)
        db.session.commit()

        doctor = Doctor(
            user_id=user.id,
            name=request.form["name"],
            specialization=request.form["specialization"],
            phone=request.form["phone"])
        db.session.add(doctor)
        db.session.commit()

        log_action(User.query.get(session["user_id"]), f"Added new doctor {doctor.name}")

        flash(f"Doctor '{doctor.name}' added successfully", "success")
        return redirect(url_for("admin_doctors"))
    return render_template("doctor_new.html")

@app.route("/admin/doctor/edit/<int:doctor_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_doctor(doctor_id):
    """Edits an existing doctor's details."""
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == "POST":
        doctor.name = request.form["name"]
        doctor.specialization = request.form["specialization"]
        doctor.phone = request.form["phone"]
        db.session.commit()

        log_action(User.query.get(doctor.user_id), f"Edited patient {doctor.name}")
        flash("Doctor updated successfully", "success")
        return redirect(url_for("admin_doctors"))
    return render_template("doctor_edit.html", doctor=doctor)

@app.route("/admin/doctor/delete/<int:doctor_id>")
@role_required("admin")
def delete_doctor(doctor_id):
    """Deletes a doctor if they have no appointments or medical records."""
    doctor = Doctor.query.get_or_404(doctor_id)
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    has_records = False
    for appt in appointments:
        record = MedicalRecord.query.filter_by(appointment_id=appt.id).first()
        if record:  
            has_records = True
            break
    if appointments or has_records:
        flash("Cannot delete doctor because they have appointments or medical records.", "warning")

        return redirect(url_for("admin_doctors"))

    user = User.query.get_or_404(doctor.user_id)
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()

    log_action(User.query.get(session["user_id"]), f"Deleted doctor {doctor.name}")

    flash("Doctor deleted successfully", "success")
    return redirect(url_for("admin_doctors"))

@app.route("/admin/patients")
@role_required("admin")
def admin_patients():
    """Renders a paginated list of patients with optional search."""
    search_query = request.args.get('search', '', type=str) 
    page = request.args.get('page', 1, type=int)  
    patients_query = Patient.query
    if search_query:
        patients_query = patients_query.filter(Patient.name.ilike(f"%{search_query}%"))

    patients = paginate_query(patients_query, page)
    return render_template("admin_patients.html", patients=patients, search_query=search_query)

@app.route("/admin/patient/edit/<int:patient_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_patient(patient_id):
    """Edits an existing patient's details."""
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        patient.name = request.form["name"]
        patient.age = request.form["age"]
        patient.gender = request.form["gender"]
        patient.phone = request.form["phone"]
        db.session.commit()
        
        log_action(User.query.get(session["user_id"]), f"Updated patient {patient.name}")

        flash("Patient updated successfully.", "success")
        return redirect(url_for("admin_patients"))
    return render_template("admin_patient_edit.html", patient=patient)

@app.route("/admin/patient/delete/<int:patient_id>")
@role_required("admin")
def delete_patient(patient_id):
    """Deletes a patient if they have no appointments or medical records."""
    patient = Patient.query.get_or_404(patient_id)  
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()  
    has_records = False

    for appt in appointments:
        record = MedicalRecord.query.filter_by(appointment_id=appt.id).first()
        if record:
            has_records = True
            break
 
    if appointments or has_records:
        flash("Cannot delete patient because they have appointments or medical records.", "warning")
        return redirect(url_for("admin_patients"))

    user = User.query.get_or_404(patient.user_id)  
    db.session.delete(patient)  
    db.session.delete(user) 
    db.session.commit() 
    
    log_action(User.query.get(session["user_id"]), f"Deleted patient {patient.name}")

    flash("Patient deleted successfully", "success")
    return redirect(url_for("admin_patients"))

@app.route("/admin/audit")
@role_required("admin")
def admin_audit():
    """Displays a paginated audit log."""
    page = request.args.get('page', 1, type=int)  
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)  

    query_params = request.args.to_dict(flat=True)
    query_params.pop('page', None)  
    page_range = get_page_range(logs.page, logs.pages)

    return render_template("admin_audit.html", logs=logs, page_range=page_range, query_params=query_params)

def get_page_range(current_page, total_pages, visible_pages=5):
    half_range = visible_pages // 2
    # Calculate the start and end page numbers
    start_page = max(1, current_page - half_range)
    end_page = min(total_pages, current_page + half_range)
    # Adjust the range if the current page is near the start or the end
    if current_page - half_range < 1:
        end_page = min(total_pages, visible_pages)
    elif current_page + half_range > total_pages:
        start_page = max(1, total_pages - visible_pages + 1)

    return range(start_page, end_page + 1)

@app.route("/admin/clear_audit_log", methods=["GET", "POST"])
@role_required("admin")
def clear_audit_log():
    """Clears all audit log entries."""
    if request.method == "POST":
        try:
            AuditLog.query.delete()  
            db.session.commit()  
            flash("Audit log has been cleared successfully", "success")
        except Exception as e:
            db.session.rollback()  
            flash(f"An error occurred while clearing the audit log: {e}", "danger")
        return redirect(url_for("admin_audit"))

    return render_template("clear_audit_log.html")

# -------------------------------------------------
# DOCTOR ROUTES
# -------------------------------------------------
@app.route("/doctor/appointments")
@role_required("doctor")
def doctor_appointments():
    """Displays a paginated list of the doctor's appointments."""
    doctor = get_user("doctor")
    page = request.args.get('page', 1, type=int)

    appointments = Appointment.query.filter_by(
        doctor_id=doctor.id).order_by(Appointment.date.desc()).paginate(page=page, per_page=10, error_out=False)

    # Get today's date to compare with appointment date
    current_date = datetime.today().date()
   
    return render_template("doctor_appointments.html", appointments=appointments, doctor=doctor, current_date=current_date)

@app.route("/doctor/records")
@role_required("doctor")
def doctor_records():
    """Displays a paginated list of medical records for the logged-in doctor."""
    doctor = get_user("doctor")

    if not doctor:
        flash("Doctor profile not found", "danger")
        return redirect(url_for("index"))

    page = request.args.get('page', 1, type=int)

    records = MedicalRecord.query.join(Appointment).filter(
        Appointment.doctor_id == doctor.id).order_by(
        MedicalRecord.id.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template("doctor_records.html", records=records)

@app.route("/doctor/record/<int:appointment_id>", methods=["GET", "POST"])
@role_required("doctor")
def add_record(appointment_id):
    doctor = get_user("doctor")
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == "POST":
        # Add the medical record
        record = MedicalRecord(
            appointment_id=appointment.id,
            diagnosis=request.form["diagnosis"],
            prescription=request.form["prescription"])
        
        # Update the status of the appointment to "Completed"
        appointment.status = "Completed"

        db.session.add(record)
        db.session.commit()

        log_action(  
            User.query.get(session["user_id"]),
            f"Added medical record for appointment {appointment.id}")
        flash("Medical record added successfully", "success")
        return redirect(url_for("doctor_appointments"))

    return render_template("record_new.html", appointment=appointment)


@app.route("/doctor/record/edit/<int:record_id>", methods=["GET", "POST"])
@role_required("doctor")
def edit_medical_record(record_id):
    """Edits an existing medical record."""
    doctor = get_user("doctor")
    record = MedicalRecord.query.get_or_404(record_id)

    if request.method == "POST":
        record.diagnosis = request.form["diagnosis"]
        record.prescription = request.form["prescription"]
        db.session.commit()

        log_action(User.query.get(session["user_id"]), f"Updated medical record for appointment {record.appointment_id}")
        flash("Medical record updated successfully", "success")
        return redirect(url_for("doctor_appointments"))

    return render_template("record_edit.html", record=record)


@app.route("/doctor/patients", methods=["GET", "POST"])
@role_required("doctor")
def doctor_view_patient_list():
    """Displays a paginated list of patients with optional search for doctors."""
    doctor = get_user("doctor")
    page = request.args.get('page', 1, type=int)   
    query = request.args.get("search", "")  

    patients_query = Patient.query
    if query:
        patients_query = patients_query.filter(Patient.name.ilike(f"%{query}%"))

    patients = paginate_query(patients_query, page)
    
    return render_template("doctor_patients.html", patients=patients, search_query=query)

@app.route("/doctor/patient/<int:patient_id>")
@role_required("doctor")
def doctor_view_patient(patient_id):
    """Displays details and medical records of a specific patient for the doctor."""
    doctor = get_user("doctor")
    patient = Patient.query.get_or_404(patient_id)
   
    records = MedicalRecord.query.join(Appointment).filter(Appointment.patient_id == patient.id).all()
    return render_template("doctor_patient_detail.html", patient=patient, records=records)


# -------------------------------------------------
# PATIENT ROUTES
# -------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles patient registration."""
    if request.method == "POST":
        
        if User.query.filter_by(username=request.form["username"]).first():
            flash("Username already exists", "danger")
            return render_template("register.html")

        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            role="patient")
        db.session.add(user)
        db.session.commit()

        patient = Patient(
            user_id=user.id,
            name=request.form["name"],
            age=request.form["age"],
            gender=request.form["gender"],
            phone=request.form["phone"] )
        db.session.add(patient)
        db.session.commit()

        flash("Patient registered successfully", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/patient/index", methods=["GET", "POST"])
@role_required("patient")
def patient_index():
    """Displays and allows updating the patient's profile."""
    patient = get_user("patient") 
    
    if request.method == "POST":

        patient.name = request.form["name"]
        patient.age = request.form["age"]
        patient.gender = request.form["gender"]
        patient.phone = request.form["phone"]
        db.session.commit()

        log_action(User.query.get(session["user_id"]), "Updated patient profile")
        flash("Profile updated successfully", "success")
    
    return render_template("patient_profile.html", patient=patient)

@app.route("/patient/book", methods=["GET", "POST"])
@role_required("patient")
def book_appointment():
    """Allows a patient to book a new appointment with validation."""
    patient = get_user("patient")  
    if not patient:
        abort(400, description="Patient profile not found.")
    
    doctors = Doctor.query.all()
    today_str = date.today().isoformat() 
    
    if request.method == "POST":
        valid, error_msg = validate_appointment_date_time(request.form["date"], request.form["time"])
        if not valid:
            flash(error_msg, "danger")
            return redirect(request.url)
        
        appt_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        appt_time = datetime.strptime(request.form["time"], "%H:%M").time()

        # Check if the appointment is in the future (if so, set status to 'Pending')
        status = "Pending" if appt_date >= date.today() else "Completed"

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=int(request.form["doctor_id"]),
            date=appt_date,
            time=appt_time,
            status=status)
        
        db.session.add(appointment)
        db.session.commit()

        log_action(User.query.get(session["user_id"]), f"Booked appointment for patient {patient.name}")

        flash("Appointment booked successfully", "success")
        return redirect(url_for("patient_appointments"))
    
    return render_template("appointment_new.html", doctors=doctors, today=today_str)


@app.route("/patient/appointments")
@role_required("patient")
def patient_appointments():
    """Displays a paginated list of the patient's appointments."""
    patient = get_user("patient")
    page = request.args.get('page', 1, type=int)

    # Get today's date to compare with appointment date
    current_date = datetime.today().date()
    current_time = datetime.now().time()  # This is the current time (e.g., 14:45)

    # Update appointments that are past due to "Completed"
    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date < current_date,
        Appointment.status == "Pending"  # Only update appointments that are pending
    ).all()

    # Commit changes to the database
    db.session.commit()

    # Get appointments for the patient
    appointments = Appointment.query.filter_by(
        patient_id=patient.id).order_by(Appointment.date.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template("patient_appointments.html", appointments=appointments, patient=patient, current_date=current_date, current_time=current_time)

@app.route("/patient/appointment/edit/<int:appointment_id>", methods=["GET", "POST"])
@role_required("patient")
def edit_appointment(appointment_id):
    """Edits an existing patient appointment."""
    patient = get_user("patient") 
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        abort(403)
    
    doctors = Doctor.query.all()
    today_str = date.today().isoformat() 
    
    if request.method == "POST":

        valid, error_msg = validate_appointment_date_time(request.form["date"], request.form["time"])
        if not valid:
            flash(error_msg, "danger")
            return redirect(request.url)

        appointment.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        appointment.time = datetime.strptime(request.form["time"], "%H:%M").time()
        appointment.doctor_id = int(request.form["doctor_id"])
        
        db.session.commit()

        log_action(User.query.get(session["user_id"]), f"Updated appointment {appointment.id} for patient {patient.name}")
        
        flash("Appointment updated successfully", "success")
        return redirect(url_for("patient_appointments"))
    
    return render_template(
        "appointment_edit.html", appointment=appointment, doctors=doctors, today=today_str)


@app.route("/patient/appointment/cancel/<int:appointment_id>")
@role_required("patient")
def cancel_appointment(appointment_id):
    """Cancels an appointment if no medical record exists."""
    appointment = Appointment.query.get_or_404(appointment_id)
    record = MedicalRecord.query.filter_by(appointment_id=appointment.id).first()

    if record:
        flash("Cannot cancel this appointment because it has a medical record", "warning")
        return redirect(url_for("patient_appointments"))

    db.session.delete(appointment)
    db.session.commit()

    log_action(User.query.get(session["user_id"]), f"Canceled appointment {appointment.id}")
    
    flash("Appointment canceled successfully", "success")
    return redirect(url_for("patient_appointments"))



@app.route("/patient/records")
@role_required("patient")
def patient_records():
    """Displays a paginated list of a patient's medical records with optional search."""
    patient = get_user("patient")

    search = request.args.get('search', '').strip()  
    page = request.args.get('page', 1, type=int)  

    query = (
        MedicalRecord.query
        .join(Appointment, MedicalRecord.appointment_id == Appointment.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.patient_id == patient.id))
    
    if search:
        query = query.filter(
            Doctor.name.ilike(f'%{search}%') |  
            MedicalRecord.diagnosis.ilike(f'%{search}%'))
        

    records = query.order_by(Appointment.date.desc()).paginate(page=page, per_page=10)

    return render_template("patient_records.html", records=records)

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8080)




