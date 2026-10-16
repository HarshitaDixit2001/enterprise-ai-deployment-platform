from app.evaluation.summary import generate_evaluation_summary


def check_evaluation_health() -> dict:
    summary = generate_evaluation_summary()

    invalid_reports = [
        name
        for name, report in summary["reports"].items()
        if report.get("status") != "available"
    ]

    healthy = summary["ready"] and not invalid_reports

    return {
        "status": "healthy" if healthy else "degraded",
        "reports_ready": summary["ready"],
        "available_report_count": sum(
            report.get("status") == "available"
            for report in summary["reports"].values()
        ),
        "missing_reports": summary["missing_reports"],
        "invalid_reports": invalid_reports,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(check_evaluation_health(), indent=2))
