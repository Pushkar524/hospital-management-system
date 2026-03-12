"""
Google Calendar Integration for HMS
Requires credentials.json from Google Cloud Console
"""
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# If modifying these scopes, delete token.pkl
SCOPES = ['https://www.googleapis.com/auth/calendar']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.pkl')


def get_calendar_service():
    """Get authenticated Google Calendar service."""
    creds = None
    
    # Check if token.pkl exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials are invalid or don't exist, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("⚠️ credentials.json not found. Skipping Google Calendar sync.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)


def add_appointment_to_calendar(booking):
    """
    Add a booking to Google Calendar.
    
    Args:
        booking: Booking object with slot, doctor, and patient info
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        service = get_calendar_service()
        if not service:
            return False
        
        # Combine date and time
        start_datetime = datetime.combine(booking.slot.date, booking.slot.start_time)
        end_datetime = datetime.combine(booking.slot.date, booking.slot.end_time)
        
        # Format for Google Calendar (ISO 8601)
        start_iso = start_datetime.isoformat()
        end_iso = end_datetime.isoformat()
        
        # Create event
        event = {
            'summary': f'Appointment with Dr. {booking.doctor.get_full_name() or booking.doctor.username}',
            'description': f'Patient: {booking.patient.get_full_name() or booking.patient.username}\\nPatient Email: {booking.patient.email}',
            'start': {
                'dateTime': start_iso,
                'timeZone': 'Asia/Kolkata',  # Change to your timezone
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [
                {'email': booking.patient.email},
                {'email': booking.doctor.email},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        # Insert event
        event_result = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'  # Send email notifications to attendees
        ).execute()
        
        print(f"✅ Google Calendar event created: {event_result.get('htmlLink')}")
        return True
        
    except HttpError as error:
        print(f"⚠️ Google Calendar API error: {error}")
        return False
    except Exception as e:
        print(f"⚠️ Google Calendar sync failed: {str(e)}")
        return False
