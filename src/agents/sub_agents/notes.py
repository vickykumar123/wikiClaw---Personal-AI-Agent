# ============================================
# NOTES SUB-AGENT - Handles user notes
# ============================================

from typing import List

from agents.base import BaseSubAgent
from agent.llm import OllamaClient
from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient
from tools.base import BaseTool
from tools.notes import CreateNoteTool, SearchNotesTool, ListNotesTool, DeleteNoteTool


NOTES_AGENT_PROMPT = """You are a notes management agent.

Your job is to:
- Create new notes for the user
- Search for specific notes
- List all notes
- Delete notes when requested

You have these tools:
- create_note: Create a new note with title, content, and optional tags
- search_notes: Find notes by semantic search
- list_notes: Show all user's notes
- delete_note: Remove a note by title

IMPORTANT:
- When creating a note, GENERATE the title automatically from the content
- Example: "Make a note: Buy groceries - milk, eggs" → title="Groceries", content="Buy groceries - milk, eggs"
- Example: "Note this down: Meeting at 5pm" → title="Meeting reminder", content="Meeting at 5pm"
- Do NOT ask for title - extract it from the message
- Call ONE tool, then IMMEDIATELY respond with confirmation
- Be concise - just confirm what was done"""


class NotesAgent(BaseSubAgent):
    """Sub-agent for handling user notes."""

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
        return "notes_agent"

    @property
    def description(self) -> str:
        return (
            "Creates, searches, lists, and deletes user notes. "
            "Use this when user asks to make a note, find a note, "
            "see all notes, or delete a note."
        )

    @property
    def system_prompt(self) -> str:
        return NOTES_AGENT_PROMPT

    def get_tools(self) -> List[BaseTool]:
        return [
            CreateNoteTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=self.user_id
            ),
            SearchNotesTool(
                db=self.db,
                embeddings_client=self.embeddings,
                user_id=self.user_id
            ),
            ListNotesTool(
                db=self.db,
                user_id=self.user_id
            ),
            DeleteNoteTool(
                db=self.db,
                user_id=self.user_id
            )
        ]
