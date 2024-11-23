                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              clinic_management.py                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            import sqlite3
from datetime import datetime
import uuid
from twilio.rest import Client

# Twilio credentials (replace these with your own credentials)
ACCOUNT_SID = 'ACbd299c346a136d15c7c1776b9a09e501'
AUTH_TOKEN = '710d9f5c0976e9f278d999c3fc6a25af'
FROM_PHONE = '+19787189860'

# Function to connect to the database
def connect_db():
    conn = sqlite3.connect("appointments.db")
    return conn

# Function to create the appointments table if it doesn't exist
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_number TEXT PRIMARY KEY,
            patient_name TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            phone_number TEXT,
            amount REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to send SMS using Twilio
def send_sms(to, message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=FROM_PHONE,
        to=to
    )

# Function to generate a unique appointment number
def generate_appointment_number():
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:4].upper()
    return f"HOSP-{date_str}-{unique_id}"

# Book a new appointment
def book_appointment():
    print("Enter patient's details:")
    patient_name = input("Enter patient's name: ")
    appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
    appointment_time = input("Enter appointment time (HH:MM): ")
    phone_number = input("Enter patient's phone number: ")
    amount = float(input("Enter amount for the appointment in ₹: "))

    # Generate a unique appointment number
    appointment_number = generate_appointment_number()

    # Insert into the database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO appointments (appointment_number, patient_name, appointment_date, appointment_time, phone_number, amount, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (appointment_number, patient_name, appointment_date, appointment_time, phone_number, amount, 'Booked'))
    conn.commit()
    conn.close()

    # Generate and display the receipt on CLI
    print(f"\nAppointment booked successfully. Your appointment number is {appointment_number}.")
    print("\nReceipt:\n")
    print("=" * 50)
    print("                ** HOSPITAL RECEIPT **")
    print("=" * 50)
    print(f"Appointment Number : {appointment_number}")
    print(f"Doctor             : Dr. Rajesh Kumar")
    print(f"Patient Name       : {patient_name}")
    print(f"Appointment Date   : {appointment_date}")
    print(f"Appointment Time   : {appointment_time}")
    print(f"Consultation Fee   : ₹{amount:.2f}")
    print("=" * 50)
    print("            ** Thank you for choosing us! **")
    print("=" * 50)

    # Send SMS notification to the patient
    sms_message = f"Your appointment at Pragyan Clinic is confirmed.\nAppointment Number: {appointment_number}\nDoctor: Dr. Rajesh Kumar\nDate: {appointment_date}\nTime: {appointment_time}\nConsultation Fee: ₹{amount:.2f}\nThank you for choosing Pragyan Clinic!"
    send_sms(phone_number, sms_message)

# View all appointments
def view_all_appointments():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    patients = cursor.fetchall()
    conn.close()

    if patients:
        print("\nAppointments List:")
        for patient in patients:
            status = patient[6]
            print(f"Appointment Number: {patient[0]}, Patient Name: {patient[1]}, Date: {patient[2]}, Time: {patient[3]}, Phone: {patient[4]}, Status: {status}")
    else:
        print("No appointments found.")

# Cancel an appointment
def cancel_appointment():
    appointment_number = input("Enter appointment number to cancel: ")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_number = ?", (appointment_number,))
    patient = cursor.fetchone()

    if patient:
        cursor.execute("UPDATE appointments SET status = ? WHERE appointment_number = ?", ('Cancelled', appointment_number))
        conn.commit()
        conn.close()

        # Send SMS notification
        sms_message = f"Your appointment at Pragyan Clinic has been cancelled.\nAppointment Number: {appointment_number}"
        send_sms(patient[4], sms_message)
        print(f"Appointment {appointment_number} has been cancelled.")
    else:
        print(f"No appointment found with Appointment Number {appointment_number}.")

# Reschedule an appointment
def reschedule_appointment():
    appointment_number = input("Enter appointment number to reschedule: ")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_number = ?", (appointment_number,))
    patient = cursor.fetchone()

    if patient:
        new_time = input("Enter new time slot (HH:MM): ")
        cursor.execute("UPDATE appointments SET appointment_time = ?, status = ? WHERE appointment_number = ?", (new_time, 'Rescheduled', appointment_number))
        conn.commit()
        conn.close()

        # Send SMS notification
        sms_message = f"Your appointment at Pragyan Clinic has been rescheduled.\nAppointment Number: {appointment_number}\nNew Time: {new_time}"
        send_sms(patient[4], sms_message)
        print(f"Appointment {appointment_number} has been rescheduled.")
    else:
        print(f"No appointment found with Appointment Number {appointment_number}.")

# Complete an appointment
def complete_appointment():
    appointment_number = input("Enter appointment number to mark as completed: ")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_number = ?", (appointment_number,))
    patient = cursor.fetchone()

    if patient:
        cursor.execute("UPDATE appointments SET status = ? WHERE appointment_number = ?", ('Completed', appointment_number))
        conn.commit()
        conn.close()

        # Send SMS notification
        sms_message = f"Your appointment at Pragyan Clinic has been completed.\nAppointment Number: {appointment_number}\nThank you for visiting Pragyan Clinic!"
        send_sms(patient[4], sms_message)
        print(f"Appointment {appointment_number} has been marked as completed.")
    else:
        print(f"No appointment found with Appointment Number {appointment_number}.")

# Search Patient by Appointment Number and Complete Appointment Option
def search_patient_by_appointment_number():
    appointment_number = input("Enter appointment number to search: ")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_number = ?", (appointment_number,))
    patient = cursor.fetchone()
    conn.close()

    if patient:
        print("\nPatient Found:")
        print(f"Appointment Number: {patient[0]}")
        print(f"Patient Name: {patient[1]}")
        print(f"Appointment Date: {patient[2]}")
        print(f"Appointment Time: {patient[3]}")
        print(f"Phone Number: {patient[4]}")
        print(f"Amount: ₹{patient[5]:.2f}")
        print(f"Status: {patient[6]}")

        # Ask if the user wants to complete the appointment
        if patient[6] != 'Completed':
            complete_choice = input("Do you want to mark this appointment as completed? (yes/no): ").strip().lower()
            if complete_choice == 'yes':
                # Mark the appointment as completed
                complete_appointment()
        else:
            print(f"Appointment {appointment_number} is already completed.")
    else:
        print(f"No patient found with Appointment Number {appointment_number}.")

# Main menu
def main():
    create_tables()

    while True:
        print("\n1. Book New Appointment")
        print("2. View All Appointments")
        print("3. Cancel Appointment")
        print("4. Reschedule Appointment")
        print("5. Complete Appointment")
        print("6. Search Patient by Appointment Number")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            book_appointment()
        elif choice == '2':
            view_all_appointments()
        elif choice == '3':
            cancel_appointment()
        elif choice == '4':
            reschedule_appointment()
        elif choice == '5':
            complete_appointment()
        elif choice == '6':
            search_patient_by_appointment_number()
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()








































































































