import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from app.evaluation.baseline_predictor import predict_feedback
from app.evaluation.dataset import EvaluationCase, load_dataset
from app.evaluation.runner import (
    EvaluationReport,
    Prediction,
    evaluate_predictions,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPARISON_REPORT_PATH = PROJECT_ROOT / "reports" / "candidate_comparison.json"

Predictor = Callable[[EvaluationCase], Prediction]


def compare_candidates(
    candidate_a_id: str,
    candidate_a_predictor: Predictor,
    candidate_b_id: str,
    candidate_b_predictor: Predictor,
) -> dict:
    if not candidate_a_id.strip() or not candidate_b_id.strip():
        raise ValueError("Candidate IDs must not be empty.")

    if candidate_a_id == candidate_b_id:
        raise ValueError("Candidate IDs must be different.")

    cases = load_dataset()

    report_a = evaluate_predictions(
        cases,
        [candidate_a_predictor(case) for case in cases],
    )
    report_b = evaluate_predictions(
        cases,
        [candidate_b_predictor(case) for case in cases],
    )

    metrics_a = report_a.model_dump()
    metrics_b = report_b.model_dump()

    comparison = {
        "candidate_a": {
            "candidate_id": candidate_a_id,
            "metrics": metrics_a,
        },
        "candidate_b": {
            "candidate_id": candidate_b_id,
            "metrics": metrics_b,
        },
        "differences_b_minus_a": {
            metric: round(metrics_b[metric] - metrics_a[metric], 6)
            for metric in (
                "task_success_rate",
                "category_accuracy",
                "priority_accuracy",
                "average_latency_ms",
                "average_cost_usd",
            )
        },
        "interpretation": {
            "task_success_rate": (
                "improved"
                if report_b.task_success_rate > report_a.task_success_rate
                else "regressed"
                if report_b.task_success_rate < report_a.task_success_rate
                else "unchanged"
            ),
            "latency": (
                "improved"
                if report_b.average_latency_ms < report_a.average_latency_ms
                else "regressed"
                if report_b.average_latency_ms > report_a.average_latency_ms
                else "unchanged"
            ),
            "cost": (
                "improved"
                if report_b.average_cost_usd < report_a.average_cost_usd
                else "regressed"
                if report_b.average_cost_usd > report_a.average_cost_usd
                else "unchanged"
            ),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_size": len(cases),
        "limitations": [
            "Both candidates are evaluated on the same small synthetic dataset.",
            "This comparison does not establish statistical significance.",
            "Latency and cost depend on the predictors supplied.",
        ],
    }

    return comparison


def generate_baseline_comparison() -> dict:
    """Generate a demonstration comparison using two local predictors."""
    def conservative_predictor(case: EvaluationCase) -> Prediction:
        prediction = predict_feedback(case)
        return prediction.model_copy(
            update={"latency_ms": 100.0, "cost_usd": 0.001}
        )

    def optimized_predictor(case: EvaluationCase) -> Prediction:
        prediction = predict_feedback(case)
        return prediction.model_copy(
            update={"latency_ms": 80.0, "cost_usd": 0.0008}
        )

    result = compare_candidates(
        candidate_a_id="baseline-v1",
        candidate_a_predictor=conservative_predictor,
        candidate_b_id="baseline-v2",
        candidate_b_predictor=optimized_predictor,
    )

    COMPARISON_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON_REPORT_PATH.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    return result


if __name__ == "__main__":
    result = generate_baseline_comparison()
    print(json.dumps(result, indent=2))
    print(f"\nComparison saved to: {COMPARISON_REPORT_PATH}")
