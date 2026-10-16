from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exception_handlers import register_exception_handlers


def create_test_app() -> FastAPI:
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/http-error")
    async def http_error():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Resource not found.")

    @test_app.get("/unexpected-error")
    async def unexpected_error():
        raise RuntimeError("sensitive internal implementation detail")

    @test_app.get("/items/{item_id}")
    async def get_item(item_id: int):
        return {"item_id": item_id}

    return test_app


def test_http_exception_uses_standard_error_format():
    client = TestClient(create_test_app())
    response = client.get("/http-error")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "HTTP_ERROR",
            "message": "Resource not found.",
        }
    }


def test_unexpected_exception_hides_internal_details():
    client = TestClient(
        create_test_app(),
        raise_server_exceptions=False,
    )
    response = client.get("/unexpected-error")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        }
    }
    assert "sensitive internal implementation detail" not in response.text


def test_request_validation_uses_standard_error_format():
    client = TestClient(create_test_app())
    response = client.get("/items/not-an-integer")

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "The request contains invalid or missing fields.",
        }
    }
