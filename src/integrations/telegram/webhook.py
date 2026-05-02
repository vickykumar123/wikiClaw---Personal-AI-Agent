# ============================================
# WEBHOOK SERVER - Single server for all platforms
# ============================================

import logging
import asyncio
import json
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

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

        # Create FastAPI app
        self.app = FastAPI(
            title="AI Agent Webhook Server",
            lifespan=self._lifespan
        )

        # Middleware to log each incoming HTTP request
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """
            Log HTTP request method, URL, and headers at DEBUG level.
            """
            logger.debug(
                "Incoming request: %s %s Headers: %s",
                request.method,
                request.url,
                dict(request.headers)
            )
            response = await call_next(request)
            return response

        # Register routes
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up webhook endpoints for each platform."""

        @self.app.get("/health")
        async def health_check(request: Request) -> Dict[str, str]:
            """Health check endpoint.

            Logs incoming health check request details at INFO level.

            Args:
                request: FastAPI Request object containing request metadata.

            Returns:
                A dictionary with a status key indicating service health.
            """
            logger.info(
                "Health check request - method: %s, path: %s, client_ip: %s",
                request.method,
                request.url.path,
                request.client.host if request.client else "unknown",
            )
            return {"status": "ok"}

        @self.app.post("/webhook/telegram")
        async def telegram_webhook(request: Request) -> Dict[str, bool]:
            """Handle incoming Telegram webhook.

            This endpoint processes updates sent by Telegram, logs request details,
            parses the update payload, forwards it to the bot's application for handling,
            and returns a confirmation response.

            Args:
                request (Request): FastAPI request containing the Telegram update
                    payload as JSON.

            Returns:
                Dict[str, bool]: A dictionary with a single key ``ok`` set to ``True``
                    when processing succeeds.

            Raises:
                HTTPException: If the Telegram bot is not configured (503) or if an
                    unexpected error occurs during processing (500).
            """
            # Log request details
            logger.info(
                "Telegram webhook request - method: %s, path: %s, client_ip: %s",
                request.method,
                request.url.path,
                request.client.host if request.client else "unknown",
            )
            logger.debug("Request headers: %s", dict(request.headers))

            if not self._telegram_bot:
                raise HTTPException(status_code=503, detail="Telegram bot not configured")

            try:
                    # Parse the update
                    data = await request.json()
                    logger.debug("Starting processing of Telegram webhook payload")
                    # Log receipt with truncated pretty JSON
                    try:
                        pretty = json.dumps(data, indent=2)
                    except Exception:
                        pretty = str(data)
                    logger.debug("Full Telegram webhook payload: %s", pretty)
                    logger.info("Received Telegram webhook: %s", pretty[:500])

                update = Update.de_json(data, self._telegram_bot.application.bot)

                # Log concise summary of the update (ID and type)
                try:
                    update_type = (
                        update.effective_message.__class__.__name__
                        if update.effective_message
                        else "unknown"
                    )
                except Exception:
                    update_type = "unknown"
                logger.info(
                    "Telegram update received: id=%s, type=%s",
                    getattr(update, "update_id", "N/A"),
                    update_type,
                )

                logger.debug("Telegram Update object: %s", update)

                # Import time for duration measurement
                from time import time
                start_time = time()
                logger.info("Processing Telegram update")
                logger.info(f"Processing Telegram Update ID: {getattr(update, 'update_id', 'N/A')}")
                await self._telegram_bot.application.process_update(update)
                logger.info("Telegram webhook processed successfully")
                duration = time() - start_time
                logger.info(
                    "Finished processing Telegram update (duration %.3f seconds)",
                    duration,
                )

                response_payload = {"ok": True}
                logger.info("Telegram webhook response payload: %s", response_payload)
                logger.debug("Returning response for Telegram webhook: {'ok': True}")
                return response_payload

            except Exception as e:
                logger.exception("Error processing Telegram webhook")
                raise HTTPException(status_code=500, detail=str(e))

        # Placeholder for future platforms
        @self.app.post("/webhook/whatsapp")
        async def whatsapp_webhook(request: Request):
            """Handle incoming WhatsApp webhook (future)."""
            logger.info("Received WhatsApp webhook request")
            # Log request method, path, and raw JSON body for debugging
            body_bytes = await request.body()
            try:
                body_str = body_bytes.decode()
            except Exception:
                body_str = str(body_bytes)
            logger.debug(
                "WhatsApp webhook request - method: %s, path: %s, body: %s",
                request.method,
                request.url.path,
                body_str,
            )
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
        logger.info("Webhook server startup sequence initiated")
        yield
        # Shutdown
        logger.info("Webhook server shutdown sequence initiated")
        await self._stop_ngrok()
        logger.info("Webhook server shutdown complete")

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

        logger.info(f"Starting ngrok tunnel on port {self.port}")
        # Start tunnel
        self.ngrok_tunnel = ngrok.connect(self.port, "http")
        self.webhook_url = self.ngrok_tunnel.public_url
        logger.debug(f"ngrok tunnel object: {self.ngrok_tunnel}")
        logger.debug(f"ngrok tunnel public URL: {self.ngrok_tunnel.public_url}")
        logger.debug(f"ngrok tunnel config: {self.ngrok_tunnel.config}")

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

            logger.debug(f"Setting Telegram webhook URL: {webhook_full_url}")
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
                logger.debug("Telegram webhook removal confirmed")
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
