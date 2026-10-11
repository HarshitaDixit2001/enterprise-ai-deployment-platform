from fastapi.testclient import TestClient

from app.main import app
from app.services.audit_service import record_release_decision

client = TestClient(app)


def create_deployment_test_use_case(use_case_id: str) -> None:
    response = client.post(
        "/use-cases",
        json={
            "use_case_id": use_case_id,
            "name": "Customer Feedback Classification",
            "business_objective": (
                "Classify customer feedback and route urgent complaints "
                "to the appropriate business team."
            ),
            "risk_level": "medium",
            "evaluation_dataset": "customer_feedback_v1",
            "requires_human_approval": True,
        },
    )
    assert response.status_code == 201


def record_release(
    use_case_id: str,
    candidate_id: str,
    decision: str,
) -> None:
    record_release_decision(
        use_case_id=use_case_id,
        decision={
            "candidate_id": candidate_id,
            "decision": decision,
            "reasons": [],
            "checks": {},
            "evaluated_metrics": {},
        },
    )


def test_deployment_policy_api_permits_approved_candidate(monkeypatch, tmp_path):
    import app.services.audit_service as audit_service

    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "release_audit.jsonl",
    )

    use_case_id = "deployment-api-approved"
    create_deployment_test_use_case(use_case_id)
    record_release(use_case_id, "candidate-v1", "approved")

    response = client.post(
        f"/deployments/{use_case_id}/policy-check",
        json={
            "candidate_id": "candidate-v1",
            "human_approval_granted": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "permitted"


def test_deployment_policy_api_blocks_missing_human_approval(
    monkeypatch, tmp_path
):
    import app.services.audit_service as audit_service

    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "release_audit.jsonl",
    )

    use_case_id = "deployment-api-no-approval"
    create_deployment_test_use_case(use_case_id)
    record_release(use_case_id, "candidate-v2", "approved")

    response = client.post(
        f"/deployments/{use_case_id}/policy-check",
        json={
            "candidate_id": "candidate-v2",
            "human_approval_granted": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "blocked"


def test_deployment_policy_api_blocks_without_release_record(
    monkeypatch, tmp_path
):
    import app.services.audit_service as audit_service

    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "release_audit.jsonl",
    )

    use_case_id = "deployment-api-no-release"
    create_deployment_test_use_case(use_case_id)

    response = client.post(
        f"/deployments/{use_case_id}/policy-check",
        json={
            "candidate_id": "candidate-without-release",
            "human_approval_granted": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "blocked"
    assert body["checks"]["release_gate_approved"] is False


def test_deployment_policy_api_blocks_rejected_release(
    monkeypatch, tmp_path
):
    import app.services.audit_service as audit_service

    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "release_audit.jsonl",
    )

    use_case_id = "deployment-api-rejected"
    create_deployment_test_use_case(use_case_id)
    record_release(use_case_id, "candidate-v3", "rejected")

    response = client.post(
        f"/deployments/{use_case_id}/policy-check",
        json={
            "candidate_id": "candidate-v3",
            "human_approval_granted": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "blocked"


def test_deployment_policy_api_returns_404_for_unknown_use_case():
    response = client.post(
        "/deployments/unknown-deployment-case/policy-check",
        json={
            "candidate_id": "candidate-v1",
            "human_approval_granted": True,
        },
    )

    assert response.status_code == 404


def test_deployment_policy_api_rejects_invalid_request():
    response = client.post(
        "/deployments/deployment-api-invalid/policy-check",
        json={
            "candidate_id": "",
            "human_approval_granted": True,
        },
    )

    assert response.status_code == 422