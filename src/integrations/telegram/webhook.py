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

import uuid
import time
from datetime import datetime
import traceback
from typing import Iterable


def _generate_request_id() -> str:
    """Generate and return a UUID4 string.

    Returns:
        A UUID4 string suitable for use as a request identifier.
    """
    return str(uuid.uuid4())


def _sanitize_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of headers with Authorization and Cookie keys removed.

    Keys are matched case-insensitively. Other headers are preserved as-is.

    Args:
        headers: Mapping of header names to values.

    Returns:
        A new dictionary containing the sanitized headers.
    """
    if not headers:
        return {}
    sanitized: Dict[str, Any] = {}
    sensitive = {"authorization", "cookie"}
    for k, v in headers.items():
        if not isinstance(k, str):
            # Preserve non-string keys as-is
            sanitized[k] = v
            continue
        if k.lower() in sensitive:
            continue
        sanitized[k] = v
    return sanitized


def _redact_sensitive(
    data: Any,
    keys_to_redact: Iterable[str] = (
        "password",
        "token",
        "access_token",
        "auth",
        "api_key",
        "secret",
        "email",
    ),
) -> Any:
    """Recursively redact sensitive values in structures.

    Walks dictionaries and lists/tuples/sets and replaces values for keys
    matching any of ``keys_to_redact`` with the string "<REDACTED>". Key
    matching is case-insensitive. Non-dict/list primitives are returned as-is.

    Args:
        data: The data structure to redact.
        keys_to_redact: Iterable of key names to redact when encountered in dicts.

    Returns:
        A new data structure with sensitive values replaced by "<REDACTED>".
    """
    lower_keys = {k.lower() for k in keys_to_redact}

    if isinstance(data, dict):
        result: Dict[Any, Any] = {}
        for k, v in data.items():
            if isinstance(k, str) and k.lower() in lower_keys:
                result[k] = "<REDACTED>"
            else:
                result[k] = _redact_sensitive(v, keys_to_redact)
        return result

    if isinstance(data, list):
        return [_redact_sensitive(x, keys_to_redact) for x in data]

    if isinstance(data, tuple):
        return tuple(_redact_sensitive(x, keys_to_redact) for x in data)

    if isinstance(data, set):
        # Convert to list to avoid issues with unhashable redacted items
        return [_redact_sensitive(x, keys_to_redact) for x in data]

    # Primitives (str, int, float, bool, None) are safe to return as-is
    return data


def _summarize_body(data: Any, max_chars: int = 500) -> Dict[str, Any]:
    """Produce a small summary of a request/response body for logging.

    The summary intentionally avoids exposing sensitive values by using
    ``_redact_sensitive`` where appropriate. The returned summary is shallow and
    intended for safe logging (previewing strings, listing top-level keys,
    indicating types, and providing counts for sequences).

    Args:
        data: The body to summarize (dict, list, str, number, etc.).
        max_chars: Maximum number of characters to include for string previews.

    Returns:
        A dictionary containing a concise summary suitable for logs.
    """
    if isinstance(data, dict):
        keys = list(data.keys())
        types = {k: type(v).__name__ for k, v in data.items()}
        # Create a shallow redacted copy for preview
        redacted = _redact_sensitive(data)
        sample: Dict[str, Any] = {}
        for k, v in redacted.items():
            if isinstance(v, str):
                sample[k] = v[:max_chars]
            elif isinstance(v, (int, float, bool)) or v is None:
                sample[k] = v
            else:
                sample[k] = f"<{type(v).__name__}>"
        return {"type": "dict", "keys": keys, "types": types, "sample": sample}

    if isinstance(data, list):
        sample_types = [type(x).__name__ for x in data[:5]]
        return {"type": "list", "length": len(data), "sample_types": sample_types}

    if isinstance(data, str):
        return {"type": "str", "preview": data[:max_chars]}

    if data is None:
        return {"type": "none"}

    if isinstance(data, (int, float, bool)):
        return {"type": type(data).__name__, "value": data}

    # Fallback for other object types
    try:
        text = str(data)
    except Exception:
        text = f"<{type(data).__name__}>"
    return {"type": type(data).__name__, "preview": text[:max_chars]}


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
            # Structured logging: generate identifiers and timing
            request_id: str = _generate_request_id()
            timestamp: str = datetime.utcnow().isoformat() + "Z"
            start_time: float = time.time()

            # Safely obtain and sanitize headers
            raw_headers: Dict[str, Any]
            hdr_list = getattr(request.headers, "_list", None)
            if hdr_list:
                try:
                    raw_headers = dict(hdr_list)
                except Exception:
                    raw_headers = dict(request.headers)
            else:
                raw_headers = dict(request.headers)
            sanitized_headers: Dict[str, Any] = _sanitize_headers(raw_headers)

            # Query params
            query_params: Dict[str, Any] = dict(request.query_params)

            if not self._telegram_bot:
                raise HTTPException(status_code=503, detail="Telegram bot not configured")

            try:
                # Parse body safely: try raw body -> json.loads, then fallback to request.json()
                body_bytes = await request.body()
                raw_data: Any = {}
                try:
                    try:
                        body_text = body_bytes.decode("utf-8")
                    except Exception:
                        body_text = body_bytes.decode("utf-8", errors="replace")
                    raw_data = json.loads(body_text) if body_text else {}
                except Exception:
                    try:
                        raw_data = await request.json()
                    except Exception:
                        raw_data = {}

                # Create redacted copy for logging and summary
                redacted_body: Any = _redact_sensitive(raw_data)
                body_summary: Dict[str, Any] = _summarize_body(redacted_body)

                # Log incoming structured message
                incoming_log = {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "method": request.method,
                    "path": request.url.path,
                    "headers": sanitized_headers,
                    "query_params": query_params,
                    "body_summary": body_summary,
                }
                logger.info(json.dumps(incoming_log, default=str))

                # Build Update from original (unredacted) payload and process
                update = Update.de_json(raw_data, self._telegram_bot.application.bot)

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

                # Process the update and measure duration
                await self._telegram_bot.application.process_update(update)

                duration: float = time.time() - start_time
                response_body: Dict[str, bool] = {"ok": True}
                response_summary: Dict[str, Any] = _summarize_body(response_body)

                success_log = {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "status_code": 200,
                    "response_summary": response_summary,
                    "duration": duration,
                }
                logger.info(json.dumps(success_log, default=str))

                return response_body

            except Exception as e:
                # Capture stack trace and log structured error without sensitive values
                stack = traceback.format_exc()
                error_log = {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "method": request.method,
                    "path": request.url.path,
                    "headers": sanitized_headers,
                    "query_params": query_params,
                    "exception": str(e),
                    "stack_trace": stack,
                }
                # Ensure we do not log unredacted body or sensitive headers here
                logger.error(json.dumps(error_log, default=str))
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
