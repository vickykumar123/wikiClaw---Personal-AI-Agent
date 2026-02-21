# ============================================
# MEMORY SUB-AGENT - Handles user memories
# ============================================

from typing import List

from agents.base import BaseSubAgent
from agent.llm import OllamaClient
from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient
from tools.base import BaseTool
from tools.memory import SaveMemoryTool, SearchMemoryTool


MEMORY_AGENT_PROMPT = """You are a memory specialist agent.

Your job is to:
- Save important information about the user
- Search and retrieve user's memories when asked

You have these tools:
- save_memory: Save personal info (content=what to save, memory_type=profile/preference/fact/event)
- search_memory: Find previously saved information

IMPORTANT:
- Call ONE tool to complete the task
- After the tool returns a result, respond with that result
- Example: If tool returns "Remembered: favorite color is blue" → respond "Saved: your favorite color is blue"
- Do NOT say generic things like "Anything else?" - confirm the specific action taken
- Do NOT use markdown formatting - use plain text only"""


class MemoryAgent(BaseSubAgent):
    """Sub-agent for handling user memories."""

    def __init__(
        self,
        llm_client: OllamaClient,
        db: MongoDB,
        embeddings_client: EmbeddingsClient,
        user_id: str
    ):
        super().__init__(llm_client)
        self.db = db
        self.embeddings = embeddings_client
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "memory_agent"

    @property
    def description(self) -> str:
        return (
            "Saves and retrieves user's personal information and memories. "
            "Use this when user shares personal info to remember, "
            "or when user asks about themselves or past conversations."
        )

    @property
    def system_prompt(self) -> str:
        return MEMORY_AGENT_PROMPT

    def get_tools(self) -> List[BaseTool]:
        return [
            SaveMemoryTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=self.user_id
            ),
            SearchMemoryTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=self.user_id
            )
        ]
