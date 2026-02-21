# ============================================
# GMAIL - Email sending client
# ============================================

import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class GmailClient:
    """
    Client for sending emails via Gmail API.

    Uses the same credentials as Google Calendar.
    """

    def __init__(self, credentials):
        """
        Initialize Gmail client.

        Args:
            credentials: Google OAuth credentials (from Calendar client)
        """
        self.creds = credentials
        self.service = None

        if self.creds:
            self._build_service()

    def _build_service(self):
        """Build the Gmail service."""
        try:
            self.service = build("gmail", "v1", credentials=self.creds)
            logger.info("Gmail service initialized")
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> Optional[dict]:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: If True, body is treated as HTML

        Returns:
            Sent message data or None if failed
        """
        if not self.service:
            logger.error("Gmail service not initialized")
            return None

        try:
            # Create message
            if html:
                message = MIMEMultipart("alternative")
                message.attach(MIMEText(body, "html"))
            else:
                message = MIMEText(body)

            message["to"] = to
            message["subject"] = subject

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send
            result = self.service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()

            logger.info(f"Email sent to {to}, message ID: {result.get('id')}")
            return result

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return None
