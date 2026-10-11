from time import perf_counter

from app.evaluation.dataset import EvaluationCase
from app.evaluation.runner import Prediction


KEYWORDS = {
    "security": (
        "unauthorized",
        "accessed my account",
        "hacked",
        "security",
    ),
    "billing": (
        "charged twice",
        "invoice",
        "tax",
        "billing",
        "payment",
    ),
    "technical_issue": (
        "crashes",
        "crash",
        "password reset",
        "email never arrives",
        "technical",
        "error",
    ),
    "account_request": (
        "cancel subscription",
        "delete account",
        "remove personal data",
        "close my account",
    ),
}

CRITICAL_KEYWORDS = (
    "unauthorized",
    "accessed my account",
    "hacked",
)

HIGH_KEYWORDS = (
    "charged twice",
    "crashes",
    "broken",
    "delete account",
    "remove personal data",
)


def predict_feedback(case: EvaluationCase) -> Prediction:
    """A simple, deterministic baseline for local evaluation."""
    started = perf_counter()
    text = case.input.lower()

    category = "general_feedback"
    for candidate, keywords in KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            category = candidate
            break

    if any(keyword in text for keyword in CRITICAL_KEYWORDS):
        priority = "critical"
    elif any(keyword in text for keyword in HIGH_KEYWORDS):
        priority = "high"
    elif category in {"billing", "technical_issue", "account_request"}:
        priority = "medium"
    else:
        priority = "low"

    latency_ms = (perf_counter() - started) * 1000

    return Prediction(
        case_id=case.case_id,
        predicted_category=category,
        predicted_priority=priority,
        latency_ms=latency_ms,
        cost_usd=0.0,
        # This baseline does not implement a validated safety evaluator.
        safety_score=None,
    )
