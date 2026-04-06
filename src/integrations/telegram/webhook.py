# ============================================
# WEBHOOK SERVER - Single server for all platforms
# ============================================

import logging
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

# Structured JSON logging added

from fastapi import FastAPI, Request, HTTPException
from telegram import Update
import uvicorn
from pyngrok import ngrok

from constants import (
    DEFAULT_WEBHOOK_PORT,
    DEFAULT_WEBHOOK_PATH,
    MSG_WEBHOOK_SET,
    ERROR_WEBHOOK_SETUP,
)

# Set up logging
logger = logging.getLogger(__name__)


def _log_event(event: str, **kwargs) -> None:
    """Log a structured JSON event with a UTC timestamp.

    Args:
        event: Name of the event.
        **kwargs: Additional key/value pairs to include in the log.
    """
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        **kwargs,
    }
    # Use logger.info for all structured logs; include exc_info if provided in kwargs
    if kwargs.get("exc_info"):
        logger.info(json.dumps(payload), exc_info=True)
    else:
        logger.info(json.dumps(payload))


class WebhookServer:
    """
    Single FastAPI server handling webhooks for all platforms.

    Manages:
    - FastAPI application
    - ngrok tunnel
    - Webhook endpoints for each platform
    """

    def __init__(
        self,
        port: int = DEFAULT_WEBHOOK_PORT,
        ngrok_auth_token: Optional[str] = None
    ):
        """
        Initialize webhook server.

        Args:
            port: Port to run server on
            ngrok_auth_token: ngrok authentication token
        """
        self.port = port
        self.ngrok_auth_token = ngrok_auth_token
        self.ngrok_tunnel = None
        self.webhook_url: Optional[str] = None

        # Platform handlers - will be registered by each platform
        self._telegram_bot = None

        # Log server initialization (structured)
        _log_event(
            "webhook_init",
            port=self.port,
            ngrok_auth_token=bool(self.ngrok_auth_token),
        )

        # Create FastAPI app
        self.app = FastAPI(
            title="AI Agent Webhook Server",
            lifespan=self._lifespan
        )

        # Register routes
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up webhook endpoints for each platform."""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            _log_event("health_check")
            return {"status": "ok"}

        @self.app.get("/test")
        async def test_endpoint():
            """Simple test endpoint to verify server is operational."""
            _log_event("test_endpoint_called")
            return {"status": "ok", "message": "Test endpoint reachable"}

        @self.app.post("/webhook/telegram")
        async def telegram_webhook(request: Request):
            """
            Handle incoming Telegram webhook.

            Telegram sends updates as JSON POST requests.
            """
            if not self._telegram_bot:
                raise HTTPException(status_code=503, detail="Telegram bot not configured")

            try:
                # Parse the update
                data = await request.json()
                # Log receipt with truncated payload and possible update_id
                truncated = json.dumps(data)[:200]
                update_id = data.get("update_id")
                _log_event(
                    "telegram_webhook_received",
                    payload=truncated,
                    update_id=update_id,
                )
                update = Update.de_json(data, self._telegram_bot.application.bot)

                # Process the update
                await self._telegram_bot.application.process_update(update)

                _log_event(
                    "telegram_webhook_processed",
                    update_id=getattr(update, "update_id", None),
                )
                return {"ok": True}

            except Exception as e:
                _log_event("telegram_webhook_error", error=str(e), exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))

        # Placeholder for future platforms
        @self.app.post("/webhook/whatsapp")
        async def whatsapp_webhook(request: Request):
            """Handle incoming WhatsApp webhook (future)."""
            _log_event("whatsapp_webhook_called")
            return {"ok": True, "message": "WhatsApp webhook not implemented yet"}

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """
        Manage server startup and shutdown.

        - On startup: Start ngrok tunnel
        - On shutdown: Close tunnel
        """
        # Startup
        _log_event("server_startup", port=self.port)
        yield
        # Shutdown
        _log_event("server_shutdown")
        await self._stop_ngrok()

    def register_telegram_bot(self, bot) -> None:
        """
        Register Telegram bot to receive webhooks.

        Args:
            bot: TelegramBot instance
        """
        self._telegram_bot = bot
        _log_event("telegram_bot_registered", bot_class=bot.__class__.__name__)

    async def start_ngrok(self) -> str:
        """
        Start ngrok tunnel and return public URL.

        Returns:
            Public HTTPS URL for webhooks
        """
        _log_event("ngrok_start", port=self.port)
        if self.ngrok_auth_token:
            ngrok.set_auth_token(self.ngrok_auth_token)

        # Start tunnel
        self.ngrok_tunnel = ngrok.connect(self.port, "http")
        self.webhook_url = self.ngrok_tunnel.public_url

        # Ensure HTTPS
        if self.webhook_url.startswith("http://"):
            self.webhook_url = self.webhook_url.replace("http://", "https://")

        _log_event("ngrok_ready", public_url=self.webhook_url)
        return self.webhook_url

    async def _stop_ngrok(self) -> None:
        """Stop ngrok tunnel."""
        if self.ngrok_tunnel:
            ngrok.disconnect(self.ngrok_tunnel.public_url)
            _log_event(
                "ngrok_stop",
                public_url=self.ngrok_tunnel.public_url if self.ngrok_tunnel else None,
            )

    async def set_telegram_webhook(self) -> bool:
        """
        Set webhook URL with Telegram.

        Returns:
            True if successful
        """
        if not self._telegram_bot or not self.webhook_url:
            _log_event("set_telegram_webhook_error", error=ERROR_WEBHOOK_SETUP, exc_info=True)
            return False

        _log_event("set_telegram_webhook_attempt")
        try:
            webhook_full_url = f"{self.webhook_url}/webhook/telegram"

            await self._telegram_bot.application.bot.set_webhook(
                url=webhook_full_url
            )

            _log_event("set_telegram_webhook_success", url=webhook_full_url)
            return True

        except Exception as e:
            _log_event("set_telegram_webhook_error", error=str(e), exc_info=True)
            return False

    async def remove_telegram_webhook(self) -> bool:
        """
        Remove webhook from Telegram.

        Returns:
            True if successful
        """
        _log_event("remove_telegram_webhook_attempt")
        try:
            if self._telegram_bot:
                await self._telegram_bot.application.bot.delete_webhook()
                _log_event("remove_telegram_webhook_success")
            return True
        except Exception as e:
            _log_event("remove_telegram_webhook_error", error=str(e), exc_info=True)
            return False

    def run(self) -> None:
        """
        Run the webhook server (blocking).

        Use this for simple single-server deployment.
        """
        _log_event("server_run_sync", host="0.0.0.0", port=self.port)
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )

    async def run_async(self) -> None:
        """
        Run the webhook server asynchronously.

        Use this when integrating with other async code.
        """
        _log_event("server_run_async", host="0.0.0.0", port=self.port)
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

