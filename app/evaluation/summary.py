import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports"

REPORT_FILES = {
    "baseline": REPORT_DIR / "baseline_evaluation.json",
    "candidate_comparison": REPORT_DIR / "candidate_comparison.json",
    "error_analysis": REPORT_DIR / "error_analysis.json",
}


def _display_path(report_path: Path) -> str:
    """Return a project-relative path when possible, otherwise an absolute path."""
    try:
        return str(report_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(report_path)


def generate_evaluation_summary() -> dict:
    summary = {
        "reports": {},
        "missing_reports": [],
        "limitations": [
            "The baseline uses deterministic keyword rules, not a live LLM.",
            "Candidate comparison latency and cost values are simulated.",
            "Evaluation results depend on the supplied synthetic dataset.",
        ],
    }

    for report_name, report_path in REPORT_FILES.items():
        if not report_path.exists():
            summary["missing_reports"].append(report_name)
            continue

        try:
            report_data = json.loads(
                report_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError) as exc:
            summary["reports"][report_name] = {
                "status": "invalid",
                "error": str(exc),
            }
            continue

        report_summary = {
            "status": "available",
            "path": _display_path(report_path),
            "dataset": report_data.get("dataset"),
            "dataset_size": report_data.get("dataset_size"),
        }

        if "metrics" in report_data:
            report_summary["metrics"] = report_data["metrics"]

        if "incorrect_case_count" in report_data:
            report_summary["incorrect_case_count"] = (
                report_data["incorrect_case_count"]
            )
            report_summary["error_rate"] = report_data.get("error_rate")

        if "comparisons" in report_data:
            report_summary["comparisons"] = report_data["comparisons"]

        summary["reports"][report_name] = report_summary

    summary["ready"] = (
        not summary["missing_reports"]
        and all(
            report.get("status") == "available"
            for report in summary["reports"].values()
        )
    )

    return summary


if __name__ == "__main__":
    print(json.dumps(generate_evaluation_summary(), indent=2))
