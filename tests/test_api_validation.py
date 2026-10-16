from fastapi.testclient import TestClient

from app.main import app


def test_invalid_json_returns_client_error():
    with TestClient(app) as client:
        response = client.post(
            "/evaluations/run",
            content="{invalid json",
            headers={"Content-Type": "application/json"},
        )

    assert 400 <= response.status_code < 500


def test_unknown_route_returns_404():
    with TestClient(app) as client:
        response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404


def test_health_endpoint_returns_success():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200