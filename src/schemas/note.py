# ============================================
# NOTE SCHEMA - Structured notes storage
# ============================================

from datetime import datetime
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, Field


class NoteSchema(BaseModel):
    """
    Schema for notes in MongoDB.

    Notes are structured with title, content, and optional tags.
    Embeddings enable semantic search.

    Collection: notes
    """

    user_id: str = Field(..., description="User ID who owns the note")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    tags: List[str] = Field(default_factory=list, description="Optional tags")

    # Embedding for semantic search
    embedding: List[float] = Field(
        default_factory=list,
        description="Embedding vector for semantic search"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

    def to_document(self) -> Dict[str, Any]:
        """Convert to MongoDB document."""
        return self.model_dump()

    @classmethod
    def from_document(cls, doc: Dict[str, Any]) -> "NoteSchema":
        """Create schema from MongoDB document."""
        # Keep _id for reference
        doc_id = doc.pop("_id", None)
        note = cls(**doc)
        if doc_id:
            note._doc_id = str(doc_id)
        return note

    def summary(self) -> str:
        """Get a brief summary of the note."""
        tags_str = f" [{', '.join(self.tags)}]" if self.tags else ""
        return f"{self.title}{tags_str}: {self.content[:50]}..."
