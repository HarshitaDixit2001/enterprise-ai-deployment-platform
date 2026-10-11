
from app.evaluation.dataset import EvaluationCase
from app.evaluation.runner import (
    Prediction,
    evaluate_predictions,
)
from app.models.use_case import UseCaseConfig
from app.services.release_gate import evaluate_release


def make_config() -> UseCaseConfig:
    return UseCaseConfig(
        use_case_id="customer-feedback",
        name="Customer Feedback Classification",
        business_objective=(
            "Classify feedback and route urgent complaints "
            "to the appropriate business team."
        ),
        risk_level="medium",
        evaluation_dataset="customer_feedback_v1",
    )


def make_cases() -> list[EvaluationCase]:
    return [
        EvaluationCase(
            case_id="CF-001",
            input="My invoice is incorrect.",
            expected_category="billing",
            expected_priority="high",
        ),
        EvaluationCase(
            case_id="CF-002",
            input="Someone accessed my account.",
            expected_category="security",
            expected_priority="critical",
        ),
    ]


def make_predictions(
    include_safety: bool = True,
    incorrect: bool = False,
) -> list[Prediction]:
    category = "general_feedback" if incorrect else "security"

    return [
        Prediction(
            case_id="CF-001",
            predicted_category=(
                "general_feedback" if incorrect else "billing"
            ),
            predicted_priority="high",
            latency_ms=500,
            cost_usd=0.01,
            safety_score=0.99 if include_safety else None,
        ),
        Prediction(
            case_id="CF-002",
            predicted_category=category,
            predicted_priority=(
                "low" if incorrect else "critical"
            ),
            latency_ms=600,
            cost_usd=0.02,
            safety_score=0.98 if include_safety else None,
        ),
    ]


def test_release_approved_when_all_checks_pass():
    report = evaluate_predictions(
        make_cases(),
        make_predictions(),
    )

    decision = evaluate_release(
        "candidate-v1",
        report,
        make_config(),
    )

    assert decision.decision == "approved"
    assert all(decision.checks.values())
    assert decision.reasons == []


def test_release_rejected_when_quality_is_too_low():
    report = evaluate_predictions(
        make_cases(),
        make_predictions(incorrect=True),
    )

    decision = evaluate_release(
        "candidate-v2",
        report,
        make_config(),
    )

    assert decision.decision == "rejected"
    assert decision.checks["task_success_rate"] is False
    assert any(
        "Task success rate" in reason
        for reason in decision.reasons
    )


def test_release_rejected_when_safety_evidence_is_missing():
    report = evaluate_predictions(
        make_cases(),
        make_predictions(include_safety=False),
    )

    decision = evaluate_release(
        "candidate-v3",
        report,
        make_config(),
    )

    assert decision.decision == "rejected"
    assert decision.checks["safety"] is False
