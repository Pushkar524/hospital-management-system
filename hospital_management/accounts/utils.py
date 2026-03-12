import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = "pushkarrajpurohit141@gmail.com"
GMAIL_APP_PASSWORD = "rnplmobtxfvrhvrw"  # Spaces removed


def send_notification(action: str, email: str, **kwargs):
    """Send notification via Gmail SMTP.
    Never crash the main app if the email service fails."""
    try:
        # Handle different notification types with additional context
        if action == "SIGNUP_WELCOME":
            subject = "Welcome to Hospital Management System!"
            body = f"Hello!\n\nWelcome to HMS! Your account ({email}) has been successfully created.\n\nYou can now log in and start using the system.\n\nBest regards,\nHMS Team"
        
        elif action == "BOOKING_CONFIRMATION_PATIENT":
            doctor_name = kwargs.get('doctor_name', 'Doctor')
            date = kwargs.get('date', '')
            time = kwargs.get('time', '')
            subject = "Appointment Booking Confirmed"
            body = f"Hello!\n\nYour appointment has been successfully confirmed.\n\nDetails:\n- Doctor: Dr. {doctor_name}\n- Date: {date}\n- Time: {time}\n\nPlease check your dashboard for more information.\n\nBest regards,\nHMS Team"
        
        elif action == "BOOKING_CONFIRMATION_DOCTOR":
            patient_name = kwargs.get('patient_name', 'Patient')
            date = kwargs.get('date', '')
            time = kwargs.get('time', '')
            subject = "New Appointment Booking"
            body = f"Hello Doctor!\n\nA new appointment has been booked with you.\n\nDetails:\n- Patient: {patient_name}\n- Date: {date}\n- Time: {time}\n\nPlease check your dashboard for more information.\n\nBest regards,\nHMS Team"
        
        else:
            return
        
        messages = {
            "subject": subject,
            "body": body
        }
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = email
        msg['Subject'] = messages['subject']
        msg.attach(MIMEText(messages['body'], 'plain'))
        
        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
            
        print(f"✅ Email sent successfully to {email} - {action}")
        
    except Exception as e:
        # Don't crash the app if email fails
        print(f"⚠️ Email sending failed: {str(e)}")
        pass
