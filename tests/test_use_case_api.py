
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def valid_payload() -> dict:
    return {
        "use_case_id": "customer-feedback",
        "name": "Customer Feedback Classification",
        "business_objective": (
            "Classify customer feedback and route urgent "
            "complaints to the appropriate business team."
        ),
        "risk_level": "medium",
        "evaluation_dataset": "customer_feedback_v1",
    }


def test_create_use_case():
    payload = valid_payload()
    payload["use_case_id"] = "customer-feedback-create"

    response = client.post("/use-cases", json=payload)

    assert response.status_code == 201
    assert response.json()["name"] == "Customer Feedback Classification"


def test_duplicate_use_case_is_rejected():
    payload = valid_payload()
    payload["use_case_id"] = "customer-feedback-duplicate"

    first = client.post("/use-cases", json=payload)
    second = client.post("/use-cases", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_get_missing_use_case_returns_404():
    response = client.get("/use-cases/does-not-exist")

    assert response.status_code == 404


def test_list_use_cases():
    payload = valid_payload()
    payload["use_case_id"] = "customer-feedback-list"

    client.post("/use-cases", json=payload)

    response = client.get("/use-cases")

    assert response.status_code == 200
    assert any(
        item["use_case_id"] == "customer-feedback-list"
        for item in response.json()
    )


def test_invalid_use_case_is_rejected():
    payload = valid_payload()
    payload["risk_level"] = "extreme"

    response = client.post("/use-cases", json=payload)

    assert response.status_code == 422
