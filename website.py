from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to get appointment details from the database
def get_appointments_data():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()

    # Total appointments booked
    c.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = c.fetchone()[0]

    # Completed appointments
    c.execute("SELECT COUNT(*) FROM appointments WHERE status = 'completed'")
    completed_appointments = c.fetchone()[0]

    # Pending appointments
    c.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'")
    pending_appointments = c.fetchone()[0]

    # Doctor availability
    c.execute("SELECT doctor_available FROM appointments LIMIT 1")
    doctor_availability = c.fetchone()[0]

    conn.close()

    return total_appointments, completed_appointments, pending_appointments, doctor_availability

@app.route('/')
def index():
    total_appointments, completed_appointments, pending_appointments, doctor_availability = get_appointments_data()

    doctor_status = "Yes" if doctor_availability else "No"

    return render_template('index.html', total_appointments=total_appointments,
                           completed_appointments=completed_appointments,
                           pending_appointments=pending_appointments,
                           doctor_status=doctor_status)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)












