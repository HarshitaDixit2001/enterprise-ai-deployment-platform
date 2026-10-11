import json

from app.evaluation import error_analysis


def test_generate_error_analysis_creates_report(tmp_path, monkeypatch):
    report_path = tmp_path / "error_analysis.json"
    monkeypatch.setattr(error_analysis, "REPORT_PATH", report_path)

    report = error_analysis.generate_error_analysis()

    assert report["dataset"] == "customer_feedback_v1"
    assert report["dataset_size"] > 0
    assert report["incorrect_case_count"] == len(report["errors"])
    assert 0.0 <= report["error_rate"] <= 1.0
    assert report_path.exists()

    saved_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved_report["dataset_size"] == report["dataset_size"]


def test_error_analysis_records_expected_and_predicted_labels(
    tmp_path, monkeypatch
):
    report_path = tmp_path / "error_analysis.json"
    monkeypatch.setattr(error_analysis, "REPORT_PATH", report_path)

    report = error_analysis.generate_error_analysis()

    for error in report["errors"]:
        assert error["case_id"]
        assert "expected_category" in error
        assert "predicted_category" in error
        assert "expected_priority" in error
        assert "predicted_priority" in error
        assert (
            error["category_correct"] is False
            or error["priority_correct"] is False
        )


def test_error_rate_is_zero_when_dataset_is_empty(tmp_path, monkeypatch):
    report_path = tmp_path / "error_analysis.json"
    monkeypatch.setattr(error_analysis, "REPORT_PATH", report_path)
    monkeypatch.setattr(error_analysis, "load_dataset", lambda: [])

    report = error_analysis.generate_error_analysis()

    assert report["dataset_size"] == 0
    assert report["incorrect_case_count"] == 0
    assert report["error_rate"] == 0.0
    assert report["errors"] == []
    assert report_path.exists()
