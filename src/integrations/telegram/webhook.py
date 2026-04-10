# ============================================
# WEBHOOK SERVER - Single server for all platforms
# ============================================

import logging
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
import logging
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import time

from constants import (
    DEFAULT_WEBHOOK_PORT,
    DEFAULT_WEBHOOK_PATH,
    MSG_WEBHOOK_SET,
    ERROR_WEBHOOK_SETUP,
)

# Request tracking enabled
REQUEST_COUNT = 0

# Set up logging
logger = logging.getLogger(__name__)

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
        self.requests_handled = 0

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
            return {"status": "ok"}

        @self.app.get("/healthz")
        async def healthz_check():
            """Extended health check endpoint."""
            return {"status": "healthy", "uptime": "ok"}

        @self.app.get("/metrics")
        async def metrics():
            """Metrics endpoint."""
            return {"requests_handled": self.requests_handled}

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
                update = Update.de_json(data, self._telegram_bot.application.bot)

                # Process the update
                await self._telegram_bot.application.process_update(update)

                self.requests_handled += 1

                return {"ok": True}

            except Exception as e:
                logger.error(f"Error processing Telegram webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Placeholder for future platforms
        @self.app.post("/webhook/whatsapp")
        async def whatsapp_webhook(request: Request):
            """Handle incoming WhatsApp webhook (future)."""
            return {"ok": True, "message": "WhatsApp webhook not implemented yet"}

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """
        Manage server startup and shutdown.

        - On startup: Start ngrok tunnel
        - On shutdown: Close tunnel
        """
        # Startup
        logger.info(f"Starting webhook server on port {self.port}")
        yield
        # Shutdown
        await self._stop_ngrok()

    def register_telegram_bot(self, bot) -> None:
        """
        Register Telegram bot to receive webhooks.

        Args:
            bot: TelegramBot instance
        """
        self._telegram_bot = bot
        logger.info("Telegram bot registered with webhook server")

    async def start_ngrok(self) -> str:
        """
        Start ngrok tunnel and return public URL.

        Returns:
            Public HTTPS URL for webhooks
        """
        if self.ngrok_auth_token:
            ngrok.set_auth_token(self.ngrok_auth_token)

        # Start tunnel
        self.ngrok_tunnel = ngrok.connect(self.port, "http")
        self.webhook_url = self.ngrok_tunnel.public_url

        # Ensure HTTPS
        if self.webhook_url.startswith("http://"):
            self.webhook_url = self.webhook_url.replace("http://", "https://")

        logger.info(f"ngrok tunnel started: {self.webhook_url}")
        return self.webhook_url

    async def _stop_ngrok(self) -> None:
        """Stop ngrok tunnel."""
        if self.ngrok_tunnel:
            ngrok.disconnect(self.ngrok_tunnel.public_url)
            logger.info("ngrok tunnel stopped")

    async def set_telegram_webhook(self) -> bool:
        """
        Set webhook URL with Telegram.

        Returns:
            True if successful
        """
        if not self._telegram_bot or not self.webhook_url:
            logger.error(ERROR_WEBHOOK_SETUP)
            return False

        try:
            webhook_full_url = f"{self.webhook_url}/webhook/telegram"

            await self._telegram_bot.application.bot.set_webhook(
                url=webhook_full_url
            )

            logger.info(f"{MSG_WEBHOOK_SET}: {webhook_full_url}")
            return True

        except Exception as e:
            logger.error(f"{ERROR_WEBHOOK_SETUP}: {e}")
            return False

    async def remove_telegram_webhook(self) -> bool:
        """
        Remove webhook from Telegram.

        Returns:
            True if successful
        """
        try:
            if self._telegram_bot:
                await self._telegram_bot.application.bot.delete_webhook()
                logger.info("Telegram webhook removed")
            return True
        except Exception as e:
            logger.error(f"Failed to remove webhook: {e}")
            return False

    def run(self) -> None:
        """
        Run the webhook server (blocking).

        Use this for simple single-server deployment.
        """
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
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
