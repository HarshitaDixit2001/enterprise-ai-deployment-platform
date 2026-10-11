
import pytest

from app.evaluation.dataset import EvaluationCase
from app.evaluation.runner import (
    Prediction,
    evaluate_predictions,
)


def make_case(
    case_id: str,
    category: str,
    priority: str,
) -> EvaluationCase:
    return EvaluationCase(
        case_id=case_id,
        input="Synthetic customer feedback.",
        expected_category=category,
        expected_priority=priority,
    )


def make_prediction(
    case_id: str,
    category: str,
    priority: str,
) -> Prediction:
    return Prediction(
        case_id=case_id,
        predicted_category=category,
        predicted_priority=priority,
        latency_ms=100,
        cost_usd=0.001,
    )


def test_perfect_predictions_score_one():
    cases = [
        make_case("CF-001", "billing", "high"),
        make_case("CF-002", "security", "critical"),
    ]
    predictions = [
        make_prediction("CF-001", "billing", "high"),
        make_prediction("CF-002", "security", "critical"),
    ]

    report = evaluate_predictions(cases, predictions)

    assert report.task_success_rate == 1.0
    assert report.category_accuracy == 1.0
    assert report.priority_accuracy == 1.0
    assert report.failed_case_ids == []


def test_incorrect_prediction_is_counted_as_failure():
    cases = [
        make_case("CF-001", "billing", "high"),
        make_case("CF-002", "security", "critical"),
    ]
    predictions = [
        make_prediction("CF-001", "billing", "high"),
        make_prediction("CF-002", "general_feedback", "low"),
    ]

    report = evaluate_predictions(cases, predictions)

    assert report.task_success_rate == 0.5
    assert report.failed_case_ids == ["CF-002"]


def test_missing_prediction_is_rejected():
    cases = [
        make_case("CF-001", "billing", "high"),
        make_case("CF-002", "security", "critical"),
    ]
    predictions = [
        make_prediction("CF-001", "billing", "high"),
    ]

    with pytest.raises(ValueError, match="exactly one result"):
        evaluate_predictions(cases, predictions)


def test_duplicate_prediction_is_rejected():
    cases = [make_case("CF-001", "billing", "high")]
    predictions = [
        make_prediction("CF-001", "billing", "high"),
        make_prediction("CF-001", "billing", "high"),
    ]

    with pytest.raises(ValueError, match="Duplicate prediction"):
        evaluate_predictions(cases, predictions)


def test_category_accuracy_is_reported_separately():
    cases = [
        make_case("CF-001", "billing", "high"),
        make_case("CF-002", "billing", "medium"),
    ]
    predictions = [
        make_prediction("CF-001", "billing", "high"),
        make_prediction("CF-002", "technical_issue", "medium"),
    ]

    report = evaluate_predictions(cases, predictions)

    assert report.category_accuracy == 0.5
    assert report.priority_accuracy == 1.0
    assert report.task_success_rate == 0.5
    assert report.per_category_accuracy["billing"] == 0.5
