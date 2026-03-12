# Google Calendar Integration Setup

## Overview
The system now automatically adds appointments to Google Calendar and sends calendar invites to both doctor and patient.

## Features Added
✅ **Email Notifications**: Both doctor and patient receive emails when an appointment is booked
✅ **Google Calendar Sync**: Appointments automatically added to Google Calendar
✅ **Calendar Invites**: Both parties receive calendar event notifications

---

## Google Calendar Setup (Optional)

If you want to enable Google Calendar integration:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "HMS Calendar Integration")
3. Enable the **Google Calendar API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - User Type: External
   - Add your email as a test user
4. Application type: **Desktop app**
5. Name: "HMS Desktop Client"
6. Click "Create"
7. **Download the JSON file**
8. Rename it to `credentials.json`
9. Place it in: `D:\Task1\MHS\hospital_management\credentials.json`

### Step 3: First-Time Authorization

1. Make sure `credentials.json` is in the `hospital_management` folder
2. When someone books an appointment for the first time:
   - A browser window will open
   - Log in with your Google account
   - Grant calendar access
   - A `token.pkl` file will be created automatically
3. Future bookings will use the saved token

---

## Without Google Calendar Setup

The system works perfectly **without** Google Calendar:
- Emails are still sent to both doctor and patient ✅
- Bookings are saved to the database ✅
- The dashboard shows all appointments ✅
- Google Calendar sync is silently skipped (no errors)

---

## Testing Email Notifications

When a booking is made, **two emails** are sent:

**Patient Email:**
```
Subject: Appointment Booking Confirmed
Body: Your appointment has been successfully confirmed.
      Doctor: Dr. [Name]
      Date: [Date]
      Time: [Time]
```

**Doctor Email:**
```
Subject: New Appointment Booking
Body: A new appointment has been booked with you.
      Patient: [Name]
      Date: [Date]
      Time: [Time]
```

---

## Files Modified/Added

- `bookings/google_calendar.py` - Google Calendar integration logic
- `bookings/views.py` - Updated to send emails to both parties + calendar sync
- `accounts/utils.py` - Enhanced email notifications with context
- `GOOGLE_CALENDAR_SETUP.md` - This setup guide

---

## Troubleshooting

**"credentials.json not found"**
- This is normal if you haven't set up Google Calendar
- The system will skip calendar sync and continue working

**"Email sending failed"**
- Check Gmail app password in `accounts/utils.py`
- Verify 2FA is enabled on Gmail account

**"Google Calendar API error"**
- Make sure the API is enabled in Google Cloud Console
- Delete `token.pkl` and re-authenticate
- Check that test users are added in OAuth consent screen
