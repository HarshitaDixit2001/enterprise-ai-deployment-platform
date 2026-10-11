import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from app.evaluation.baseline_predictor import predict_feedback
from app.evaluation.dataset import load_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "reports" / "error_analysis.json"


def generate_error_analysis() -> dict:
    cases = load_dataset()

    errors = []
    category_errors = Counter()
    priority_errors = Counter()

    for case in cases:
        prediction = predict_feedback(case)

        category_correct = (
            prediction.predicted_category == case.expected_category
        )
        priority_correct = (
            prediction.predicted_priority == case.expected_priority
        )

        if not category_correct:
            category_errors[
                f"{case.expected_category} -> {prediction.predicted_category}"
            ] += 1

        if not priority_correct:
            priority_errors[
                f"{case.expected_priority} -> {prediction.predicted_priority}"
            ] += 1

        if not category_correct or not priority_correct:
            errors.append(
                {
                    "case_id": case.case_id,
                    "input": case.input,
                    "expected_category": case.expected_category,
                    "predicted_category": prediction.predicted_category,
                    "category_correct": category_correct,
                    "expected_priority": case.expected_priority,
                    "predicted_priority": prediction.predicted_priority,
                    "priority_correct": priority_correct,
                }
            )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": "customer_feedback_v1",
        "dataset_size": len(cases),
        "incorrect_case_count": len(errors),
        "error_rate": (
            len(errors) / len(cases) if cases else 0.0
        ),
        "category_error_patterns": dict(category_errors),
        "priority_error_patterns": dict(priority_errors),
        "errors": errors,
        "limitations": [
            "The analysis evaluates a deterministic keyword baseline.",
            "Error patterns depend on the supplied synthetic dataset and labels.",
            "Observed errors do not establish production model performance.",
        ],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report


if __name__ == "__main__":
    print(json.dumps(generate_error_analysis(), indent=2))
    print(f"\nReport saved to: {REPORT_PATH}")
