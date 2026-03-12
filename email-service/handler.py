import json


def send_email(event, context):
    """Lambda handler for sending email notifications."""
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
