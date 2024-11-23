from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth
import sqlite3
import hashlib

app = Flask(__name__)
auth = HTTPBasicAuth()

# Hardcoded credentials
ADMIN_USERNAME = "pragyan"
ADMIN_PASSWORD = "pragyan"

# SQLite DB path
DB_PATH = "appointments.db"

# Function to authenticate using basic credentials
@auth.verify_password
def authenticate_user(username, password):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return False
    return True

# Function to connect to SQLite DB
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

# Create appointments table if it doesn't exist
def create_appointments_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_number TEXT PRIMARY KEY,
            patient_name TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            phone_number TEXT,
            amount REAL,
            status TEXT,
            doctor_available INTEGER
        )
    """)
    conn.commit()

# Create users table for credentials (optional)
def create_users_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()

# Create initial admin user
def create_admin_user():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (ADMIN_USERNAME,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (ADMIN_USERNAME, hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()))
        conn.commit()

# Initialize tables and create the admin user
create_appointments_table()
create_users_table()
create_admin_user()

@app.route("/appointments", methods=["GET"])
@auth.login_required
def get_appointments():
    """Get all appointments"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()
    return jsonify([dict(appointment) for appointment in appointments])

@app.route("/appointments", methods=["POST"])
@auth.login_required
def create_appointment():
    """Create a new appointment"""
    data = request.get_json()
    appointment_number = data.get("appointment_number")
    patient_name = data.get("patient_name")
    appointment_date = data.get("appointment_date")
    appointment_time = data.get("appointment_time")
    phone_number = data.get("phone_number")
    amount = data.get("amount", 0.0)
    status = data.get("status", "Scheduled")
    doctor_available = data.get("doctor_available", 1)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (appointment_number, patient_name, appointment_date,
        appointment_time, phone_number, amount, status, doctor_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (appointment_number, patient_name, appointment_date, appointment_time, phone_number, amount, status, doctor_available))
    conn.commit()
    return jsonify({"message": "Appointment created successfully"})

@app.route("/appointments/<appointment_number>", methods=["PUT"])
@auth.login_required
def update_appointment(appointment_number):
    """Update the appointment status"""
    data = request.get_json()
    status = data.get("status")
    doctor_available = data.get("doctor_available")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments SET status = ?, doctor_available = ? WHERE appointment_number = ?
    """, (status, doctor_available, appointment_number))
    conn.commit()
    return jsonify({"message": f"Appointment {appointment_number} updated successfully"})

@app.route("/appointments/<appointment_number>", methods=["DELETE"])
@auth.login_required
def delete_appointment(appointment_number):
    """Delete an appointment"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE appointment_number = ?", (appointment_number,))
    conn.commit()
    return jsonify({"message": f"Appointment {appointment_number} deleted successfully"})

@app.route("/appointments/<appointment_number>", methods=["GET"])
@auth.login_required
def get_appointment(appointment_number):
    """Get a single appointment"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_number = ?", (appointment_number,))
    appointment = cursor.fetchone()
    if appointment is None:
        abort(404, description="Appointment not found")
    return jsonify(dict(appointment))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
