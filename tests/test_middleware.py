
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging_config import request_id_context
from app.core.metrics import request_metrics
from app.middleware import RequestContextMiddleware


def create_test_app():
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/error")
    async def error():
        from fastapi import HTTPException

        raise HTTPException(
            status_code=500,
            detail="Simulated server error",
        )

    return app


def test_request_id_is_preserved():
    client = TestClient(create_test_app())

    response = client.get(
        "/ok",
        headers={"X-Request-ID": "test-request-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_invalid_request_id_is_replaced():
    client = TestClient(create_test_app())

    response = client.get(
        "/ok",
        headers={"X-Request-ID": "invalid request id"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "invalid request id"
    assert len(response.headers["X-Request-ID"]) > 0


def test_request_id_is_added_when_missing():
    client = TestClient(create_test_app())

    response = client.get("/ok")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]


def test_request_context_is_reset_after_request():
    client = TestClient(create_test_app())

    client.get(
        "/ok",
        headers={"X-Request-ID": "context-test-456"},
    )

    assert request_id_context.get() != "context-test-456"


def test_server_error_is_counted():
    client = TestClient(create_test_app())
    before = request_metrics.snapshot()["server_error_requests"]

    response = client.get("/error")

    after = request_metrics.snapshot()["server_error_requests"]

    assert response.status_code == 500
    assert after == before + 1


def test_not_found_is_not_counted_as_server_error():
    client = TestClient(create_test_app())
    before = request_metrics.snapshot()["server_error_requests"]

    response = client.get("/does-not-exist")

    after = request_metrics.snapshot()["server_error_requests"]

    assert response.status_code == 404
    assert after == before
