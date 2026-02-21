# ============================================
# REMINDER SCHEMA - Calendar events backup
# ============================================

from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class ReminderSchema(BaseModel):
    """
    Schema for reminders/calendar events in MongoDB.

    Serves as backup/log for Google Calendar events.
    Primary source of truth is Google Calendar.

    Collection: reminders
    """

    user_id: str = Field(..., description="Telegram user ID")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(default=None, description="Event description")
    remind_at: datetime = Field(..., description="When to remind")

    # Google Calendar link
    google_event_id: Optional[str] = Field(
        default=None,
        description="Google Calendar event ID"
    )

    # Status
    completed: bool = Field(default=False, description="Whether completed")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    def from_document(cls, doc: Dict[str, Any]) -> "ReminderSchema":
        """
        Create schema from MongoDB document.

        Args:
            doc: MongoDB document

        Returns:
            ReminderSchema instance
        """
        doc.pop("_id", None)
        return cls(**doc)
