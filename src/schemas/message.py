# ============================================
# MESSAGE SCHEMA - Chat messages collection
# ============================================

from datetime import datetime, timezone
from typing import Dict, Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class MessageSchema(BaseModel):
    """
    Schema for chat messages stored in MongoDB.

    Stores conversation history for each user.
    No embeddings - just recent N messages used for context.

    Collection: messages
    """

    user_id: str = Field(..., description="Telegram user ID")
    chat_id: str = Field(..., description="Telegram chat ID")
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")
    platform: str = Field(default="telegram", description="Source platform")
    timestamp: datetime = Field(default_factory=utc_now)

    class Config:
        populate_by_name = True

    def to_document(self) -> Dict[str, Any]:
        """
        Convert to MongoDB document format.

        Returns:
            Dict ready for MongoDB insertion
        """
        return self.model_dump()

    @classmethod
    def from_document(cls, doc: Dict[str, Any]) -> "MessageSchema":
        """
        Create schema from MongoDB document.

        Args:
            doc: MongoDB document

        Returns:
            MessageSchema instance
        """
        doc.pop("_id", None)
        return cls(**doc)
