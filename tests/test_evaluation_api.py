from fastapi.testclient import TestClient

from app.main import app
import app.services.audit_service as audit_service
client = TestClient(app)


def create_test_use_case(use_case_id: str) -> None:
    response = client.post(
        "/use-cases",
        json={
            "use_case_id": use_case_id,
            "name": "Customer Feedback Classification",
            "business_objective": (
                "Classify customer feedback and route urgent "
                "complaints to the appropriate business team."
            ),
            "risk_level": "medium",
            "evaluation_dataset": "customer_feedback_v1",
        },
    )
    assert response.status_code == 201


def make_predictions() -> list[dict]:
    return [
        {
            "case_id": "CF-001",
            "predicted_category": "general_feedback",
            "predicted_priority": "low",
            "latency_ms": 100,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-002",
            "predicted_category": "billing",
            "predicted_priority": "high",
            "latency_ms": 120,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-003",
            "predicted_category": "technical_issue",
            "predicted_priority": "high",
            "latency_ms": 150,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-004",
            "predicted_category": "general_feedback",
            "predicted_priority": "low",
            "latency_ms": 110,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-005",
            "predicted_category": "security",
            "predicted_priority": "critical",
            "latency_ms": 180,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-006",
            "predicted_category": "billing",
            "predicted_priority": "medium",
            "latency_ms": 130,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-007",
            "predicted_category": "technical_issue",
            "predicted_priority": "medium",
            "latency_ms": 140,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-008",
            "predicted_category": "account_request",
            "predicted_priority": "medium",
            "latency_ms": 160,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-009",
            "predicted_category": "general_feedback",
            "predicted_priority": "medium",
            "latency_ms": 170,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
        {
            "case_id": "CF-010",
            "predicted_category": "account_request",
            "predicted_priority": "high",
            "latency_ms": 190,
            "cost_usd": 0.001,
            "safety_score": 0.99,
        },
    ]


def test_release_decision_endpoint_approves_good_candidate():
    use_case_id = "release-api-approved"
    create_test_use_case(use_case_id)

    response = client.post(
        f"/evaluations/{use_case_id}/release-decision",
        json={
            "candidate_id": "candidate-v1",
            "predictions": make_predictions(),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_id"] == "candidate-v1"
    assert body["decision"] == "approved"
    assert all(body["checks"].values())


def test_release_decision_rejects_missing_use_case():
    response = client.post(
        "/evaluations/unknown-use-case/release-decision",
        json={
            "candidate_id": "candidate-v1",
            "predictions": make_predictions(),
        },
    )

    assert response.status_code == 404


def test_release_decision_rejects_incomplete_predictions():
    use_case_id = "release-api-incomplete"
    create_test_use_case(use_case_id)

    response = client.post(
        f"/evaluations/{use_case_id}/release-decision",
        json={
            "candidate_id": "candidate-v1",
            "predictions": make_predictions()[:1],
        },
    )

    assert response.status_code == 422

def test_release_history_returns_recorded_decision(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "release_audit.jsonl",
    )

    use_case_id = "release-history-test"
    create_test_use_case(use_case_id)

    release_response = client.post(
        f"/evaluations/{use_case_id}/release-decision",
        json={
            "candidate_id": "candidate-history-1",
            "predictions": make_predictions(),
        },
    )

    assert release_response.status_code == 200

    history_response = client.get(
        f"/evaluations/{use_case_id}/history"
    )

    assert history_response.status_code == 200

    history = history_response.json()
    assert len(history) == 1
    assert history[0]["candidate_id"] == "candidate-history-1"
    assert history[0]["decision"] == "approved"
    assert history[0]["use_case_id"] == use_case_id
    assert "timestamp" in history[0]


def test_release_history_returns_empty_list_for_new_use_case(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "release_audit.jsonl",
    )

    use_case_id = "release-history-empty"
    create_test_use_case(use_case_id)

    response = client.get(
        f"/evaluations/{use_case_id}/history"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_release_history_returns_404_for_unknown_use_case():
    response = client.get(
        "/evaluations/unknown-history-case/history"
    )

    assert response.status_code == 404
