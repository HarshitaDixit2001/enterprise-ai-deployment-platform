import json
import pytest

import app.services.audit_service as audit_service
def test_audit_history_skips_json_values_that_are_not_objects(
    tmp_path, monkeypatch
):
    audit_path = tmp_path / "release_audit.jsonl"
    monkeypatch.setattr(audit_service, "AUDIT_LOG_PATH", audit_path)

    valid_record = {
        "timestamp": "2026-10-11T10:00:00+00:00",
        "use_case_id": "customer-feedback",
        "candidate_id": "candidate-valid",
        "decision": "approved",
        "reasons": [],
        "checks": {"safety": True},
        "evaluated_metrics": {"average_safety_score": 0.99},
    }

    audit_path.write_text(
        "null\n"
        + json.dumps(["unexpected", "list"])
        + "\n"
        + json.dumps(valid_record)
        + "\n",
        encoding="utf-8",
    )

    history = audit_service.list_release_decisions()

    assert len(history) == 1
    assert history[0]["candidate_id"] == "candidate-valid"