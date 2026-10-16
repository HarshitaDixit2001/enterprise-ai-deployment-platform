from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exception_handlers import register_exception_handlers

from fastapi.testclient import TestClient
from app.main import app
def test_unexpected_error_does_not_expose_internal_details():
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/simulate-failure")
    async def simulate_failure():
        raise RuntimeError("database_password=super-secret-value")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/simulate-failure")

    assert response.status_code == 500
    assert "super-secret-value" not in response.text
    assert "database_password" not in response.text
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        }
    }



def test_internal_exception_details_are_not_exposed():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert "SECRET_DATABASE_PASSWORD" not in response.text
