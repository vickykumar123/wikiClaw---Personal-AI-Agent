# ============================================
# CONFIG - Load and validate environment variables
# ============================================

import os
from dataclasses import dataclass
from dotenv import load_dotenv

from constants import (
    DEFAULT_WEBHOOK_PORT,
    DEFAULT_WEBHOOK_PATH,
    DEFAULT_OLLAMA_HOST,
    DEFAULT_OLLAMA_MODEL,
    ERROR_MISSING_TELEGRAM_TOKEN,
    ERROR_MISSING_OPENAI_KEY,
    ERROR_MISSING_MONGODB_URI,
)


@dataclass
class Config:
    """Configuration loaded from environment variables."""

    # Telegram
    telegram_token: str

    # Webhook
    ngrok_auth_token: str
    webhook_url: str
    webhook_port: int
    webhook_path: str

    # OpenAI
    openai_api_key: str

    # MongoDB
    mongodb_uri: str

    # Ollama
    ollama_host: str
    ollama_model: str

    # Google Calendar
    google_credentials_path: str
    google_token_path: str


def load_config() -> Config:
    """
    Load configuration from .env file.

    Returns:
        Config object with all settings

    Raises:
        ValueError: If required environment variables are missing
    """
    # Load .env file
    load_dotenv()

    # Get required variables (will raise error if missing)
    telegram_token = _get_required("TELEGRAM_BOT_TOKEN", ERROR_MISSING_TELEGRAM_TOKEN)
    openai_api_key = _get_required("OPENAI_API_KEY", ERROR_MISSING_OPENAI_KEY)
    mongodb_uri = _get_required("MONGODB_URI", ERROR_MISSING_MONGODB_URI)

    # Get optional variables with defaults
    config = Config(
        # Telegram
        telegram_token=telegram_token,

        # Webhook
        ngrok_auth_token=os.getenv("NGROK_AUTH_TOKEN", ""),
        webhook_url=os.getenv("WEBHOOK_URL", ""),
        webhook_port=int(os.getenv("WEBHOOK_PORT", DEFAULT_WEBHOOK_PORT)),
        webhook_path=os.getenv("WEBHOOK_PATH", DEFAULT_WEBHOOK_PATH),

        # OpenAI
        openai_api_key=openai_api_key,

        # MongoDB
        mongodb_uri=mongodb_uri,

        # Ollama
        ollama_host=os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST),
        ollama_model=os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),

        # Google Calendar
        google_credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json"),
        google_token_path=os.getenv("GOOGLE_TOKEN_PATH", "./token.json"),
    )

    return config


def _get_required(key: str, error_message: str) -> str:
    """
    Get a required environment variable.

    Args:
        key: Environment variable name
        error_message: Error message if missing

    Returns:
        The environment variable value

    Raises:
        ValueError: If the variable is missing or empty
    """
    value = os.getenv(key)

    if not value:
        raise ValueError(error_message)
    return value

def format_timestamp(dt):
    """Format a datetime object as 'YYYY-MM-DD HH:MM:SS'."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def truncate_text(text, max_length=100):
    """Truncate text to max_length characters, adding an ellipsis if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + '…'
