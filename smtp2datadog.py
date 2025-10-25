#!/usr/bin/env python3
"""
SMTP to Datadog Logger

An SMTP server that receives emails and forwards their content to Datadog's logs API.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from typing import Any, Dict

import aiohttp
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPServer, Envelope, Session


class DatadogHandler:
    """Handler for sending logs to Datadog."""

    def __init__(self, api_key: str, site: str = "datadoghq.com"):
        """
        Initialize the Datadog handler.

        Args:
            api_key: Datadog API key
            site: Datadog site (e.g., datadoghq.com, datadoghq.eu)
        """
        self.api_key = api_key
        self.url = f"https://http-intake.logs.{site}/api/v2/logs"
        self.headers = {
            "DD-API-KEY": api_key,
            "Content-Type": "application/json",
        }

    async def send_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Send a log entry to Datadog.

        Args:
            log_data: Dictionary containing log data

        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, headers=self.headers, json=log_data, timeout=10
                ) as response:
                    if response.status == 202:
                        print(f"✓ Successfully sent log to Datadog")
                        return True
                    else:
                        text = await response.text()
                        print(
                            f"✗ Failed to send log to Datadog: {response.status} - {text}"
                        )
                        return False
        except Exception as e:
            print(f"✗ Error sending log to Datadog: {e}")
            return False


class SMTPToDatadogHandler:
    """SMTP handler that processes emails and sends them to Datadog."""

    def __init__(self, datadog_handler: DatadogHandler, service_name: str = "smtp2datadog"):
        """
        Initialize the SMTP handler.

        Args:
            datadog_handler: DatadogHandler instance
            service_name: Service name to tag logs with
        """
        self.datadog_handler = datadog_handler
        self.service_name = service_name

    async def handle_DATA(self, server: SMTPServer, session: Session, envelope: Envelope) -> str:
        """
        Handle incoming email data.

        Args:
            server: SMTP server instance
            session: SMTP session
            envelope: Email envelope

        Returns:
            SMTP response code
        """
        print(f"\n--- Received email ---")
        print(f"From: {envelope.mail_from}")
        print(f"To: {envelope.rcpt_tos}")

        try:
            # Parse the email
            msg = BytesParser(policy=policy.default).parsebytes(envelope.content)

            # Extract email components
            subject = msg.get("subject", "")
            from_addr = msg.get("from", envelope.mail_from)
            to_addrs = msg.get("to", ", ".join(envelope.rcpt_tos))
            date = msg.get("date", "")

            # Get email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = part.get_content()
                        break
                    elif content_type == "text/html" and not body:
                        body = part.get_content()
            else:
                body = msg.get_content()

            # Prepare log data for Datadog
            log_entry = {
                "ddsource": "smtp",
                "service": self.service_name,
                "ddtags": f"env:production",
                "hostname": session.host_name or "unknown",
                "message": f"Email from {from_addr}: {subject}",
                "email": {
                    "from": from_addr,
                    "to": to_addrs,
                    "subject": subject,
                    "body": body,
                    "date": date,
                    "recipients": envelope.rcpt_tos,
                    "mail_from": envelope.mail_from,
                },
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }

            print(f"Subject: {subject}")
            print(f"Body preview: {body[:100]}..." if len(body) > 100 else f"Body: {body}")

            # Send to Datadog
            await self.datadog_handler.send_log(log_entry)

            return "250 Message accepted for delivery"

        except Exception as e:
            print(f"✗ Error processing email: {e}")
            return "550 Error processing message"


async def main():
    """Main entry point."""
    # Get configuration from environment variables
    datadog_api_key = os.getenv("DATADOG_API_KEY")
    datadog_site = os.getenv("DATADOG_SITE", "datadoghq.com")
    service_name = os.getenv("SERVICE_NAME", "smtp2datadog")
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))

    if not datadog_api_key:
        print("Error: DATADOG_API_KEY environment variable is required")
        sys.exit(1)

    print(f"Starting SMTP to Datadog server...")
    print(f"SMTP Server: {smtp_host}:{smtp_port}")
    print(f"Datadog Site: {datadog_site}")
    print(f"Service Name: {service_name}")
    print(f"")

    # Initialize handlers
    datadog_handler = DatadogHandler(api_key=datadog_api_key, site=datadog_site)
    smtp_handler = SMTPToDatadogHandler(
        datadog_handler=datadog_handler, service_name=service_name
    )

    # Start SMTP server
    controller = Controller(
        smtp_handler,
        hostname=smtp_host,
        port=smtp_port,
    )

    controller.start()
    print(f"✓ SMTP server listening on {smtp_host}:{smtp_port}")
    print(f"Press Ctrl+C to stop\n")

    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        controller.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
