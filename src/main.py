# ============================================
# MAIN - Application entry point
# ============================================

import asyncio
import logging
import signal
from typing import Optional

from config import load_config, Config
from constants import LOG_FORMAT, LOG_DATE_FORMAT, MSG_BOT_STARTED
from integrations.telegram.bot import TelegramBot
from integrations.telegram.webhook import WebhookServer

# Global references for shutdown handler
webhook_server: Optional[WebhookServer] = None
telegram_bot: Optional[TelegramBot] = None


def setup_logging() -> None:
    """
    Configure application logging.

    Sets up console logging with timestamp and level.
    Sync function - just configures loggers, no I/O.
    """
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )


async def echo_response(message) -> str:
    """
    Temporary echo response for testing.

    Will be replaced by Agent in Phase 2.

    Args:
        message: Incoming Message object

    Returns:
        Echo response string
    """
    return f"Echo: {message.text}"


async def shutdown(sig: Optional[signal.Signals] = None) -> None:
    """
    Clean shutdown of all services.

    Args:
        sig: Signal that triggered shutdown (optional)
    """
    logger = logging.getLogger(__name__)

    if sig:
        logger.info(f"Received signal {sig.name}, shutting down...")

    # Remove webhook from Telegram
    if webhook_server:
        await webhook_server.remove_telegram_webhook()

    # Stop Telegram bot
    if telegram_bot:
        await telegram_bot.stop()

    logger.info("Shutdown complete")


async def main() -> None:
    """
    Main application entry point.

    1. Setup logging
    2. Load configuration
    3. Create and start Telegram bot
    4. Create webhook server
    5. Start ngrok tunnel
    6. Set webhook with Telegram
    7. Run server
    """
    global webhook_server, telegram_bot

    # Setup logging (sync - fast)
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load configuration (sync - reads env vars)
    config = load_config()
    logger.info("Configuration loaded")

    # Create Telegram bot
    telegram_bot = TelegramBot(
        token=config.telegram_token,
        message_callback=echo_response  # Temporary, will be Agent later
    )

    # Initialize the bot
    await telegram_bot.start()

    # Create webhook server
    webhook_server = WebhookServer(
        port=config.webhook_port,
        ngrok_auth_token=config.ngrok_auth_token
    )

    # Register bot with webhook server
    webhook_server.register_telegram_bot(telegram_bot)

    # Start ngrok tunnel (async - network I/O)
    webhook_url = await webhook_server.start_ngrok()
    logger.info(f"Webhook URL: {webhook_url}")

    # Set webhook with Telegram (async - network I/O)
    await webhook_server.set_telegram_webhook()

    logger.info(MSG_BOT_STARTED)
    logger.info("Press Ctrl+C to stop")

    # Run the webhook server (async - HTTP server)
    try:
        await webhook_server.run_async()
    except asyncio.CancelledError:
        logger.info("Server cancelled")
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
