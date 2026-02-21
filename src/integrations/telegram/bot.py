# ============================================
# TELEGRAM BOT - Telegram implementation
# ============================================

import logging
from typing import Callable, Optional

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from integrations.base import BaseMessenger, Message
from constants import MSG_BOT_STARTED

# Set up logging
logger = logging.getLogger(__name__)


class TelegramBot(BaseMessenger):
    """
    Telegram implementation of BaseMessenger.

    Handles all Telegram-specific logic while providing
    a standard interface to the rest of the application.
    """

    def __init__(
        self,
        token: str,
        message_callback: Optional[Callable[[Message], str]] = None
    ):
        """
        Initialize Telegram bot.

        Args:
            token: Telegram bot token from BotFather
            message_callback: Function to call when message received.
                              Takes Message, returns response string.
        """
        self.token = token
        self.message_callback = message_callback
        self.application: Optional[Application] = None

    async def start(self) -> None:
        """
        Initialize and start the Telegram bot.

        - Build the application
        - Add message handler
        - Start polling (webhook setup is in webhook.py)
        """
        # Build application
        self.application = Application.builder().token(self.token).build()

        # Add handler for text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )

        # Initialize the application
        await self.application.initialize()

        logger.info(MSG_BOT_STARTED)

    async def stop(self) -> None:
        """
        Clean shutdown of the bot.

        - Stop the application
        - Clean up resources
        """
        if self.application:
            await self.application.shutdown()
            logger.info("Telegram bot stopped")

    async def send_message(self, chat_id: str, text: str) -> bool:
        """
        Send a message to a Telegram chat.

        Args:
            chat_id: Telegram chat ID
            text: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if self.application:
                await self.application.bot.send_message(
                    chat_id=int(chat_id),
                    text=text
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def handle_message(self, message: Message) -> None:
        """
        Process an incoming message and send response.

        Args:
            message: Standardized Message object
        """
        if self.message_callback:
            # Get response from callback (will be agent in future)
            response = await self.message_callback(message)

            # Send response back to user
            await self.send_message(message.chat_id, response)

    async def _on_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Internal handler for incoming Telegram messages.

        Converts Telegram Update to standardized Message format
        and passes to handle_message.

        Args:
            update: Telegram Update object
            context: Telegram context
        """
        # Extract message info
        if not update.message or not update.message.text:
            return

        # Convert to standardized Message format
        message = Message(
            user_id=str(update.effective_user.id),
            chat_id=str(update.effective_chat.id),
            text=update.message.text,
            username=update.effective_user.username or update.effective_user.first_name,
            platform="telegram"
        )

        # Process the message
        await self.handle_message(message)
