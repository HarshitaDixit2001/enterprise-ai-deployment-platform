from app.evaluation import health_check


def test_health_check_is_healthy_when_all_reports_are_ready(monkeypatch):
    monkeypatch.setattr(
        health_check,
        "generate_evaluation_summary",
        lambda: {
            "ready": True,
            "reports": {
                "baseline": {"status": "available"},
                "candidate_comparison": {"status": "available"},
                "error_analysis": {"status": "available"},
            },
            "missing_reports": [],
        },
    )

    result = health_check.check_evaluation_health()

    assert result["status"] == "healthy"
    assert result["reports_ready"] is True
    assert result["available_report_count"] == 3
    assert result["missing_reports"] == []
    assert result["invalid_reports"] == []


def test_health_check_is_degraded_when_reports_are_missing(monkeypatch):
    monkeypatch.setattr(
        health_check,
        "generate_evaluation_summary",
        lambda: {
            "ready": False,
            "reports": {
                "baseline": {"status": "available"},
            },
            "missing_reports": ["candidate_comparison", "error_analysis"],
        },
    )

    result = health_check.check_evaluation_health()

    assert result["status"] == "degraded"
    assert result["reports_ready"] is False
    assert result["available_report_count"] == 1
    assert result["missing_reports"] == [
        "candidate_comparison",
        "error_analysis",
    ]


def test_health_check_lists_invalid_reports(monkeypatch):
    monkeypatch.setattr(
        health_check,
        "generate_evaluation_summary",
        lambda: {
            "ready": False,
            "reports": {
                "baseline": {"status": "invalid"},
                "candidate_comparison": {"status": "available"},
            },
            "missing_reports": ["error_analysis"],
        },
    )

    result = health_check.check_evaluation_health()

    assert result["status"] == "degraded"
    assert result["invalid_reports"] == ["baseline"]
    assert result["missing_reports"] == ["error_analysis"]
