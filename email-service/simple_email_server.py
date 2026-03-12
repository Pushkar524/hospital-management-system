"""
Simple email service mock server - runs on port 3000
This replaces the serverless offline setup for local testing
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class EmailHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/dev/send_email':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            action = data.get('action')
            email = data.get('email')
            
            messages = {
                "SIGNUP_WELCOME": f"✅ Welcome to HMS! Your account ({email}) has been created.",
                "BOOKING_CONFIRMATION": f"✅ Your appointment has been confirmed for {email}. Check your calendar.",
            }
            
            message = messages.get(action, "Notification from HMS")
            
            # Print to console (simulates sending email)
            print(f"\n{'='*60}")
            print(f"📧 EMAIL SENT")
            print(f"{'='*60}")
            print(f"To: {email}")
            print(f"Action: {action}")
            print(f"Message: {message}")
            print(f"{'='*60}\n")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({"message": message})
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass


if __name__ == '__main__':
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, EmailHandler)
    print("🚀 Email Service running on http://localhost:3000")
    print("📬 Listening for notifications on /dev/send_email")
    print("Press Ctrl+C to stop\n")
    httpd.serve_forever()
