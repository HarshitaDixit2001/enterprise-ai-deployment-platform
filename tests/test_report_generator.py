import json

from app.evaluation import report_generator


def test_report_generation_writes_reproducible_metrics(
    tmp_path,
    monkeypatch,
):
    report_path = tmp_path / "baseline_evaluation.json"

    monkeypatch.setattr(
        report_generator,
        "REPORT_PATH",
        report_path,
    )

    result = report_generator.generate_report()

    assert result["dataset"] == "customer_feedback_v1"
    assert result["dataset_size"] == 10
    assert result["model_type"] == "deterministic_keyword_baseline"
    assert result["metrics"]["total_cases"] == 10
    assert 0.0 <= result["metrics"]["task_success_rate"] <= 1.0
    assert result["metrics"]["average_safety_score"] is None

    saved = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved["dataset_size"] == 10
    assert saved["limitations"]


def test_baseline_prediction_does_not_invent_safety_score():
    from app.evaluation.baseline_predictor import predict_feedback
    from app.evaluation.dataset import load_dataset

    prediction = predict_feedback(load_dataset()[0])

    assert prediction.safety_score is None
    assert prediction.cost_usd == 0.0
