from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_readiness_returns_degraded_when_database_is_unavailable(
    monkeypatch,
) -> None:
    """Readiness should return 503 when PostgreSQL is unavailable."""

    monkeypatch.setattr(
        "app.api.routes.health.check_database_connection",
        lambda: False,
    )

    response = client.get("/health/ready")

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "degraded"
    assert data["database"] == "unavailable"


def test_readiness_returns_ok_when_database_is_available(
    monkeypatch,
) -> None:
    """Readiness should return 200 when PostgreSQL is available."""

    monkeypatch.setattr(
        "app.api.routes.health.check_database_connection",
        lambda: True,
    )

    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] == "available"
    assert data["llm_provider"] == "ollama"