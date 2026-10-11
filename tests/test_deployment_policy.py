from app.models.deployment import DeploymentDecision
from app.models.use_case import UseCaseConfig
from app.services.deployment_policy import evaluate_deployment_policy


def make_config(
    risk_level: str = "medium",
    requires_human_approval: bool = True,
) -> UseCaseConfig:
    return UseCaseConfig(
        use_case_id="test-deployment",
        name="Customer Feedback Classification",
        business_objective=(
            "Classify customer feedback and route urgent complaints "
            "to the appropriate business team."
        ),
        risk_level=risk_level,
        evaluation_dataset="customer_feedback_v1",
        requires_human_approval=requires_human_approval,
    )


def test_deployment_blocked_without_human_approval():
    decision = evaluate_deployment_policy(
        candidate_id="candidate-v1",
        release_approved=True,
        human_approval_granted=False,
        config=make_config(),
    )

    assert decision.decision == "blocked"
    assert decision.checks["human_approval"] is False


def test_deployment_permitted_when_all_required_checks_pass():
    decision = evaluate_deployment_policy(
        candidate_id="candidate-v2",
        release_approved=True,
        human_approval_granted=True,
        config=make_config(),
    )

    assert decision.decision == "permitted"
    assert all(decision.checks.values())


def test_deployment_blocked_when_release_gate_rejects_candidate():
    decision = evaluate_deployment_policy(
        candidate_id="candidate-v3",
        release_approved=False,
        human_approval_granted=True,
        config=make_config(),
    )

    assert decision.decision == "blocked"
    assert decision.checks["release_gate_approved"] is False


def test_low_risk_use_case_can_skip_human_approval():
    decision = evaluate_deployment_policy(
        candidate_id="candidate-v4",
        release_approved=True,
        human_approval_granted=False,
        config=make_config(
            risk_level="low",
            requires_human_approval=False,
        ),
    )

    assert decision.decision == "permitted"
    assert decision.checks["human_approval"] is True


def test_high_risk_use_case_cannot_disable_human_approval():
    from pydantic import ValidationError
    import pytest

    with pytest.raises(ValidationError):
        make_config(
            risk_level="high",
            requires_human_approval=False,
        )