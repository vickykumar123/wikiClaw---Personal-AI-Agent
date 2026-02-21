# ============================================
# AGENT CORE - Main agent logic with tool support
# ============================================

import logging
import json
from typing import List, Optional, Dict, Any

from agent.llm import OllamaClient, ChatResponse
from agent.prompts import build_messages
from integrations.base import Message
from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient
from schemas.message import MessageSchema
from tools.base import BaseTool
from tools.memory import SearchMemoryTool, SaveMemoryTool
from tools.notes import CreateNoteTool, SearchNotesTool, ListNotesTool, DeleteNoteTool
from tools.calendar import CreateEventTool, ListEventsTool, SearchEventsTool, DeleteEventTool
from tools.websearch import WebSearchTool, NewsSearchTool
from tools.email import SendEmailTool
from integrations.google.calendar import GoogleCalendarClient
from integrations.google.gmail import GmailClient
from constants import MAX_RECENT_MESSAGES

# Set up logging
logger = logging.getLogger(__name__)

# Maximum tool call iterations to prevent infinite loops
MAX_TOOL_ITERATIONS = 5


class Agent:
    """
    Main agent that processes messages and generates responses.

    Coordinates between:
    - LLM (for generating responses)
    - MongoDB (for conversation history)
    - Tools (for actions like memory search/save)
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

    def _get_tools_for_user(self, user_id: str) -> List[BaseTool]:
        """
        Get available tools for a user.

        Args:
            user_id: User identifier

        Returns:
            List of tool instances
        """
        tools = [
            # Memory tools
            SearchMemoryTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=user_id
            ),
            SaveMemoryTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=user_id
            ),
            # Notes tools
            CreateNoteTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=user_id
            ),
            SearchNotesTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=user_id
            ),
            ListNotesTool(
                db=self.db,
                user_id=user_id
            ),
            DeleteNoteTool(
                db=self.db,
                user_id=user_id
            )
        ]

        # Add calendar tools if client is available
        if self.calendar:
            tools.extend([
                CreateEventTool(calendar_client=self.calendar),
                ListEventsTool(calendar_client=self.calendar),
                SearchEventsTool(calendar_client=self.calendar),
                DeleteEventTool(calendar_client=self.calendar)
            ])

        # Web search tools (always available)
        tools.extend([
            WebSearchTool(),
            NewsSearchTool()
        ])

        # Email tool if Gmail client is available
        if self.gmail:
            tools.append(SendEmailTool(gmail_client=self.gmail))

        return tools

    async def process_message(self, message: Message) -> str:
        """
        Process an incoming message and generate response.

        This is the main entry point called by Telegram bot.

        Flow:
        1. Get recent messages from MongoDB
        2. Build prompt with available tools
        3. Call LLM with tools
        4. Execute any tool calls
        5. Loop until LLM returns final response
        6. Save messages to MongoDB

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
            # 1. Get recent conversation history (always - it's cheap)
            history = await self._get_conversation_history(user_id)

            # 2. Build initial messages
            messages = build_messages(
                user_message=user_text,
                conversation_history=history
            )

            # 3. Get tools for this user
            tools = self._get_tools_for_user(user_id)
            tool_schemas = [tool.to_schema() for tool in tools]
            tool_map = {tool.name: tool for tool in tools}

            # 4. Tool execution loop
            response = await self._run_tool_loop(messages, tool_schemas, tool_map)

            # 5. Save messages to MongoDB
            await self._save_message(user_id, chat_id, "user", user_text)
            await self._save_message(user_id, chat_id, "assistant", response)

            logger.info(f"Response generated for {user_id}")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def _run_tool_loop(
        self,
        messages: List[Dict[str, str]],
        tool_schemas: List[Dict[str, Any]],
        tool_map: Dict[str, BaseTool]
    ) -> str:
        """
        Run the tool execution loop.

        Keeps calling LLM and executing tools until:
        - LLM returns a response without tool calls
        - Max iterations reached

        Args:
            messages: Current message list
            tool_schemas: Tool schemas for LLM
            tool_map: Map of tool name to tool instance

        Returns:
            Final response text
        """
        iterations = 0
        executed_tools = set()  # Track executed tools to prevent duplicates

        while iterations < MAX_TOOL_ITERATIONS:
            iterations += 1
            logger.info(f"Tool loop iteration {iterations}/{MAX_TOOL_ITERATIONS}")

            # Call LLM with tools
            chat_response = await self.llm.chat_with_tools(
                messages=messages,
                tools=tool_schemas
            )

            logger.info(f"LLM response - finished: {chat_response.finished}, "
                       f"tool_calls: {len(chat_response.tool_calls)}, "
                       f"content: {chat_response.content[:100] if chat_response.content else 'None'}...")

            # If no tool calls, we're done
            if chat_response.finished:
                return chat_response.content

            # If LLM returned content with tool calls, it might be confused
            # After a few iterations, return whatever content we have
            if iterations >= 3 and chat_response.content:
                logger.warning("Multiple iterations with content, returning early")
                return chat_response.content

            # Execute tool calls
            logger.info(f"LLM requested {len(chat_response.tool_calls)} tool call(s)")

            # Build tool calls for assistant message
            tool_calls_for_message = []
            for tc in chat_response.tool_calls:
                tool_calls_for_message.append({
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments
                    }
                })

            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": chat_response.content or "",
                "tool_calls": tool_calls_for_message
            })

            # Execute each tool and add results
            for tool_call in chat_response.tool_calls:
                tool_name = tool_call.name
                tool_args = tool_call.arguments

                # Create a key to track duplicate calls
                tool_key = f"{tool_name}:{str(sorted(tool_args.items()) if tool_args else '')}"

                if tool_key in executed_tools:
                    logger.warning(f"Skipping duplicate tool call: {tool_name}")
                    messages.append({
                        "role": "tool",
                        "content": "Already executed this action."
                    })
                    continue

                executed_tools.add(tool_key)
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                if tool_name in tool_map:
                    tool = tool_map[tool_name]
                    result = await tool.execute(**tool_args)

                    # Add tool result to messages
                    result_content = str(result.data) if result.success else f"Error: {result.error}"
                    messages.append({
                        "role": "tool",
                        "content": result_content
                    })
                    logger.info(f"Tool result: {result_content[:100]}...")
                else:
                    logger.warning(f"Unknown tool: {tool_name}")
                    messages.append({
                        "role": "tool",
                        "content": f"Error: Unknown tool '{tool_name}'"
                    })

        # Max iterations reached
        logger.warning("Max tool iterations reached")
        return "I'm having trouble processing this request. Please try again."

    async def _get_conversation_history(
        self,
        user_id: str
    ) -> List[dict]:
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
        # TODO: Implement delete messages from MongoDB
        logger.info(f"Clear history requested for {user_id}")
