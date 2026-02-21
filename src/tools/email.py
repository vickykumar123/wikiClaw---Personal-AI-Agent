# ============================================
# EMAIL TOOLS - Send emails via Gmail
# ============================================

import logging
from typing import Any, Dict

from tools.base import BaseTool, ToolResult
from integrations.google.gmail import GmailClient

logger = logging.getLogger(__name__)


class SendEmailTool(BaseTool):
    """Tool for sending emails via Gmail."""

    def __init__(self, gmail_client: GmailClient):
        self.gmail = gmail_client

    @property
    def name(self) -> str:
        return "send_email"

    @property
    def description(self) -> str:
        return (
            "Send an email to someone. "
            "Use this when the user asks to send an email, "
            "compose a message, or contact someone via email."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient's email address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content"
                }
            },
            "required": ["to", "subject", "body"]
        }

    async def execute(
        self,
        to: str,
        subject: str,
        body: str,
        **kwargs
    ) -> ToolResult:
        """Send an email."""
        try:
            logger.info(f"Sending email to {to}: {subject}")

            result = await self.gmail.send_email(
                to=to,
                subject=subject,
                body=body
            )

            if result:
                return ToolResult(
                    success=True,
                    data=f"Email sent successfully to {to}."
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error="Failed to send email"
                )

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
