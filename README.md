# 🏥 Mini Hospital Management System (HMS)

A full-stack web application built with **Django + PostgreSQL + Serverless (AWS Lambda)** that allows doctors to manage availability and patients to book appointments — with Google Calendar sync and automated email notifications.

---

## 📌 Project Overview

| Layer | Technology |
|---|---|
| Backend | Django (Python) |
| Database | PostgreSQL |
| Email Service | Serverless Framework (AWS Lambda - Python) |
| Calendar Integration | Google Calendar API |
| Auth | Django built-in auth (Custom User Model) |

---

## 🗂️ Full Project Structure

```
hospital_management/          ← Django root project
│
├── manage.py
│
├── hospital_management/      ← Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                 ← Custom User Model (Doctor & Patient)
│   ├── models.py             ← User model with role field
│   ├── views.py              ← Signup, Login, Logout
│   ├── forms.py              ← DoctorSignupForm, PatientSignupForm
│   └── urls.py
│
├── doctors/                  ← Doctor availability management
│   ├── models.py             ← Availability model
│   ├── views.py              ← Doctor dashboard, slot creation
│   └── urls.py
│
├── bookings/                 ← Appointment booking
│   ├── models.py             ← Booking model
│   ├── views.py              ← Book slot, view bookings
│   └── urls.py
│
└── templates/                ← HTML templates
    ├── base.html
    ├── accounts/
    │   ├── doctor_signup.html
    │   ├── patient_signup.html
    │   └── login.html
    ├── doctors/
    │   └── dashboard.html
    └── bookings/
        └── patient_dashboard.html

email-service/                ← Separate Serverless project
├── handler.py                ← Lambda function
├── serverless.yml            ← Serverless config
└── requirements.txt
```

---

## ⚙️ Step-by-Step Setup Instructions

### Step 1 — Install Required Software

```bash
# Python packages
pip install django psycopg2-binary requests

# Google API
pip install google-api-python-client google-auth google-auth-oauthlib

# Serverless (Node.js required)
npm install -g serverless
npm install -g serverless-offline
```

---

### Step 2 — Create the Django Project

```bash
django-admin startproject hospital_management
cd hospital_management

python manage.py startapp accounts
python manage.py startapp doctors
python manage.py startapp bookings
```

Register all apps in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'accounts',
    'doctors',
    'bookings',
]
```

---

### Step 3 — Configure PostgreSQL

Create the database:

```bash
createdb hospital_db
```

Update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hospital_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Run initial migrations:

```bash
python manage.py migrate
```

---

### Step 4 — Custom User Model

**`accounts/models.py`**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
```

**`settings.py`** — add this line:

```python
AUTH_USER_MODEL = 'accounts.User'
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

> ⚠️ IMPORTANT: `AUTH_USER_MODEL` must be set **before** the first `migrate`. If the project already has migrations, you must reset them.

---

### Step 5 — Authentication (Signup / Login / Logout)

**`accounts/forms.py`** — Create separate signup forms for doctors and patients.

During doctor signup, set:
```python
user.role = "doctor"
```

During patient signup, set:
```python
user.role = "patient"
```

Django automatically hashes passwords — never store plain text.

**URLs needed:**
- `/accounts/doctor/signup/`
- `/accounts/patient/signup/`
- `/accounts/login/`
- `/accounts/logout/`

---

### Step 6 — Doctor Availability Model

**`doctors/models.py`**

```python
from django.db import models
from accounts.models import User

class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr.{self.doctor.username} | {self.date} | {self.start_time}-{self.end_time}"
```

Run migrations:

```bash
python manage.py makemigrations doctors
python manage.py migrate
```

---

### Step 7 — Booking Model

**`bookings/models.py`**

```python
from django.db import models
from accounts.models import User
from doctors.models import Availability

class Booking(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_bookings')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_bookings')
    slot = models.ForeignKey(Availability, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} → Dr.{self.doctor.username} on {self.slot.date}"
```

Run migrations:

```bash
python manage.py makemigrations bookings
python manage.py migrate
```

---

### Step 8 — Doctor Dashboard (View + Template)

**Route:** `/doctor/dashboard/`

**What it does:**
- Shows the logged-in doctor's available and booked slots
- Form to add new availability slots (date, start time, end time)

**View logic:**
```python
# Only show the current doctor's slots
slots = Availability.objects.filter(doctor=request.user)
```

**Access control:** Restrict this view so only users with `role == "doctor"` can access it.

---

### Step 9 — Patient Dashboard

**Route:** `/patient/dashboard/`

**What it does:**
- Lists all doctors
- Shows available (unbooked) future slots

**Query to get available slots:**

```python
from datetime import date

slots = Availability.objects.filter(
    is_booked=False,
    date__gte=date.today()
).select_related('doctor')
```

Display per slot:
- Doctor name
- Date
- Start time – End time
- "Book" button (POST form with `slot_id`)

---

### Step 10 — Booking Logic (Critical — Prevents Double Booking)

**`bookings/views.py`**

```python
from django.shortcuts import get_object_or_404, redirect
from doctors.models import Availability
from bookings.models import Booking

def book_slot(request, slot_id):
    if request.method == "POST":
        try:
            # Only get the slot if it is NOT already booked
            slot = Availability.objects.get(id=slot_id, is_booked=False)

            Booking.objects.create(
                doctor=slot.doctor,
                patient=request.user,
                slot=slot
            )

            # Mark slot as booked so no one else can book it
            slot.is_booked = True
            slot.save()

            # TODO: Trigger email notification here (Step 14)
            # TODO: Trigger Google Calendar event here (Step 11)

        except Availability.DoesNotExist:
            # Slot was already booked by someone else
            pass

    return redirect('patient_dashboard')
```

> ⚠️ For production, wrap this in `select_for_update()` inside a database transaction to handle race conditions.

---

### Step 11 — Google Calendar Integration

#### Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Calendar API**
4. Create **OAuth 2.0 credentials** → Download as `credentials.json`
5. Place `credentials.json` in the Django project root

#### Install:
```bash
pip install google-api-python-client google-auth google-auth-oauthlib
```

#### Integration code (call this after a booking is confirmed):

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

def add_to_google_calendar(booking):
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('calendar', 'v3', credentials=creds)

    start_dt = datetime.combine(booking.slot.date, booking.slot.start_time).isoformat()
    end_dt = datetime.combine(booking.slot.date, booking.slot.end_time).isoformat()

    event = {
        'summary': f'Appointment with Dr. {booking.doctor.get_full_name()}',
        'description': f'Patient: {booking.patient.get_full_name()}',
        'start': {'dateTime': start_dt, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_dt, 'timeZone': 'Asia/Kolkata'},
    }

    service.events().insert(calendarId='primary', body=event).execute()
```

---

### Step 12 — Serverless Email Service

Create a separate folder **outside** the Django project:

```bash
mkdir email-service
cd email-service
serverless create --template aws-python
```

**`handler.py`**

```python
import json

def send_email(event, context):
    body = event.get('body')
    if isinstance(body, str):
        body = json.loads(body)

    action = body.get('action')
    email = body.get('email')

    messages = {
        "SIGNUP_WELCOME": f"Welcome to HMS! Your account ({email}) has been created.",
        "BOOKING_CONFIRMATION": f"Your appointment has been confirmed. Check your calendar.",
    }

    message = messages.get(action, "Notification from HMS")

    # TODO: Replace with real email sending (SES, SendGrid, etc.)
    print(f"Sending to {email}: {message}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": message})
    }
```

**`serverless.yml`**

```yaml
service: email-service

provider:
  name: aws
  runtime: python3.9
  stage: dev
  region: us-east-1

functions:
  sendEmail:
    handler: handler.send_email
    events:
      - http:
          path: send_email
          method: post
          cors: true

plugins:
  - serverless-offline
```

---

### Step 13 — Run Serverless Locally

```bash
cd email-service
serverless offline
```

The local API will be available at:

```
POST http://localhost:3000/dev/send_email
```

Test with curl:

```bash
curl -X POST http://localhost:3000/dev/send_email \
  -H "Content-Type: application/json" \
  -d '{"action": "SIGNUP_WELCOME", "email": "test@example.com"}'
```

---

### Step 14 — Connect Django to Email Service

Add this helper function in a `utils.py` file:

```python
import requests

EMAIL_SERVICE_URL = "http://localhost:3000/dev/send_email"

def send_notification(action: str, email: str):
    try:
        requests.post(
            EMAIL_SERVICE_URL,
            json={"action": action, "email": email},
            timeout=5
        )
    except requests.exceptions.RequestException:
        pass  # Don't crash the main app if email service is down
```

**After signup (in `accounts/views.py`):**

```python
from .utils import send_notification

send_notification("SIGNUP_WELCOME", user.email)
```

**After booking (in `bookings/views.py`):**

```python
from accounts.utils import send_notification

send_notification("BOOKING_CONFIRMATION", request.user.email)
```

---

## 🗄️ Database Schema (ER Overview)

```
User (accounts_user)
  id, username, email, password, role (doctor | patient)
        |
        |──── Availability (doctors_availability)
        |       id, doctor_id (FK→User), date, start_time, end_time, is_booked
        |
        └──── Booking (bookings_booking)
                id, doctor_id (FK→User), patient_id (FK→User), slot_id (FK→Availability), created_at
```

---

## 🚀 Running the Full System

### Terminal 1 — Django Backend
```bash
cd hospital_management
python manage.py runserver
```
Runs at: `http://localhost:8000`

### Terminal 2 — Serverless Email Service
```bash
cd email-service
serverless offline
```
Runs at: `http://localhost:3000`

---

## ✅ Demo Checklist

| # | Action | Expected Result |
|---|---|---|
| 1 | Show project structure | Both folders visible |
| 2 | Run Django server | `localhost:8000` responds |
| 3 | Run serverless offline | `localhost:3000` responds |
| 4 | Doctor signup | Account created with `role=doctor` |
| 5 | Doctor adds availability | Slots saved to DB |
| 6 | Patient signup | Account created with `role=patient` |
| 7 | Patient books a slot | Booking record created |
| 8 | Slot becomes unavailable | `is_booked=True`, hidden from others |
| 9 | Booking visible in both dashboards | Doctor & Patient can see it |
| 10 | Email notification triggered | Lambda function logs/sends email |

---

## 🔑 Key Implementation Notes for Copilot

- Use **`@login_required`** decorator on all dashboard views
- Use a custom decorator or mixin to check `request.user.role` before granting access
- The `Booking` model has **two ForeignKeys to the same `User` model** — use `related_name` to avoid clashes (`doctor_bookings`, `patient_bookings`)
- Always use **`select_related('doctor')`** when querying `Availability` to avoid N+1 queries
- The `send_notification()` function must **never crash the main app** — wrap in try/except
- Google Calendar `token.json` is generated on first OAuth login — handle the refresh token flow

---

## 📦 Full Requirements

**`requirements.txt` (Django project)**
```
django
psycopg2-binary
requests
google-api-python-client
google-auth
google-auth-oauthlib
```

**`email-service/requirements.txt`**
```
# No extra packages needed for basic handler
# Add boto3 if using AWS SES for real email sending
```
