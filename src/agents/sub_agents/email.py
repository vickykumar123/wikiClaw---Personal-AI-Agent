# ============================================
# EMAIL SUB-AGENT - Handles sending emails
# ============================================

from typing import List

from agents.base import BaseSubAgent
from agent.llm import OllamaClient
from integrations.google.gmail import GmailClient
from tools.base import BaseTool
from tools.email import SendEmailTool

import logging

logger = logging.getLogger(__name__)


EMAIL_AGENT_PROMPT = """You are an email agent.

Your job is to send emails on behalf of the user.

You have this tool:
- send_email: Send an email with recipient (to), subject, and body

IMPORTANT:
- Extract email address, subject, and body from the task
- Call send_email ONCE with all the information
- After the tool returns, IMMEDIATELY confirm the email was sent
- Do NOT call the tool multiple times
- Be concise - just confirm what was done
- Do NOT use markdown formatting - use plain text only"""


class EmailAgent(BaseSubAgent):
    """Sub-agent for handling email sending."""

    def __init__(
        self,
        llm_client: OllamaClient,
        gmail_client: GmailClient
    ):
        super().__init__(llm_client)
        logger.debug(f"EmailAgent initialized with llm_client={llm_client}, gmail_client={gmail_client}")
        self.gmail = gmail_client

    @property
    def name(self) -> str:
        return "email_agent"

    @property
    def description(self) -> str:
        return (
            "Sends emails via Gmail. "
            "Use this when user asks to send an email, "
            "compose a message, or contact someone via email."
        )

    @property
    def system_prompt(self) -> str:
        logger.debug("Accessed system_prompt")
        return EMAIL_AGENT_PROMPT

    def get_tools(self) -> List[BaseTool]:
        logger.debug("Entering get_tools")
        try:
            tools = [
                SendEmailTool(gmail_client=self.gmail)
            ]
            tool_names = [type(t).__name__ for t in tools]
            logger.debug(f"Returning tools: {tool_names}")
            return tools
        except Exception as e:
            logger.error("Error in get_tools", exc_info=True)
            raise
