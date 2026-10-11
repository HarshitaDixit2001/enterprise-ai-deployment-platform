import json
from datetime import datetime, timezone
from pathlib import Path

from app.evaluation.baseline_predictor import predict_feedback
from app.evaluation.dataset import load_dataset
from app.evaluation.runner import evaluate_predictions

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "reports" / "baseline_evaluation.json"


def generate_report() -> dict:
    cases = load_dataset()
    predictions = [predict_feedback(case) for case in cases]
    report = evaluate_predictions(cases, predictions)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_type": "deterministic_keyword_baseline",
        "dataset": "customer_feedback_v1",
        "dataset_size": len(cases),
        "metrics": report.model_dump(),
        "limitations": [
            "This is a deterministic keyword baseline, not an LLM.",
            "Results depend on the supplied synthetic labels.",
            "Safety has not been independently evaluated.",
            "Latency is a local execution measurement.",
            "Cost is zero because no paid model is called.",
        ],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    return result


if __name__ == "__main__":
    generated = generate_report()
    print(json.dumps(generated, indent=2))
    print(f"\nReport saved to: {REPORT_PATH}")
