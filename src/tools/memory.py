# ============================================
# MEMORY TOOL - Search long-term memory
# ============================================

import logging
from typing import Any, Dict, List

from tools.base import BaseTool, ToolResult
from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient

logger = logging.getLogger(__name__)


class SearchMemoryTool(BaseTool):
    """
    Tool for searching user's long-term memory.

    Searches context stored in MongoDB using vector similarity.
    Returns relevant facts, preferences, and profile info.
    """

    def __init__(
        self,
        db: MongoDB,
        embeddings_client: EmbeddingsClient,
        user_id: str
    ):
        """
        Initialize memory search tool.

        Args:
            db: MongoDB connection
            embeddings_client: OpenAI embeddings client
            user_id: Current user's ID (for filtering)
        """
        self.db = db
        self.embeddings = embeddings_client
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "search_memory"

    @property
    def description(self) -> str:
        return (
            "Search your memory for information about the user. "
            "Use this when the user asks about their preferences, "
            "past conversations, personal info, or anything you should remember. "
            "Returns relevant context from previous interactions."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for (e.g., 'user's favorite food', 'their job', 'programming preferences')"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, limit: int = 5) -> ToolResult:
        """
        Search memory for relevant context.

        Args:
            query: Search query
            limit: Max results to return

        Returns:
            ToolResult with matching context entries
        """
        try:
            logger.info(f"Searching memory for: {query}")

            # Generate embedding for query
            embedding = await self.embeddings.get_embedding(query)

            # Search MongoDB
            results = await self.db.search_context(
                user_id=self.user_id,
                embedding=embedding,
                limit=limit
            )

            if not results:
                return ToolResult(
                    success=True,
                    data="No relevant memories found."
                )

            # Format results
            memories = []
            for ctx in results:
                memories.append(f"[{ctx.type}] {ctx.value}")

            return ToolResult(
                success=True,
                data="\n".join(memories)
            )

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )


class SaveMemoryTool(BaseTool):
    """
    Tool for saving information to long-term memory.

    Stores context with embeddings for later retrieval.
    """

    def __init__(
        self,
        db: MongoDB,
        embeddings_client: EmbeddingsClient,
        user_id: str
    ):
        self.db = db
        self.embeddings = embeddings_client
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "save_memory"

    @property
    def description(self) -> str:
        return (
            "Save important information about the user to memory. "
            "Use this when the user shares personal info, preferences, "
            "facts about themselves, or anything worth remembering. "
            "Types: 'profile' (name, job), 'preference' (likes/dislikes), "
            "'fact' (general info), 'event' (things that happened)."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "memory_type": {
                    "type": "string",
                    "enum": ["profile", "preference", "fact", "event"],
                    "description": "Type of memory to save"
                },
                "content": {
                    "type": "string",
                    "description": "The information to remember (e.g., 'User's name is John', 'Prefers Python over JavaScript')"
                }
            },
            "required": ["memory_type", "content"]
        }

    async def execute(self, content: str, memory_type: str = None, **kwargs) -> ToolResult:
        """
        Save information to memory.

        Args:
            content: Information to save
            memory_type: Type of memory (profile, preference, fact, event)
            **kwargs: Handle alternative parameter names (e.g., 'type')

        Returns:
            ToolResult indicating success/failure
        """
        # Handle LLM sending 'type' instead of 'memory_type'
        if memory_type is None:
            memory_type = kwargs.get('type', 'fact')

        try:
            logger.info(f"Saving memory [{memory_type}]: {content[:50]}...")

            # Generate embedding
            embedding = await self.embeddings.get_embedding(content)

            # Create context schema
            from schemas.context import ContextSchema
            context = ContextSchema(
                user_id=self.user_id,
                type=memory_type,
                value=content,
                embedding=embedding
            )

            # Save to MongoDB
            await self.db.save_context(context)

            return ToolResult(
                success=True,
                data=f"Remembered: {content}"
            )

        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
