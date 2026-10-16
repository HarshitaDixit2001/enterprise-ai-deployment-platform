import pytest
from pydantic import ValidationError

from app.evaluation.runner import EvaluationReport
from app.services.release_gate import evaluate_release

from tests.test_release_gate import make_config


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("task_success_rate", float("nan")),
        ("task_success_rate", float("inf")),
        ("average_latency_ms", float("inf")),
        ("average_cost_usd", float("nan")),
        ("average_safety_score", float("nan")),
        ("average_safety_score", 1.5),
        ("average_safety_score", -0.1),
    ],
)
def test_evaluation_report_rejects_invalid_metrics(field, value):
    metrics = {
        "total_cases": 2,
        "successful_cases": 2,
        "task_success_rate": 1.0,
        "category_accuracy": 1.0,
        "priority_accuracy": 1.0,
        "per_category_accuracy": {"billing": 1.0},
        "failed_case_ids": [],
        "average_latency_ms": 100.0,
        "average_cost_usd": 0.01,
        "average_safety_score": 0.99,
    }
    metrics[field] = value

    with pytest.raises(ValidationError):
        EvaluationReport(**metrics)


def test_release_rejects_missing_safety_evidence():
    report = EvaluationReport(
        total_cases=2,
        successful_cases=2,
        task_success_rate=1.0,
        category_accuracy=1.0,
        priority_accuracy=1.0,
        per_category_accuracy={"billing": 1.0},
        failed_case_ids=[],
        average_latency_ms=100.0,
        average_cost_usd=0.01,
        average_safety_score=None,
    )

    decision = evaluate_release(
        "candidate-missing-safety",
        report,
        make_config(),
    )

    assert decision.decision == "rejected"
    assert decision.checks["safety"] is False

def make_valid_report_data():
    return {
        "total_cases": 2,
        "successful_cases": 2,
        "task_success_rate": 1.0,
        "category_accuracy": 1.0,
        "priority_accuracy": 1.0,
        "per_category_accuracy": {"billing": 1.0},
        "failed_case_ids": [],
        "average_latency_ms": 100.0,
        "average_cost_usd": 0.01,
        "average_safety_score": 0.99,
    }

def test_report_rejects_more_successes_than_total_cases():
    metrics = make_valid_report_data()
    metrics["successful_cases"] = 3

    with pytest.raises(ValidationError):
        EvaluationReport(**metrics)


def test_report_rejects_incorrect_task_success_rate():
    metrics = make_valid_report_data()
    metrics["successful_cases"] = 1
    metrics["task_success_rate"] = 1.0

    with pytest.raises(ValidationError):
        EvaluationReport(**metrics)


def test_report_rejects_duplicate_failed_case_ids():
    metrics = make_valid_report_data()
    metrics["successful_cases"] = 0
    metrics["task_success_rate"] = 0.0
    metrics["failed_case_ids"] = ["CF-001", "CF-001"]

    with pytest.raises(ValidationError):
        EvaluationReport(**metrics)
