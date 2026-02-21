# ============================================
# AGENT CORE - Main agent with hierarchical sub-agents
# ============================================

import logging
from typing import List, Optional, Dict

from agent.llm import OllamaClient
from integrations.base import Message
from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient
from schemas.message import MessageSchema
from integrations.google.calendar import GoogleCalendarClient
from integrations.google.gmail import GmailClient
from constants import MAX_RECENT_MESSAGES

from agents.orchestrator import Orchestrator
from agents.base import BaseSubAgent
from agents.sub_agents.memory import MemoryAgent
from agents.sub_agents.notes import NotesAgent
from agents.sub_agents.calendar import CalendarAgent
from agents.sub_agents.web import WebAgent
from agents.sub_agents.email import EmailAgent

logger = logging.getLogger(__name__)


class Agent:
    """
    Main agent that processes messages using hierarchical sub-agents.

    Coordinates between:
    - Orchestrator (decides which sub-agents to call)
    - Sub-agents (specialized agents for different tasks)
    - MongoDB (for conversation history)
    """

    def __init__(
        self,
        llm_client: OllamaClient,
        db: MongoDB,
        embeddings_client: EmbeddingsClient,
        calendar_client: Optional[GoogleCalendarClient] = None,
        gmail_client: Optional[GmailClient] = None
    ):
        """
        Initialize the agent.

        Args:
            llm_client: Ollama client for LLM calls
            db: MongoDB connection for storage
            embeddings_client: OpenAI embeddings client
            calendar_client: Google Calendar client (optional)
            gmail_client: Gmail client (optional)
        """
        self.llm = llm_client
        self.db = db
        self.embeddings = embeddings_client
        self.calendar = calendar_client
        self.gmail = gmail_client

    def _get_sub_agents(self, user_id: str) -> List[BaseSubAgent]:
        """
        Get available sub-agents for a user.

        Args:
            user_id: User identifier

        Returns:
            List of sub-agent instances
        """
        sub_agents = [
            MemoryAgent(
                llm_client=self.llm,
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=user_id
            ),
            NotesAgent(
                llm_client=self.llm,
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=user_id
            ),
            WebAgent(llm_client=self.llm)
        ]

        if self.calendar:
            sub_agents.append(
                CalendarAgent(
                    llm_client=self.llm,
                    calendar_client=self.calendar
                )
            )

        if self.gmail:
            sub_agents.append(
                EmailAgent(
                    llm_client=self.llm,
                    gmail_client=self.gmail
                )
            )

        return sub_agents

    async def process_message(self, message: Message) -> str:
        """
        Process an incoming message and generate response.

        This is the main entry point called by Telegram bot.

        Flow:
        1. Get recent messages from MongoDB
        2. Create sub-agents for this user
        3. Create orchestrator with sub-agents
        4. Process message through orchestrator
        5. Save messages to MongoDB

        Args:
            message: Incoming message from user

        Returns:
            Response text to send back
        """
        user_id = message.user_id
        chat_id = message.chat_id
        user_text = message.text

        logger.info(f"Processing message from {user_id}: {user_text[:50]}...")

        try:
            # 1. Get recent conversation history
            history = await self._get_conversation_history(user_id)

            # 2. Create sub-agents for this user
            sub_agents = self._get_sub_agents(user_id)

            # 3. Create orchestrator
            orchestrator = Orchestrator(
                llm_client=self.llm,
                sub_agents=sub_agents
            )

            # 4. Process through orchestrator
            response = await orchestrator.process(
                user_message=user_text,
                conversation_history=history
            )

            # 5. Save messages to MongoDB
            await self._save_message(user_id, chat_id, "user", user_text)
            await self._save_message(user_id, chat_id, "assistant", response)

            logger.info(f"Response generated for {user_id}")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def _get_conversation_history(
        self,
        user_id: str
    ) -> List[Dict]:
        """
        Get recent conversation history from MongoDB.

        Args:
            user_id: User identifier

        Returns:
            List of message dicts for LLM
        """
        try:
            messages = await self.db.get_messages(user_id, MAX_RECENT_MESSAGES)

            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

        except Exception as e:
            logger.warning(f"Failed to get history: {e}")
            return []

    async def _save_message(
        self,
        user_id: str,
        chat_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Save a message to MongoDB.

        Args:
            user_id: User identifier
            chat_id: Chat identifier
            role: 'user' or 'assistant'
            content: Message content
        """
        try:
            message = MessageSchema(
                user_id=user_id,
                chat_id=chat_id,
                role=role,
                content=content
            )
            await self.db.save_message(message)

        except Exception as e:
            logger.error(f"Failed to save message: {e}")

    async def clear_history(self, user_id: str) -> None:
        """
        Clear conversation history for a user.

        Args:
            user_id: User identifier
        """
        logger.info(f"Clear history requested for {user_id}")
