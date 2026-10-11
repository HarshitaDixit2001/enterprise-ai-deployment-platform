
import json
from pathlib import Path

from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "customer_feedback.json"
)


class EvaluationCase(BaseModel):
    case_id: str = Field(min_length=1)
    input: str = Field(min_length=1)
    expected_category: str = Field(min_length=1)
    expected_priority: str = Field(min_length=1)


def load_dataset(
    path: Path = DEFAULT_DATASET_PATH,
) -> list[EvaluationCase]:
    if not path.is_file():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, list) or not raw_data:
        raise ValueError(
            "Evaluation dataset must be a non-empty JSON list."
        )

    cases = [
        EvaluationCase.model_validate(item)
        for item in raw_data
    ]

    case_ids = [case.case_id for case in cases]

    if len(case_ids) != len(set(case_ids)):
        raise ValueError(
            "Evaluation dataset contains duplicate case IDs."
        )

    return cases

def load_named_dataset(dataset_name: str) -> list[EvaluationCase]:
    """Load an evaluation dataset by its registered identifier."""
    dataset_registry = {
        "customer_feedback_v1": DEFAULT_DATASET_PATH,
    }

    path = dataset_registry.get(dataset_name)
    if path is None:
        raise ValueError(
            f"Unsupported evaluation dataset: {dataset_name}"
        )

    return load_dataset(path)
