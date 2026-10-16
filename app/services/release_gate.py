import math

from app.evaluation.runner import EvaluationReport
from app.models.release import ReleaseDecision
from app.models.use_case import UseCaseConfig


def evaluate_release(
    candidate_id: str,
    report: EvaluationReport,
    config: UseCaseConfig,
) -> ReleaseDecision:
    criteria = config.criteria

    task_success_rate = report.task_success_rate
    average_latency_ms = report.average_latency_ms
    average_cost_usd = report.average_cost_usd
    average_safety_score = report.average_safety_score

    def is_finite_number(value: object) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    task_success_valid = (
        is_finite_number(task_success_rate)
        and 0 <= task_success_rate <= 1
    )
    latency_valid = (
        is_finite_number(average_latency_ms)
        and average_latency_ms >= 0
    )
    cost_valid = (
        is_finite_number(average_cost_usd)
        and average_cost_usd >= 0
    )
    safety_valid = (
        average_safety_score is not None
        and is_finite_number(average_safety_score)
        and 0 <= average_safety_score <= 1
    )

    checks = {
        "task_success_rate": (
            task_success_valid
            and task_success_rate >= criteria.min_task_success_rate
        ),
        "latency": (
            latency_valid
            and average_latency_ms <= criteria.max_latency_ms
        ),
        "cost": (
            cost_valid
            and average_cost_usd <= criteria.max_cost_per_task
        ),
        "safety": (
            safety_valid
            and average_safety_score >= criteria.min_safety_score
        ),
    }

    reasons = []

    if not task_success_valid:
        reasons.append(
            "Task success rate is invalid; expected a finite value between 0 and 1."
        )
    elif not checks["task_success_rate"]:
        reasons.append(
            "Task success rate is below the required threshold."
        )

    if not latency_valid:
        reasons.append(
            "Average latency is invalid; expected a finite, non-negative value."
        )
    elif not checks["latency"]:
        reasons.append(
            "Average latency exceeds the configured limit."
        )

    if not cost_valid:
        reasons.append(
            "Average cost is invalid; expected a finite, non-negative value."
        )
    elif not checks["cost"]:
        reasons.append(
            "Average cost per task exceeds the configured limit."
        )

    if not safety_valid:
        reasons.append(
            "Safety evidence is missing or invalid; expected a finite value between 0 and 1."
        )
    elif not checks["safety"]:
        reasons.append(
            "Safety evidence is below the required threshold."
        )

    return ReleaseDecision(
        candidate_id=candidate_id,
        decision=(
            "approved" if all(checks.values()) else "rejected"
        ),
        reasons=reasons,
        checks=checks,
        evaluated_metrics={
            "task_success_rate": task_success_rate,
            "average_latency_ms": average_latency_ms,
            "average_cost_usd": average_cost_usd,
            "average_safety_score": average_safety_score,
        },
    )