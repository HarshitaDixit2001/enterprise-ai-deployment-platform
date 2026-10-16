from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_request_id_is_returned_in_response():
    response = client.get(
        "/health",
        headers={"X-Request-ID": "req-test-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-123"


def test_request_id_is_generated_when_missing():
    response = client.get("/health")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert request_id
    assert len(request_id) == 36


def test_invalid_request_id_is_replaced():
    response = client.get(
        "/health",
        headers={"X-Request-ID": "invalid request id!"},
    )

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]

    assert request_id != "invalid request id!"
    assert len(request_id) == 36


def test_overlong_request_id_is_replaced():
    supplied_id = "a" * 101

    response = client.get(
        "/health",
        headers={"X-Request-ID": supplied_id},
    )

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]

    assert request_id != supplied_id
    assert len(request_id) == 36
