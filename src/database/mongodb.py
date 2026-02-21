# ============================================
# MONGODB - Database connection and operations
# ============================================

import logging
from typing import List, Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import DESCENDING

from schemas.context import ContextSchema
from schemas.message import MessageSchema
from schemas.reminder import ReminderSchema
from schemas.note import NoteSchema
from constants import (
    MAX_RECENT_MESSAGES,
    VECTOR_INDEX_NAME,
    NOTES_INDEX_NAME,
    COLLECTION_CONTEXT,
    COLLECTION_MESSAGES,
    COLLECTION_REMINDERS,
    COLLECTION_NOTES
)

# Set up logging
logger = logging.getLogger(__name__)


class MongoDB:
    """
    MongoDB connection and operations.

    Uses Motor for async operations.
    Handles all database interactions for:
    - Context (long-term memory with embeddings)
    - Messages (conversation history)
    - Reminders (calendar backup)
    """

    def __init__(self, uri: str, database_name: str = "agent_db"):
        """
        Initialize MongoDB client.

        Args:
            uri: MongoDB connection URI
            database_name: Database name to use
        """
        self.uri = uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """
        Connect to MongoDB.

        Establishes connection and verifies it works.
        """
        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.database_name]

            # Verify connection
            await self.client.admin.command("ping")
            logger.info(f"Connected to MongoDB: {self.database_name}")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Disconnect from MongoDB.
        """
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    # ==========================================
    # MESSAGE OPERATIONS
    # ==========================================

    async def save_message(self, message: MessageSchema) -> str:
        """
        Save a chat message.

        Args:
            message: Message to save

        Returns:
            Inserted document ID
        """
        collection = self.db[COLLECTION_MESSAGES]
        result = await collection.insert_one(message.to_document())
        return str(result.inserted_id)

    async def get_messages(
        self,
        user_id: str,
        limit: int = MAX_RECENT_MESSAGES
    ) -> List[MessageSchema]:
        """
        Get recent messages for a user.

        Args:
            user_id: User identifier
            limit: Maximum messages to return

        Returns:
            List of messages (oldest first)
        """
        collection = self.db[COLLECTION_MESSAGES]

        cursor = collection.find(
            {"user_id": user_id}
        ).sort("timestamp", DESCENDING).limit(limit)

        docs = await cursor.to_list(length=limit)

        # Reverse to get oldest first
        docs.reverse()

        return [MessageSchema.from_document(doc) for doc in docs]

    # ==========================================
    # CONTEXT OPERATIONS
    # ==========================================

    async def save_context(self, context: ContextSchema) -> str:
        """
        Save a context entry.

        Args:
            context: Context to save

        Returns:
            Inserted document ID
        """
        collection = self.db[COLLECTION_CONTEXT]
        result = await collection.insert_one(context.to_document())
        return str(result.inserted_id)

    async def get_context_by_type(
        self,
        user_id: str,
        context_type: str,
        limit: int = 10
    ) -> List[ContextSchema]:
        """
        Get context entries by type.

        Args:
            user_id: User identifier
            context_type: Type of context (profile, fact, etc.)
            limit: Maximum entries to return

        Returns:
            List of context entries
        """
        collection = self.db[COLLECTION_CONTEXT]

        cursor = collection.find({
            "user_id": user_id,
            "type": context_type
        }).sort("updated_at", DESCENDING).limit(limit)

        docs = await cursor.to_list(length=limit)

        return [ContextSchema.from_document(doc) for doc in docs]

    async def get_all_context(
        self,
        user_id: str,
        limits: Optional[Dict[str, int]] = None
    ) -> Dict[str, List[ContextSchema]]:
        """
        Get all context for a user, grouped by type.

        Args:
            user_id: User identifier
            limits: Optional dict of type -> limit

        Returns:
            Dict with type as key, list of contexts as value
        """
        from constants import CONTEXT_LIMITS

        limits = limits or CONTEXT_LIMITS
        result = {}

        for context_type, limit in limits.items():
            entries = await self.get_context_by_type(user_id, context_type, limit)
            if entries:
                result[context_type] = entries

        return result

    async def search_context(
        self,
        user_id: str,
        embedding: List[float],
        limit: int = 5
    ) -> List[ContextSchema]:
        """
        Search context using vector similarity.

        Uses MongoDB Atlas Vector Search.

        Args:
            user_id: User identifier
            embedding: Query embedding vector
            limit: Maximum results

        Returns:
            List of similar context entries
        """
        collection = self.db[COLLECTION_CONTEXT]

        # Vector search pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": VECTOR_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": embedding,
                    "numCandidates": limit * 10,
                    "limit": limit,
                    "filter": {"user_id": user_id}
                }
            },
            {
                "$project": {
                    "user_id": 1,
                    "type": 1,
                    "value": 1,
                    "embedding": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)

        return [ContextSchema.from_document(doc) for doc in docs]

    async def delete_context(
        self,
        user_id: str,
        context_type: Optional[str] = None
    ) -> int:
        """
        Delete context entries.

        Args:
            user_id: User identifier
            context_type: Optional type to delete (all if None)

        Returns:
            Number of deleted documents
        """
        collection = self.db[COLLECTION_CONTEXT]

        query = {"user_id": user_id}
        if context_type:
            query["type"] = context_type

        result = await collection.delete_many(query)
        return result.deleted_count

    # ==========================================
    # REMINDER OPERATIONS
    # ==========================================

    async def save_reminder(self, reminder: ReminderSchema) -> str:
        """
        Save a reminder.

        Args:
            reminder: Reminder to save

        Returns:
            Inserted document ID
        """
        collection = self.db[COLLECTION_REMINDERS]
        result = await collection.insert_one(reminder.to_document())
        return str(result.inserted_id)

    async def get_reminders(
        self,
        user_id: str,
        include_completed: bool = False
    ) -> List[ReminderSchema]:
        """
        Get reminders for a user.

        Args:
            user_id: User identifier
            include_completed: Whether to include completed reminders

        Returns:
            List of reminders
        """
        collection = self.db[COLLECTION_REMINDERS]

        query = {"user_id": user_id}
        if not include_completed:
            query["completed"] = False

        cursor = collection.find(query).sort("remind_at", 1)
        docs = await cursor.to_list(length=100)

        return [ReminderSchema.from_document(doc) for doc in docs]

    # ==========================================
    # NOTE OPERATIONS
    # ==========================================

    async def save_note(self, note: NoteSchema) -> str:
        """
        Save a note.

        Args:
            note: Note to save

        Returns:
            Inserted document ID
        """
        collection = self.db[COLLECTION_NOTES]
        result = await collection.insert_one(note.to_document())
        return str(result.inserted_id)

    async def get_notes(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[NoteSchema]:
        """
        Get all notes for a user.

        Args:
            user_id: User identifier
            limit: Maximum notes to return

        Returns:
            List of notes (newest first)
        """
        collection = self.db[COLLECTION_NOTES]

        cursor = collection.find(
            {"user_id": user_id}
        ).sort("created_at", DESCENDING).limit(limit)

        docs = await cursor.to_list(length=limit)

        return [NoteSchema.from_document(doc) for doc in docs]

    async def get_notes_by_tag(
        self,
        user_id: str,
        tag: str,
        limit: int = 20
    ) -> List[NoteSchema]:
        """
        Get notes with a specific tag.

        Args:
            user_id: User identifier
            tag: Tag to filter by
            limit: Maximum notes to return

        Returns:
            List of notes with the tag
        """
        collection = self.db[COLLECTION_NOTES]

        cursor = collection.find({
            "user_id": user_id,
            "tags": tag
        }).sort("created_at", DESCENDING).limit(limit)

        docs = await cursor.to_list(length=limit)

        return [NoteSchema.from_document(doc) for doc in docs]

    async def search_notes(
        self,
        user_id: str,
        embedding: List[float],
        limit: int = 5
    ) -> List[NoteSchema]:
        """
        Search notes using vector similarity.

        Args:
            user_id: User identifier
            embedding: Query embedding vector
            limit: Maximum results

        Returns:
            List of similar notes
        """
        collection = self.db[COLLECTION_NOTES]

        # Vector search pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": NOTES_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": embedding,
                    "numCandidates": limit * 10,
                    "limit": limit,
                    "filter": {"user_id": user_id}
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "user_id": 1,
                    "title": 1,
                    "content": 1,
                    "tags": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)

        return [NoteSchema.from_document(doc) for doc in docs]

    async def delete_note(
        self,
        user_id: str,
        title: str
    ) -> bool:
        """
        Delete a note by title.

        Args:
            user_id: User identifier
            title: Note title to delete

        Returns:
            True if deleted, False if not found
        """
        collection = self.db[COLLECTION_NOTES]

        result = await collection.delete_one({
            "user_id": user_id,
            "title": title
        })

        return result.deleted_count > 0

    async def delete_all_notes(self, user_id: str) -> int:
        """
        Delete all notes for a user.

        Args:
            user_id: User identifier

        Returns:
            Number of deleted notes
        """
        collection = self.db[COLLECTION_NOTES]
        result = await collection.delete_many({"user_id": user_id})
        return result.deleted_count
