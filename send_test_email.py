#!/usr/bin/env python3
"""
Send a test email to the SMTP server.
"""

import smtplib
from email.message import EmailMessage

# SMTP server configuration
SMTP_HOST = "localhost"
SMTP_PORT = 1025

# Create email message
msg = EmailMessage()
msg['Subject'] = 'Test Email from SMTP2Datadog'
msg['From'] = 'sender@example.com'
msg['To'] = 'recipient@example.com'
msg.set_content("""
This is a test email sent to the SMTP2Datadog server.

This email should appear in your Datadog logs with:
- source: smtp
- service: smtp2datadog

The email metadata and body will be structured in the log entry.
""")

# Send email
try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.send_message(msg)
    print(f"✓ Email sent successfully to {SMTP_HOST}:{SMTP_PORT}")
except Exception as e:
    print(f"✗ Failed to send email: {e}")
