import json

import app.services.audit_service as audit_service


def test_record_and_list_release_decisions(tmp_path, monkeypatch):
    audit_path = tmp_path / "release_audit.jsonl"
    monkeypatch.setattr(audit_service, "AUDIT_LOG_PATH", audit_path)

    decision = {
        "candidate_id": "candidate-test",
        "decision": "approved",
        "reasons": [],
        "checks": {
            "task_success_rate": True,
            "latency": True,
            "cost": True,
            "safety": True,
        },
        "evaluated_metrics": {
            "task_success_rate": 1.0,
            "average_latency_ms": 100.0,
            "average_cost_usd": 0.001,
            "average_safety_score": 0.99,
        },
    }

    recorded = audit_service.record_release_decision(
        decision=decision,
        use_case_id="customer-feedback",
    )

    assert recorded["candidate_id"] == "candidate-test"
    assert recorded["use_case_id"] == "customer-feedback"
    assert "timestamp" in recorded

    history = audit_service.list_release_decisions(
        "customer-feedback"
    )

    assert len(history) == 1
    assert history[0]["decision"] == "approved"


def test_audit_history_filters_by_use_case(tmp_path, monkeypatch):
    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "release_audit.jsonl",
    )

    base_decision = {
        "candidate_id": "candidate-1",
        "decision": "rejected",
        "reasons": ["Quality threshold not met"],
        "checks": {"task_success_rate": False},
        "evaluated_metrics": {"task_success_rate": 0.5},
    }

    audit_service.record_release_decision(
        base_decision,
        "use-case-a",
    )
    audit_service.record_release_decision(
        base_decision,
        "use-case-b",
    )

    filtered = audit_service.list_release_decisions("use-case-a")
    all_records = audit_service.list_release_decisions()

    assert len(filtered) == 1
    assert filtered[0]["use_case_id"] == "use-case-a"
    assert len(all_records) == 2


def test_missing_audit_log_returns_empty_list(tmp_path, monkeypatch):
    monkeypatch.setattr(
        audit_service,
        "AUDIT_LOG_PATH",
        tmp_path / "missing.jsonl",
    )

    assert audit_service.list_release_decisions() == []
