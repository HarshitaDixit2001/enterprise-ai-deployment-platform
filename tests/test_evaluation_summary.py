import json

from app.evaluation import summary


def test_summary_reports_missing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(summary, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(
        summary,
        "REPORT_FILES",
        {
            "baseline": tmp_path / "baseline.json",
            "candidate_comparison": tmp_path / "comparison.json",
            "error_analysis": tmp_path / "errors.json",
        },
    )

    result = summary.generate_evaluation_summary()

    assert result["ready"] is False
    assert set(result["missing_reports"]) == {
        "baseline",
        "candidate_comparison",
        "error_analysis",
    }


def test_summary_reads_available_reports(tmp_path, monkeypatch):
    report_path = tmp_path / "baseline.json"
    report_path.write_text(
        json.dumps(
            {
                "dataset": "customer_feedback_v1",
                "dataset_size": 10,
                "metrics": {"task_success_rate": 0.8},
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(summary, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(
        summary,
        "REPORT_FILES",
        {
            "baseline": report_path,
            "candidate_comparison": tmp_path / "comparison.json",
            "error_analysis": tmp_path / "errors.json",
        },
    )

    result = summary.generate_evaluation_summary()

    baseline = result["reports"]["baseline"]
    assert baseline["status"] == "available"
    assert baseline["dataset"] == "customer_feedback_v1"
    assert baseline["dataset_size"] == 10
    assert baseline["metrics"]["task_success_rate"] == 0.8
    assert result["ready"] is False


def test_summary_handles_invalid_json(tmp_path, monkeypatch):
    report_path = tmp_path / "baseline.json"
    report_path.write_text("{invalid json", encoding="utf-8")

    monkeypatch.setattr(summary, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(
        summary,
        "REPORT_FILES",
        {
            "baseline": report_path,
            "candidate_comparison": tmp_path / "comparison.json",
            "error_analysis": tmp_path / "errors.json",
        },
    )

    result = summary.generate_evaluation_summary()

    assert result["reports"]["baseline"]["status"] == "invalid"
    assert result["ready"] is False
