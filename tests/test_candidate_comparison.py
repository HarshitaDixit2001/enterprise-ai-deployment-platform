import pytest

from app.evaluation.baseline_predictor import predict_feedback
from app.evaluation.candidate_comparison import compare_candidates
from app.evaluation.dataset import EvaluationCase, load_dataset
from app.evaluation.runner import Prediction


def test_candidate_comparison_uses_same_dataset():
    def candidate_a(case: EvaluationCase) -> Prediction:
        return predict_feedback(case).model_copy(
            update={"latency_ms": 100.0, "cost_usd": 0.001}
        )

    def candidate_b(case: EvaluationCase) -> Prediction:
        return predict_feedback(case).model_copy(
            update={"latency_ms": 80.0, "cost_usd": 0.0008}
        )

    result = compare_candidates(
        "candidate-a",
        candidate_a,
        "candidate-b",
        candidate_b,
    )

    assert result["dataset_size"] == len(load_dataset())
    assert result["differences_b_minus_a"]["average_latency_ms"] == -20.0
    assert result["differences_b_minus_a"]["average_cost_usd"] == -0.0002
    assert result["interpretation"]["latency"] == "improved"
    assert result["interpretation"]["cost"] == "improved"


def test_candidate_comparison_rejects_same_candidate_ids():
    def predictor(case: EvaluationCase) -> Prediction:
        return predict_feedback(case)

    with pytest.raises(ValueError, match="must be different"):
        compare_candidates(
            "same",
            predictor,
            "same",
            predictor,
        )


def test_candidate_comparison_rejects_blank_ids():
    def predictor(case: EvaluationCase) -> Prediction:
        return predict_feedback(case)

    with pytest.raises(ValueError, match="must not be empty"):
        compare_candidates(
            " ",
            predictor,
            "candidate-b",
            predictor,
        )
