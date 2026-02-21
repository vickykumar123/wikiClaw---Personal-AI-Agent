# ============================================
# BASE MESSENGER - Interface for all platforms
# ============================================

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    """Standardized message format across all platforms."""

    user_id: str          # Unique user identifier
    chat_id: str          # Chat/conversation identifier
    text: str             # Message content
    username: Optional[str] = None  # User's display name
    platform: str = ""    # Which platform (telegram, discord, etc.)


class BaseMessenger(ABC):
    """
    Abstract base class for all messaging platforms.

    All platforms (Telegram, Discord, WhatsApp) must implement
    these methods to ensure consistent behavior.
    """

    @abstractmethod
    async def start(self) -> None:
        """
        Initialize and start the messenger.

        - Connect to the platform
        - Set up webhook or polling
        - Start listening for messages
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Clean shutdown of the messenger.

        - Remove webhook registration
        - Close connections
        - Clean up resources
        """
        pass

    @abstractmethod
    async def send_message(self, chat_id: str, text: str) -> bool:
        """
        Send a message to a user/chat.

        Args:
            chat_id: The chat to send to
            text: Message content

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        """
        Process an incoming message.

        Args:
            message: Standardized Message object
        """
        pass
