from pathlib import Path

from app.evaluation.summary import generate_evaluation_summary

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "reports" / "evaluation_summary.md"


def generate_markdown_report() -> Path:
    summary = generate_evaluation_summary()
    lines = [
        "# Evaluation Summary",
        "",
        f"**Report-generation status:** {'READY' if summary['ready'] else 'NOT READY'}",
        "",
        "> READY means the required evaluation reports are available and valid. "
        "This does not mean a candidate is approved for production.",
        "",
        "## Reports",
        "",
        "| Report | Status | Dataset | Cases |",
        "|---|---|---|---:|",
    ]

    for name, report in summary["reports"].items():
        lines.append(
            f"| {name} | {report['status']} | "
            f"{report.get('dataset') or 'N/A'} | "
            f"{report.get('dataset_size') if report.get('dataset_size') is not None else 'N/A'} |"
        )

    if summary["missing_reports"]:
        lines.extend(["", "## Missing Reports", ""])
        lines.extend(f"- {name}" for name in summary["missing_reports"])

    lines.extend(["", "## Known Limitations", ""])
    lines.extend(f"- {item}" for item in summary["limitations"])
    lines.append("")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return OUTPUT_PATH


if __name__ == "__main__":
    print(generate_markdown_report())
