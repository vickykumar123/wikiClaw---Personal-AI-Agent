# ============================================
# WEBHOOK SERVER - Single server for all platforms
# ============================================

import logging
import asyncio
import json
import time
import traceback
from typing import Optional, Dict, Any, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Response
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
logger = logging.getLogger("wikiClaw.webhook")

# Constants for truncation and sensitive headers
BODY_TRUNCATE_LEN = 200
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "proxy-authorization"}


def sanitize_headers(headers: Dict[str, Any]) -> Dict[str, str]:
    """
    Return a sanitized copy of headers with sensitive values redacted and long
    values truncated.

    Args:
        headers: Original headers mapping.

    Returns:
        A new dict mapping header names (lowercased) to string values that are
        safe for logging.
    """
    sanitized: Dict[str, str] = {}
    for key, value in headers.items():
        k = key.lower()
        try:
            v = value.decode() if isinstance(value, (bytes, bytearray)) else str(value)
        except Exception:
            v = "<unserializable>"
        if k in SENSITIVE_HEADERS:
            sanitized[k] = "<redacted>"
        else:
            if len(v) > BODY_TRUNCATE_LEN:
                sanitized[k] = v[:BODY_TRUNCATE_LEN] + "...(truncated)"
            else:
                sanitized[k] = v
    return sanitized


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

        # Register request/response logging middleware
        @self.app.middleware("http")
        async def request_logging_middleware(request: Request, call_next: Callable[[Request], Response]) -> Response:
            """
            Middleware that logs incoming requests, outgoing responses, and
            exceptions with contextual request information.

            Logs:
            - Incoming: timestamp, method, path, client IP, sanitized headers,
              content-type, truncated body.
            - Outgoing: status code, truncated body, latency (ms).
            - Exceptions: full stack trace and the same request context.

            Args:
                request: Incoming FastAPI request.
                call_next: Callable to invoke the next handler and obtain a response.

            Returns:
                The HTTP response to return to the client.
            """
            start_ts = time.time()
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(start_ts))
            client_ip = request.client.host if request.client else "unknown"

            try:
                body_bytes = await request.body()
            except Exception:
                body_bytes = b""

            try:
                body_text = body_bytes.decode(errors='replace')
            except Exception:
                body_text = "<unserializable>"

            truncated_body = body_text if len(body_text) <= BODY_TRUNCATE_LEN else body_text[:BODY_TRUNCATE_LEN] + "...(truncated)"
            headers = dict(request.headers)
            sanitized = sanitize_headers(headers)
            content_type = headers.get("content-type") or headers.get("Content-Type") or ""

            logger.info("Incoming request",
                        extra={
                            "timestamp": timestamp,
                            "method": request.method,
                            "path": request.url.path,
                            "client_ip": client_ip,
                            "headers": sanitized,
                            "content_type": content_type,
                            "body": truncated_body,
                        })

            # Re-create request with the captured body so downstream can read it
            async def _receive() -> dict:
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            req_with_body = Request(request.scope, receive=_receive)

            try:
                response = await call_next(req_with_body)

                # Capture response body (may be streamed)
                resp_body = b""
                async for chunk in response.body_iterator:
                    resp_body += chunk

                try:
                    resp_text = resp_body.decode(errors='replace')
                except Exception:
                    resp_text = "<unserializable>"

                truncated_resp = resp_text if len(resp_text) <= BODY_TRUNCATE_LEN else resp_text[:BODY_TRUNCATE_LEN] + "...(truncated)"
                latency_ms = int((time.time() - start_ts) * 1000)

                logger.info("Outgoing response",
                            extra={
                                "status_code": response.status_code,
                                "body": truncated_resp,
                                "latency_ms": latency_ms,
                            })

                # Rebuild response to send to client since we consumed the iterator
                new_response = Response(
                    content=resp_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
                return new_response

            except Exception as e:  # noqa: BLE
                latency_ms = int((time.time() - start_ts) * 1000)
                logger.exception("Exception during request processing",
                                 extra={
                                     "timestamp": timestamp,
                                     "method": request.method,
                                     "path": request.url.path,
                                     "client_ip": client_ip,
                                     "headers": sanitized,
                                     "content_type": content_type,
                                     "body": truncated_body,
                                     "latency_ms": latency_ms,
                                 })
                raise

        # Register routes
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up webhook endpoints for each platform."""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            logger.info('Health check requested')
            return {"status": "ok"}

        @self.app.post("/webhook/telegram")
        async def telegram_webhook(request: Request):
            """
            Handle incoming Telegram webhook.

            Telegram sends updates as JSON POST requests.
            """
            if not self._telegram_bot:
                logger.warning("Telegram bot not configured")
                raise HTTPException(status_code=503, detail="Telegram bot not configured")

            update = None
            try:
                # Parse the update
                data = await request.json()
                logger.debug(f"Telegram webhook payload: {str(data)[:200]}")
                update = Update.de_json(data, self._telegram_bot.application.bot)

                # Process the update
                await self._telegram_bot.application.process_update(update)

                return {"ok": True}

            except Exception as e:
                # Log full stack trace and request context
                if update is not None and hasattr(update, "update_id"):
                    logger.exception("Error processing Telegram webhook",
                                     extra={
                                         "client_ip": getattr(request.client, "host", "unknown"),
                                         "update_id": update.update_id,
                                     })
                else:
                    logger.exception(f"Error processing Telegram webhook from {getattr(request.client, 'host', 'unknown')}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Placeholder for future platforms
        @self.app.post("/webhook/whatsapp")
        async def whatsapp_webhook(request: Request):
            """Handle incoming WhatsApp webhook (future)."""
            logger.info("Received WhatsApp webhook request")
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

        try:
            logger.info(f"Starting ngrok tunnel on port {self.port}")
            logger.debug(f"Attempting to start ngrok tunnel on port {self.port}")
            # Start tunnel
            self.ngrok_tunnel = ngrok.connect(self.port, "http")
            self.webhook_url = self.ngrok_tunnel.public_url
            logger.debug(f"ngrok public URL obtained: {self.webhook_url}")

            # Ensure HTTPS
            if self.webhook_url.startswith("http://"):
                self.webhook_url = self.webhook_url.replace("http://", "https://")

            logger.info(f"ngrok tunnel started: {self.webhook_url}")
            return self.webhook_url
        except Exception as e:
            logger.exception(f"Failed to start ngrok tunnel: {e}")
            raise

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

            logger.info(f"Attempting to set Telegram webhook: {webhook_full_url}")

            logger.debug(f"Setting Telegram webhook to URL: {webhook_full_url}")
            await self._telegram_bot.application.bot.set_webhook(
                url=webhook_full_url
            )
            logger.debug(f"Telegram webhook set successfully: {webhook_full_url}")

            logger.info(f"{MSG_WEBHOOK_SET}: {webhook_full_url}")
            return True

        except Exception as e:
            logger.exception(f"{ERROR_WEBHOOK_SETUP}: {e}")
            return False

    async def remove_telegram_webhook(self) -> bool:
        """
        Remove webhook from Telegram.

        Returns:
            True if successful
        """
        try:
            if self._telegram_bot:
                logger.info("Removing Telegram webhook")
                logger.debug("Attempting to delete Telegram webhook")
                await self._telegram_bot.application.bot.delete_webhook()
                logger.debug("Telegram webhook successfully deleted")
                logger.info("Telegram webhook removed")
            return True
        except Exception as e:
            logger.exception(f"Failed to remove webhook: {e}")
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
