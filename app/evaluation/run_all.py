import json

from app.evaluation.candidate_comparison import generate_baseline_comparison
from app.evaluation.error_analysis import generate_error_analysis
from app.evaluation.report_generator import generate_report
from app.evaluation.summary import generate_evaluation_summary


def main() -> int:
    print("Generating baseline evaluation report...")
    generate_report()

    print("Generating candidate comparison report...")
    generate_baseline_comparison()

    print("Generating error analysis report...")
    generate_error_analysis()

    print("Generating combined evaluation summary...")
    summary = generate_evaluation_summary()

    print(json.dumps(summary, indent=2))

    if not summary["ready"]:
        print(
            "\nEvaluation run completed, but one or more reports "
            "are missing or invalid."
        )
        return 1

    print("\nAll evaluation reports were generated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
