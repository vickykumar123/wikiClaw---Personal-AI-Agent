import logging
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from src.integrations.telegram import webhook as webhook_mod
from src.integrations.telegram.webhook import WebhookServer


class DummyApplication:
    def __init__(self) -> None:
        self.bot: Any = object()
        self.called: bool = False
        self.last_update: Any = None

    async def process_update(self, update: Any) -> None:
        """Simulate processing an update by recording it was called."""
        self.called = True
        self.last_update = update


class DummyBot:
    def __init__(self) -> None:
        self.application = DummyApplication()


def test_telegram_webhook_correlation_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify correlation ID generation/propagation and basic logging on the Telegram webhook endpoint.

    This test instantiates the WebhookServer, registers a minimal dummy bot, monkeypatches
    Update.de_json to avoid real Telegram parsing, and performs a POST to the webhook URL.
    It asserts that the response contains an X-Request-ID header and that that ID plus the
    request path appear in the captured logs.
    """
    caplog.set_level(logging.INFO)

    server = WebhookServer()
    dummy_bot = DummyBot()

    # Try a few possible registration method names to be resilient to implementation details
    if hasattr(server, "register_bot"):
        server.register_bot("dummy", dummy_bot)
    elif hasattr(server, "register"):
        server.register("dummy", dummy_bot)
    elif hasattr(server, "add_bot"):
        server.add_bot("dummy", dummy_bot)
    else:
        # Best-effort fallback: attach to a bots mapping if present or set an attribute
        try:
            if hasattr(server, "bots") and isinstance(server.bots, dict):
                server.bots["dummy"] = dummy_bot
            else:
                setattr(server, "bots", {"dummy": dummy_bot})
        except Exception:
            # If registration is not necessary for the route to exist, continue
            pass

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
    finally:
        # Restore original de_json if it existed
        if original_de_json is not None:
            webhook_mod.Update.de_json = original_de_json  # type: ignore
