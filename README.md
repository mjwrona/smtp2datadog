# SMTP to Datadog

A lightweight Python SMTP server that receives emails and forwards their content to Datadog's logs API.

Perfect for monitoring application emails, or creating email-based logging pipelines.

## Quick Start

```bash
# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the server
DATADOG_API_KEY=your_api_key_here python3 smtp2datadog.py

# In another terminal, send a test email
python3 send_test_email.py
```

## Features

- Asynchronous SMTP server using aiosmtpd
- Parses incoming emails (subject, body, headers)
- Sends structured logs to Datadog Logs API
- Configurable via environment variables
- Handles both plain text and multipart emails
- Test script included

## Installation

1. Clone this repository

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Configuration is done via environment variables:

- `DATADOG_API_KEY`: Your Datadog API key (required)
- `DATADOG_SITE`: Your Datadog site (default: datadoghq.com)
  - US1: `datadoghq.com`
  - US3: `us3.datadoghq.com`
  - US5: `us5.datadoghq.com`
  - EU: `datadoghq.eu`
  - AP1: `ap1.datadoghq.com`
- `SERVICE_NAME`: Service name for tagging logs (default: smtp2datadog)
- `SMTP_HOST`: Host to bind the SMTP server (default: localhost)
- `SMTP_PORT`: Port for the SMTP server (default: 1025)

See `.env.example` for reference.

## Usage

### Running the server

**Linux/macOS:**
```bash
# Export environment variable
export DATADOG_API_KEY=your_api_key_here
python3 smtp2datadog.py

# Or inline
DATADOG_API_KEY=your_api_key_here python3 smtp2datadog.py
```

**Windows (Command Prompt):**
```cmd
set DATADOG_API_KEY=your_api_key_here
python smtp2datadog.py
```

**Windows (PowerShell):**
```powershell
$env:DATADOG_API_KEY="your_api_key_here"
python smtp2datadog.py
```

### Sending test emails

Use the included test script:

```bash
python3 send_test_email.py
```

Or send emails manually using the `swaks` tool:
```bash
swaks --to test@example.com \
      --from sender@example.com \
      --server localhost:1025 \
      --header "Subject: Test Email" \
      --body "This is a test message"
```

## Log Format

Emails are sent to Datadog with the following structure:

```json
{
  "ddsource": "smtp",
  "ddtags": "service:smtp2datadog,env:production",
  "hostname": "client-hostname",
  "message": "Email from sender@example.com: Subject Line",
  "email": {
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Subject Line",
    "body": "Email body content",
    "date": "Mon, 25 Oct 2025 12:00:00 +0000",
    "recipients": ["recipient@example.com"],
    "mail_from": "sender@example.com"
  },
  "timestamp": "2025-10-25T12:00:00.000000Z"
}
```

## Viewing Logs in Datadog

1. Go to Datadog Logs Explorer
2. Filter by `source:smtp` or `service:smtp2datadog`
3. You can create custom facets on the `email.*` fields for better filtering

## Security

**This server has NO authentication.**

- By default, the server binds to `localhost` and is only accessible from the local machine

## Use Case

- Converting application emails to Datadog logs for centralized monitoring

## License

MIT
