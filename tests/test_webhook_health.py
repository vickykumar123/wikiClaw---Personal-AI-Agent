import pytest
from typing import Generator

from fastapi.testclient import TestClient

from webhook_server import WebhookServer


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a TestClient for the WebhookServer FastAPI app.

    Yields:
        TestClient: The test client instance.
    """
    server = WebhookServer()
    with TestClient(server.app) as client:
        yield client


def test_health_endpoint(client: TestClient) -> None:
    """Test that the /health endpoint returns status 200 and the expected JSON payload."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
