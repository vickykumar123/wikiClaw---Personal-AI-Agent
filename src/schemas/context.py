# ============================================
# CONTEXT SCHEMA - Unified long-term memory
# ============================================

from datetime import datetime, timezone
from typing import List, Dict, Any


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)

from pydantic import BaseModel, Field

from constants import (
    CONTEXT_TYPE_PROFILE,
    CONTEXT_TYPE_PREFERENCE,
    CONTEXT_TYPE_FACT,
    CONTEXT_TYPE_TOPIC,
    CONTEXT_TYPE_EVENT,
    CONTEXT_TYPE_SESSION,
)

# Valid context types
VALID_CONTEXT_TYPES = [
    CONTEXT_TYPE_PROFILE,
    CONTEXT_TYPE_PREFERENCE,
    CONTEXT_TYPE_FACT,
    CONTEXT_TYPE_TOPIC,
    CONTEXT_TYPE_EVENT,
    CONTEXT_TYPE_SESSION,
]


class ContextSchema(BaseModel):
    """
    Schema for unified context collection in MongoDB.

    Stores all types of long-term memory:
    - profile: User info (name, occupation)
    - preference: User preferences (response style)
    - fact: Things to remember (wifi password)
    - topic: Active topics/projects
    - event: Upcoming events
    - session: Session summaries

    Collection: context
    """

    user_id: str = Field(..., description="Telegram user ID")
    type: str = Field(..., description="Context type (profile, fact, etc.)")
    value: str = Field(..., description="The actual content")

    # Embedding for semantic search
    embedding: List[float] = Field(
        ...,
        description="Vector embedding for semantic search (1536 dimensions)"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

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
    def from_document(cls, doc: Dict[str, Any]) -> "ContextSchema":
        """
        Create schema from MongoDB document.

        Args:
            doc: MongoDB document

        Returns:
            ContextSchema instance
        """
        doc.pop("_id", None)
        return cls(**doc)
