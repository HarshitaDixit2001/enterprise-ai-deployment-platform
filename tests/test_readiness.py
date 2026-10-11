from fastapi.testclient import TestClient

from app.main import app
from app.services import readiness_service

client = TestClient(app)


def test_readiness_returns_ready_when_checks_pass(monkeypatch):
    monkeypatch.setattr(
        readiness_service,
        "load_named_dataset",
        lambda name: [object()],
    )

    def fake_audit_directory():
        return None

    monkeypatch.setattr(
        readiness_service.AUDIT_LOG_PATH.parent,
        "mkdir",
        fake_audit_directory,
    ) if False else None

    # Use a temporary writable directory for the audit check.
    from pathlib import Path

    monkeypatch.setattr(
        readiness_service,
        "AUDIT_LOG_PATH",
        Path(__file__).parent / ".test_release_audit.jsonl",
    )

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["checks"]["evaluation_dataset"]["status"] == "ready"
    assert response.json()["checks"]["audit_storage"]["status"] == "ready"


def test_readiness_returns_not_ready_when_dataset_fails(monkeypatch):
    def fail_to_load(name):
        raise FileNotFoundError("Dataset missing")

    monkeypatch.setattr(
        readiness_service,
        "load_named_dataset",
        fail_to_load,
    )

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["checks"]["evaluation_dataset"]["status"] == "not_ready"
