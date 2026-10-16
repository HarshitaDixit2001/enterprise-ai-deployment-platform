import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG_PATH = PROJECT_ROOT / "reports" / "release_audit.jsonl"

logger = logging.getLogger(__name__)
_audit_lock = Lock()


def record_release_decision(
    decision: dict[str, Any],
    use_case_id: str,
) -> dict[str, Any]:
    """Append a release decision to the local audit log."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "use_case_id": use_case_id,
        "candidate_id": decision["candidate_id"],
        "decision": decision["decision"],
        "reasons": decision["reasons"],
        "checks": decision["checks"],
        "evaluated_metrics": decision["evaluated_metrics"],
    }

    with _audit_lock:
        with AUDIT_LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, sort_keys=True) + "\n")

    return record


def list_release_decisions(
    use_case_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return valid audit records, optionally filtered by use case."""
    if not AUDIT_LOG_PATH.is_file():
        return []

    records: list[dict[str, Any]] = []

    with _audit_lock:
        with AUDIT_LOG_PATH.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(
                        "Skipping malformed release audit record",
                        extra={"audit_line_number": line_number},
                    )
                    continue

                if not isinstance(record, dict):
                    logger.warning(
                        "Skipping invalid release audit record",
                        extra={"audit_line_number": line_number},
                    )
                    continue

                if (
                    use_case_id is None
                    or record.get("use_case_id") == use_case_id
                ):
                    records.append(record)

    return records