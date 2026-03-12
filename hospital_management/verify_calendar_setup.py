"""
Google Calendar Integration Verification Script
Run this to verify everything is set up correctly
"""
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("Google Calendar Integration Setup Verification")
print("="*60)

# Check 1: Credentials file
credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
if os.path.exists(credentials_path):
    print("✅ credentials.json found")
    import json
    with open(credentials_path, 'r') as f:
        creds_data = json.load(f)
        if 'installed' in creds_data or 'web' in creds_data:
            print("✅ credentials.json format is valid")
        else:
            print("❌ credentials.json format is invalid")
else:
    print("❌ credentials.json NOT FOUND")
    print("   Place it in:", os.path.dirname(__file__))

# Check 2: Required packages
print("\nChecking required packages...")
packages_ok = True
try:
    import google.auth
    print("✅ google-auth installed")
except ImportError:
    print("❌ google-auth NOT installed")
    packages_ok = False

try:
    import google_auth_oauthlib
    print("✅ google-auth-oauthlib installed")
except ImportError:
    print("❌ google-auth-oauthlib NOT installed")
    packages_ok = False

try:
    import googleapiclient
    print("✅ google-api-python-client installed")
except ImportError:
    print("❌ google-api-python-client NOT installed")
    packages_ok = False

# Check 3: Module imports
print("\nChecking module imports...")
try:
    from bookings.google_calendar import get_calendar_service, add_appointment_to_calendar
    print("✅ google_calendar.py can be imported")
except Exception as e:
    print(f"❌ Error importing google_calendar.py: {e}")
    packages_ok = False

# Check 4: Django settings
try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management.settings')
    django.setup()
    print("✅ Django settings configured")
except Exception as e:
    print(f"❌ Django setup error: {e}")

# Final status
print("\n" + "="*60)
if packages_ok and os.path.exists(credentials_path):
    print("✅ GOOGLE CALENDAR INTEGRATION IS READY!")
    print("\nNext steps:")
    print("1. Book an appointment")
    print("2. Browser will open for Google authorization (first time only)")
    print("3. Grant calendar access")
    print("4. token.pkl will be created for future use")
else:
    print("❌ SETUP INCOMPLETE")
    print("\nMissing components:")
    if not os.path.exists(credentials_path):
        print("- credentials.json file")
    if not packages_ok:
        print("- Required Python packages")
print("="*60)
