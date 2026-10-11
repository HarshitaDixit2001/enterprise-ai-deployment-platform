
import pytest
from pydantic import ValidationError

from app.models.use_case import (
    SuccessCriteria,
    UseCaseConfig,
)


def test_valid_use_case_configuration():
    config = UseCaseConfig(
        use_case_id="customer-feedback",
        name="Customer Feedback Classification",
        business_objective=(
            "Classify customer feedback and route urgent "
            "complaints to the appropriate business team."
        ),
        risk_level="medium",
        evaluation_dataset="customer_feedback_v1",
    )

    assert config.use_case_id == "customer-feedback"
    assert config.criteria.min_task_success_rate == 0.90
    assert config.requires_human_approval is True


def test_high_risk_use_case_requires_human_approval():
    with pytest.raises(ValidationError):
        UseCaseConfig(
            use_case_id="high-risk-workflow",
            name="High Risk Workflow",
            business_objective=(
                "Evaluate a high-risk workflow before release."
            ),
            risk_level="high",
            evaluation_dataset="high_risk_v1",
            requires_human_approval=False,
        )


def test_invalid_success_threshold_is_rejected():
    with pytest.raises(ValidationError):
        SuccessCriteria(min_task_success_rate=1.5)


def test_negative_latency_threshold_is_rejected():
    with pytest.raises(ValidationError):
        SuccessCriteria(max_latency_ms=-100)
