import logging
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

from src.integrations.telegram import webhook as webhook_mod
from src.integrations.telegram.webhook import WebhookServer


class DummyBot:
    """A minimal dummy bot exposing the new process_update_with_logging API for tests.

    Attributes:
        called: Whether the method was invoked.
        last_update: The last update object passed in.
        last_request_id: The last request_id passed in.
    """

    def __init__(self) -> None:
        self.called: bool = False
        self.last_update: Any = None
        self.last_request_id: Optional[str] = None

    async def process_update_with_logging(self, update: Any, request_id: Optional[str] = None) -> None:
        """Record invocation and capture the provided update and request_id.

        Args:
            update: The update object passed from the webhook.
            request_id: Optional request id propagated from the incoming HTTP request.

        Returns:
            None
        """
        self.called = True
        self.last_update = update
        self.last_request_id = request_id
        return None


def test_telegram_webhook_correlation_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify correlation ID generation/propagation and basic logging on the Telegram webhook endpoint.

    This test instantiates the WebhookServer, registers a minimal dummy bot by assigning it
    to server._telegram_bot, monkeypatches Update.de_json to avoid real Telegram parsing,
    and performs a POST to the webhook URL. It asserts that the response contains an
    X-Request-ID header, that the ID and the request path appear in logs, and that the
    dummy bot received the propagated request_id via process_update_with_logging.
    """
    caplog.set_level(logging.INFO)

    server = WebhookServer()
    dummy_bot = DummyBot()

    # Register the dummy bot directly on the server for the webhook to use
    setattr(server, "_telegram_bot", dummy_bot)

    # Monkeypatch Update.de_json to return a simple object and avoid complex Update construction
    original_de_json = getattr(webhook_mod.Update, "de_json", None)

    def fake_de_json(data: Dict[str, Any], bot: Any = None) -> Any:
        return {"fake_update": True}

    webhook_mod.Update.de_json = fake_de_json  # type: ignore

    client = TestClient(server.app)  # type: ignore

    try:
        response = client.post("/webhook/telegram", json={"update_id": 123})
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

        request_id = response.headers["X-Request-ID"]

        # Ensure logs include the request id and the request path/method
        log_text = caplog.text
        assert request_id in log_text
        assert "/webhook/telegram" in log_text

        # Verify the webhook invoked the new bot API and propagated the request id
        assert getattr(dummy_bot, "called", False) is True
        assert dummy_bot.last_request_id == request_id
    finally:
        # Restore original de_json if it existed
        if original_de_json is not None:
            webhook_mod.Update.de_json = original_de_json  # type: ignore
