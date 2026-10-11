
from collections import defaultdict
from typing import Callable

from pydantic import BaseModel, Field

from app.evaluation.dataset import (
    EvaluationCase,
    load_dataset,
)


class Prediction(BaseModel):
    case_id: str
    predicted_category: str
    predicted_priority: str
    latency_ms: float = Field(ge=0)
    cost_usd: float = Field(ge=0)
    safety_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class EvaluationReport(BaseModel):
    total_cases: int
    successful_cases: int
    task_success_rate: float
    category_accuracy: float
    priority_accuracy: float
    per_category_accuracy: dict[str, float]
    failed_case_ids: list[str]
    average_latency_ms: float
    average_cost_usd: float
    average_safety_score: float | None


Predictor = Callable[[EvaluationCase], Prediction]


def evaluate_predictions(
    cases: list[EvaluationCase],
    predictions: list[Prediction],
) -> EvaluationReport:
    if not cases:
        raise ValueError("Cannot evaluate an empty dataset.")

    expected_ids = {case.case_id for case in cases}
    prediction_ids = [p.case_id for p in predictions]

    if len(prediction_ids) != len(set(prediction_ids)):
        raise ValueError("Duplicate prediction case IDs found.")

    if set(prediction_ids) != expected_ids:
        raise ValueError(
            "Predictions must contain exactly one result "
            "for every evaluation case."
        )

    predictions_by_id = {
        prediction.case_id: prediction
        for prediction in predictions
    }

    category_totals: dict[str, int] = defaultdict(int)
    category_successes: dict[str, int] = defaultdict(int)

    category_correct_count = 0
    priority_correct_count = 0
    successful_cases = 0
    failed_case_ids: list[str] = []

    for case in cases:
        prediction = predictions_by_id[case.case_id]

        category_correct = (
            prediction.predicted_category == case.expected_category
        )
        priority_correct = (
            prediction.predicted_priority == case.expected_priority
        )
        task_success = category_correct and priority_correct

        category_totals[case.expected_category] += 1

        if category_correct:
            category_correct_count += 1
            category_successes[case.expected_category] += 1

        if priority_correct:
            priority_correct_count += 1

        if task_success:
            successful_cases += 1
        else:
            failed_case_ids.append(case.case_id)

    total = len(cases)
    safety_scores = [
        p.safety_score
        for p in predictions
        if p.safety_score is not None
    ]

    return EvaluationReport(
        total_cases=total,
        successful_cases=successful_cases,
        task_success_rate=successful_cases / total,
        category_accuracy=category_correct_count / total,
        priority_accuracy=priority_correct_count / total,
        per_category_accuracy={
            category: category_successes[category] / count
            for category, count in sorted(category_totals.items())
        },
        failed_case_ids=failed_case_ids,
        average_latency_ms=(
            sum(p.latency_ms for p in predictions) / total
        ),
        average_cost_usd=(
            sum(p.cost_usd for p in predictions) / total
        ),
        average_safety_score=(
            sum(safety_scores) / total
            if len(safety_scores) == total
            else None
        ),
    )


def run_evaluation(
    predictor: Predictor,
) -> EvaluationReport:
    cases = load_dataset()
    predictions = [predictor(case) for case in cases]
    return evaluate_predictions(cases, predictions)
