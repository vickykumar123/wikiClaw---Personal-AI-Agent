# ============================================
# TELEGRAM BOT - Telegram implementation
# ============================================

import logging
import os
import re
import tempfile
import time
from typing import Any, Callable, Optional, List

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from integrations.base import BaseMessenger, Message
from constants import MSG_BOT_STARTED, SUPPORTED_FILE_EXTENSIONS
from utils.file_processor import process_file, is_supported_file

# Set up logging
logger = logging.getLogger(__name__)

# Telegram message limit
MAX_TELEGRAM_MESSAGE_LENGTH = 4000  # Leave some buffer from 4096


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', '').strip(), text)
    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    # Remove italic (careful with bullet points)
    text = re.sub(r'(?<![*\w])\*([^*]+)\*(?![*\w])', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text


def split_message(text: str, max_length: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> List[str]:
    """Split long message into chunks for Telegram."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    # Split by paragraphs first
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_length:
            current_chunk += para + '\n\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If single paragraph is too long, split by sentences
            if len(para) > max_length:
                sentences = para.replace('. ', '.\n').split('\n')
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= max_length:
                        current_chunk += sentence + ' '
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ' '
            else:
                current_chunk = para + '\n\n'

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text[:max_length]]


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
        self.application: Optional[Any] = None

    async def start(self) -> None:
        """
        Initialize and start the Telegram bot.

        - Build the application
        - Add message handlers
        - Start polling (webhook setup is in webhook.py)
        """
        # Build application
        self.application = Application.builder().token(self.token).build()

        # Add handler for text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )

        # Add handler for documents (files)
        self.application.add_handler(
            MessageHandler(filters.Document.ALL, self._on_document)
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

        Handles:
        - Stripping markdown for plain text
        - Splitting long messages into chunks

        Args:
            chat_id: Telegram chat ID
            text: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.application:
                return False

            # Strip markdown formatting
            clean_text = strip_markdown(text)

            # Split into chunks if too long
            chunks = split_message(clean_text)

            for chunk in chunks:
                await self.application.bot.send_message(
                    chat_id=int(chat_id),
                    text=chunk
                )

            return True
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

    async def process_update_with_logging(self, update: Any, request_id: Optional[str] = None) -> Any:
        """
        Wrap processing of a raw Telegram update with structured logging.

        This wrapper produces a minimal, non-sensitive summary of the update,
        logs the start and completion (including duration), delegates to the
        underlying application's process_update method, and propagates any
        exceptions raised by the underlying processing.

        Args:
            update: Raw update object from Telegram or a dict representing it.
            request_id: Optional external request identifier to correlate logs.

        Returns:
            The value returned by the underlying application's process_update.

        Raises:
            RuntimeError: If the underlying application is not available or
                does not expose process_update.
            Exception: Re-raises any exception thrown by the underlying
                application's process_update.
        """
        # Determine update_id robustly
        update_id = getattr(update, 'update_id', None)
        if update_id is None and isinstance(update, dict):
            update_id = update.get('update_id')

        # Build a minimal, non-sensitive summary
        summary = "unknown"
        try:
            if hasattr(update, 'message') and getattr(update.message, 'text', None):
                text_val = getattr(update.message, 'text', None)
                summary = f"message_text_len={len(text_val) if text_val else 0}"
            elif isinstance(update, dict):
                keys = list(update.keys())
                summary = f"keys={keys}"
            else:
                top_attrs = []
                for attr in ('message', 'callback_query', 'edited_message', 'channel_post'):
                    if getattr(update, attr, None):
                        top_attrs.append(attr)
                summary = f"types={top_attrs or ['unknown']}"
        except Exception:
            summary = "summary_unavailable"

        logger.info(
            "Starting processing update: request_id=%s, update_id=%s, summary=%s",
            request_id,
            update_id,
            summary,
        )

        # Ensure underlying application is present and supports process_update
        if not self.application or not hasattr(self.application, 'process_update'):
            logger.error(
                "Application not available or missing process_update: request_id=%s, update_id=%s",
                request_id,
                update_id,
            )
            raise RuntimeError("Telegram application not available to process update")

        start_time = time.perf_counter()
        try:
            result = await self.application.process_update(update)
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            # Minimal result summary to avoid sensitive content
            result_summary = type(result).__name__ if result is not None else 'None'

            logger.info(
                "Completed processing update: request_id=%s, update_id=%s, result=%s, duration_ms=%.2f",
                request_id,
                update_id,
                result_summary,
                duration_ms,
            )

            return result
        except Exception:
            logger.exception(
                "Exception while processing update: request_id=%s, update_id=%s",
                request_id,
                update_id,
            )
            raise

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

    async def _on_document(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle incoming document/file uploads.

        Downloads the file, extracts text, and processes as a message.

        Args:
            update: Telegram Update object
            context: Telegram context
        """
        if not update.message or not update.message.document:
            return

        document = update.message.document
        file_name = document.file_name or "unknown"
        file_ext = os.path.splitext(file_name)[1].lower()

        # Check if file type is supported
        if file_ext not in SUPPORTED_FILE_EXTENSIONS:
            await update.message.reply_text(
                f"Sorry, I don't support {file_ext} files.\n\n"
                f"Supported types: PDF, Word (.docx), Excel (.xlsx), CSV, "
                f"Text (.txt, .md), JSON, and code files."
            )
            return

        # Get caption (user's message with the file)
        caption = update.message.caption or "Please analyze this file."

        # Send processing message
        processing_msg = await update.message.reply_text(
            f"Processing {file_name}..."
        )

        try:
            # Download file to temp directory
            file = await context.bot.get_file(document.file_id)

            with tempfile.NamedTemporaryFile(
                suffix=file_ext,
                delete=False
            ) as tmp_file:
                tmp_path = tmp_file.name
                await file.download_to_drive(tmp_path)

            # Process the file
            result = process_file(tmp_path)

            # Clean up temp file
            os.unlink(tmp_path)

            if not result.success:
                await processing_msg.edit_text(f"Error processing file: {result.error}")
                return

            # Build message with file content
            file_context = f"[File: {file_name}]\n"
            if result.truncated:
                file_context += "[Note: Content was truncated due to length]\n"
            file_context += f"\n{result.text}\n\n"
            file_context += f"User request: {caption}"

            # Delete processing message
            await processing_msg.delete()

            # Create message object
            message = Message(
                user_id=str(update.effective_user.id),
                chat_id=str(update.effective_chat.id),
                text=file_context,
                username=update.effective_user.username or update.effective_user.first_name,
                platform="telegram"
            )

            # Process the message
            await self.handle_message(message)

        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            await processing_msg.edit_text(
                f"Sorry, I couldn't process the file: {str(e)}"
            )
