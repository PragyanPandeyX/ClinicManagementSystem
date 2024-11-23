# Function to create the database and the `patients` table
def create_database():
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    # Create the `patients` table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            appointment_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            pincode TEXT,
            payment_mode TEXT,
            time_slot TEXT,
            amount REAL,
            status TEXT DEFAULT 'Booked'
        )
        """
    )

    # Create a table for managing available seats (if not exists)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS seats (
            total_seats INTEGER DEFAULT 50,
            available_seats INTEGER DEFAULT 50
        )
        """
    )

    # Initialize the seats table with default values if empty
    cursor.execute("SELECT COUNT(*) FROM seats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO seats (total_seats, available_seats) VALUES (50, 50)")

    conn.commit()
    conn.close()


# Function to book an appointment
def book_appointment(appointment_number, name, address, pincode, payment_mode, time_slot, amount):
    try:
        conn = sqlite3.connect("clinic.db")
        cursor = conn.cursor()

        # Check if seats are available
        cursor.execute("SELECT available_seats FROM seats")
        available_seats = cursor.fetchone()[0]
        if available_seats <= 0:
            return "No seats available for booking."

        # Insert new appointment
        cursor.execute(
            """
            INSERT INTO patients (appointment_number, name, address, pincode, payment_mode, time_slot, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (appointment_number, name, address, pincode, payment_mode, time_slot, amount),
        )

        # Reduce available seats by 1
        cursor.execute(
            "UPDATE seats SET available_seats = available_seats - 1 WHERE total_seats > 0"
        )

        conn.commit()
        conn.close()
        return None  # No error
    except sqlite3.IntegrityError:
        return "Duplicate appointment number. Try again."
    except Exception as e:
        return str(e)


# Function to view all appointments
def view_appointments():
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()
    return patients


# Function to cancel an appointment
def cancel_appointment(appointment_number):
    try:
        conn = sqlite3.connect("clinic.db")
        cursor = conn.cursor()

        # Update status to 'Cancelled'
        cursor.execute(
            "UPDATE patients SET status = 'Cancelled' WHERE appointment_number = ?",
            (appointment_number,),
        )

        # Check if the appointment was updated
        if cursor.rowcount == 0:
            return "Appointment not found."

        # Increase available seats by 1
        cursor.execute(
            "UPDATE seats SET available_seats = available_seats + 1 WHERE total_seats > 0"
        )

        conn.commit()
        conn.close()
        return None  # No error
    except Exception as e:
        return str(e)


# Function to reschedule an appointment
def reschedule_appointment(appointment_number, new_time_slot):
    try:
        conn = sqlite3.connect("clinic.db")
        cursor = conn.cursor()

        # Update the time slot
        cursor.execute(
            "UPDATE patients SET time_slot = ?, status = 'Rescheduled' WHERE appointment_number = ?",
            (new_time_slot, appointment_number),
        )

        # Check if the appointment was updated
        if cursor.rowcount == 0:
            return "Appointment not found."

        conn.commit()
        conn.close()
        return None  # No error
    except Exception as e:
        return str(e)


# Function to view available seats
def view_seats():
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute("SELECT total_seats, available_seats FROM seats")
    seats = cursor.fetchone()

    conn.close()
    return seats


# Function to search for a patient by appointment number
def search_patient(appointment_number):
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE appointment_number = ?", (appointment_number,)
    )
    patient = cursor.fetchone()

    conn.close()
    return patient
# Option 6: Search patient by appointment number
def search_patient_by_appointment_number():
    appointment_number = input("\nEnter appointment number to search: ").strip()  # Strip any extra spaces
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE appointment_number = ?", (appointment_number,))
    patient = cursor.fetchone()

    if patient:
        print(f"\nAppointment #{patient[0]}: {patient[1]} at {patient[5]}, Amount: ₹{patient[6]:.2f}, Status: {patient[7]}")
    else:
        print("\nNo patient found with that appointment number.")
    conn.close()








































































