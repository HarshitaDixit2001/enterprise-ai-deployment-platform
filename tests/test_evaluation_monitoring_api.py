from fastapi.testclient import TestClient

from app.main import app
from app.api import evaluations

client = TestClient(app)


def test_evaluation_summary_endpoint_returns_summary(monkeypatch):
    expected = {
        "ready": True,
        "reports": {
            "baseline": {"status": "available"},
            "candidate_comparison": {"status": "available"},
            "error_analysis": {"status": "available"},
        },
        "missing_reports": [],
        "limitations": [],
    }

    monkeypatch.setattr(
        evaluations,
        "generate_evaluation_summary",
        lambda: expected,
    )

    response = client.get("/evaluations/summary")

    assert response.status_code == 200
    assert response.json() == expected


def test_evaluation_health_endpoint_returns_healthy(monkeypatch):
    expected = {
        "status": "healthy",
        "reports_ready": True,
        "available_report_count": 3,
        "missing_reports": [],
        "invalid_reports": [],
    }

    monkeypatch.setattr(
        evaluations,
        "check_evaluation_health",
        lambda: expected,
    )

    response = client.get("/evaluations/health")

    assert response.status_code == 200
    assert response.json() == expected


def test_evaluation_health_endpoint_returns_503_when_degraded(monkeypatch):
    expected = {
        "status": "degraded",
        "reports_ready": False,
        "available_report_count": 2,
        "missing_reports": ["error_analysis"],
        "invalid_reports": [],
    }

    monkeypatch.setattr(
        evaluations,
        "check_evaluation_health",
        lambda: expected,
    )

    response = client.get("/evaluations/health")

    assert response.status_code == 503
    assert response.json() == expected


def test_evaluation_health_endpoint_returns_503_when_report_is_invalid(
    monkeypatch,
):
    expected = {
        "status": "degraded",
        "reports_ready": False,
        "available_report_count": 2,
        "missing_reports": [],
        "invalid_reports": ["baseline"],
    }

    monkeypatch.setattr(
        evaluations,
        "check_evaluation_health",
        lambda: expected,
    )

    response = client.get("/evaluations/health")

    assert response.status_code == 503
    assert response.json() == expected