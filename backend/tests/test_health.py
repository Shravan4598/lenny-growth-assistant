from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    """The basic health endpoint should confirm application availability."""

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "application" in data
    assert "environment" in data
    assert "timestamp" in data


def test_root_endpoint_returns_application_metadata() -> None:
    """The root endpoint should expose basic service metadata."""

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["health"] == "/health"