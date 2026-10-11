
from app.evaluation.runner import EvaluationReport
from app.models.release import ReleaseDecision
from app.models.use_case import UseCaseConfig


def evaluate_release(
    candidate_id: str,
    report: EvaluationReport,
    config: UseCaseConfig,
) -> ReleaseDecision:
    criteria = config.criteria

    checks = {
        "task_success_rate": (
            report.task_success_rate
            >= criteria.min_task_success_rate
        ),
        "latency": (
            report.average_latency_ms
            <= criteria.max_latency_ms
        ),
        "cost": (
            report.average_cost_usd
            <= criteria.max_cost_per_task
        ),
        "safety": (
            report.average_safety_score is not None
            and report.average_safety_score
            >= criteria.min_safety_score
        ),
    }

    reasons = []

    for name, passed in checks.items():
        if not passed:
            if name == "task_success_rate":
                reasons.append(
                    "Task success rate is below the required threshold."
                )
            elif name == "latency":
                reasons.append(
                    "Average latency exceeds the configured limit."
                )
            elif name == "cost":
                reasons.append(
                    "Average cost per task exceeds the configured limit."
                )
            elif name == "safety":
                reasons.append(
                    "Safety evidence is missing or below the required threshold."
                )

    return ReleaseDecision(
        candidate_id=candidate_id,
        decision=(
            "approved" if all(checks.values()) else "rejected"
        ),
        reasons=reasons,
        checks=checks,
        evaluated_metrics={
            "task_success_rate": report.task_success_rate,
            "average_latency_ms": report.average_latency_ms,
            "average_cost_usd": report.average_cost_usd,
            "average_safety_score": report.average_safety_score,
        },
    )
