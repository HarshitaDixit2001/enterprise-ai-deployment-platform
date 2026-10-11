from app.evaluation.dataset import load_named_dataset
from app.services.audit_service import AUDIT_LOG_PATH


def check_readiness() -> dict:
    checks: dict[str, dict[str, str]] = {}

    try:
        cases = load_named_dataset("customer_feedback_v1")
        checks["evaluation_dataset"] = {
            "status": "ready" if cases else "not_ready",
            "detail": (
                f"{len(cases)} evaluation cases loaded."
                if cases
                else "The evaluation dataset is empty."
            ),
        }
    except Exception:
        checks["evaluation_dataset"] = {
            "status": "not_ready",
            "detail": "The evaluation dataset could not be loaded.",
        }

    try:
        AUDIT_LOG_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        probe_path = AUDIT_LOG_PATH.parent / ".readiness_probe"
        probe_path.write_text("ok", encoding="utf-8")
        probe_path.unlink()

        checks["audit_storage"] = {
            "status": "ready",
            "detail": "The audit directory is writable.",
        }
    except OSError:
        checks["audit_storage"] = {
            "status": "not_ready",
            "detail": "The audit directory is not writable.",
        }

    ready = all(
        check["status"] == "ready"
        for check in checks.values()
    )

    return {
        "status": "ready" if ready else "not_ready",
        "checks": checks,
    }
