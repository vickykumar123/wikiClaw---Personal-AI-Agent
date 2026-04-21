# ============================================
# NOTES TOOLS - Create, search, list, delete notes
# ============================================

import logging
from typing import Any, Dict, List

from tools.base import BaseTool, ToolResult
from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient
from schemas.note import NoteSchema

logger = logging.getLogger(__name__)


class CreateNoteTool(BaseTool):
    """Tool for creating a new note."""

    def __init__(
        self,
        db: MongoDB,
        embeddings_client: EmbeddingsClient,
        user_id: str
    ):
        logger.info(f"Initializing CreateNoteTool for user_id: {user_id}")
        self.db = db
        self.embeddings = embeddings_client
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "create_note"

    @property
    def description(self) -> str:
        return (
            "Create a new note with a title and content. "
            "Use this when the user explicitly asks to save/create a note, "
            "write something down, or make a reminder note. "
            "Optionally add tags for organization."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note (short, descriptive)"
                },
                "content": {
                    "type": "string",
                    "description": "Content of the note"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization (e.g., ['work', 'important'])"
                }
            },
            "required": ["title", "content"]
        }

    async def execute(
        self,
        title: str,
        content: str,
        tags: List[str] = None
    ) -> ToolResult:
        """Create a new note."""
        try:
            logger.info(f"CreateNoteTool called with title={title}, tags={tags}")
            logger.debug("Generating embedding for note")
            embed_text = f"{title} {content}"
            embedding = await self.embeddings.get_embedding(embed_text)
            logger.debug("Embedding generated")
            logger.debug("Saving note to DB")
            note = NoteSchema(
                user_id=self.user_id,
                title=title,
                content=content,
                tags=tags or [],
                embedding=embedding
            )
            doc_id = await self.db.save_note(note)
            logger.debug(f"Note saved with id {doc_id}")
            tags_str = f" with tags {tags}" if tags else ""
            logger.info(f"Note '{title}' created{tags_str}.")
            return ToolResult(
                success=True,
                data=f"Note '{title}' created{tags_str}."
            )
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            raise RuntimeError(f"{__name__}: {e}")


class SearchNotesTool(BaseTool):
    """Tool for searching notes by content."""

    def __init__(
        self,
        db: MongoDB,
        embeddings_client: EmbeddingsClient,
        user_id: str
    ):
        logger.info(f"Initializing SearchNotesTool for user_id: {user_id}")
        self.db = db
        self.embeddings = embeddings_client
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "search_notes"

    @property
    def description(self) -> str:
        return (
            "Search through user's notes using semantic search. "
            "Use this when the user asks to find a note, "
            "or asks about something they wrote down."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for in notes"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str) -> ToolResult:
        """Search notes by content."""
        try:
            logger.info(f"SearchNotesTool called with query={query}")
            logger.debug("Generating embedding for query")
            embedding = await self.embeddings.get_embedding(query)
            logger.debug("Embedding generated")
            logger.debug("Searching notes in DB")
            results = await self.db.search_notes(
                user_id=self.user_id,
                embedding=embedding,
                limit=5
            )
            logger.debug(f"Found {len(results)} notes")
            if not results:
                return ToolResult(
                    success=True,
                    data="No notes found matching your search."
                )

            # Format results
            notes_text = []
            for note in results:
                tags_str = f" [{', '.join(note.tags)}]" if note.tags else ""
                notes_text.append(f"**{note.title}**{tags_str}: {note.content}")

            logger.info("Search completed successfully")
            return ToolResult(
                success=True,
                data="\n\n".join(notes_text)
            )

        except Exception as e:
            logger.error(f"Failed to search notes: {e}")
            raise RuntimeError(f"{__name__}: {e}")


class ListNotesTool(BaseTool):
    """Tool for listing all notes."""

    def __init__(self, db: MongoDB, user_id: str):
        logger.info(f"Initializing ListNotesTool for user_id: {user_id}")
        self.db = db
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "list_notes"

    @property
    def description(self) -> str:
        return (
            "List all notes or notes with a specific tag. "
            "Use this when the user asks to see all their notes, "
            "or wants to see notes in a category."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tag": {
                    "type": "string",
                    "description": "Optional tag to filter notes by"
                }
            },
            "required": []
        }

    async def execute(self, tag: str = None) -> ToolResult:
        """List notes, optionally filtered by tag."""
        try:
            logger.info(f"Listing notes{' with tag: ' + tag if tag else ''}")
            if tag:
                logger.debug("Fetching notes by tag from DB")
                results = await self.db.get_notes_by_tag(
                    user_id=self.user_id,
                    tag=tag
                )
            else:
                logger.debug("Fetching all notes from DB")
                results = await self.db.get_notes(user_id=self.user_id)
            logger.debug(f"Retrieved {len(results)} notes")
            if not results:
                if tag:
                    return ToolResult(
                        success=True,
                        data=f"No notes found with tag '{tag}'."
                    )
                return ToolResult(
                    success=True,
                    data="You don't have any notes yet."
                )

            # Format results
            notes_text = []
            for i, note in enumerate(results, 1):
                tags_str = f" [{', '.join(note.tags)}]" if note.tags else ""
                notes_text.append(f"{i}. **{note.title}**{tags_str}")

            logger.info("Listing notes completed successfully")
            return ToolResult(
                success=True,
                data=f"Your notes:\n" + "\n".join(notes_text)
            )

        except Exception as e:
            logger.error(f"Failed to list notes: {e}")
            raise RuntimeError(f"${__name__}: {e}")


class DeleteNoteTool(BaseTool):
    """Tool for deleting a note."""

    def __init__(self, db: MongoDB, user_id: str):
        logger.info(f"Initializing DeleteNoteTool for user_id: {user_id}")
        self.db = db
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "delete_note"

    @property
    def description(self) -> str:
        return (
            "Delete a note by its title. "
            "Use this when the user asks to remove or delete a specific note."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the note to delete"
                }
            },
            "required": ["title"]
        }

    async def execute(self, title: str) -> ToolResult:
        """Delete a note by title."""
        try:
            logger.info(f"DeleteNoteTool called with title={title}")
            logger.debug("Deleting note from DB")
            deleted = await self.db.delete_note(
                user_id=self.user_id,
                title=title
            )
            logger.debug(f"Delete operation returned: {deleted}")
            if deleted:
                return ToolResult(
                    success=True,
                    data=f"Note '{title}' deleted."
                )
            else:
                return ToolResult(
                    success=True,
                    data=f"Note '{title}' not found."
                )

        except Exception as e:
            logger.error(f"Failed to delete note: {e}")
            raise RuntimeError(f"{__name__}: {e}")
