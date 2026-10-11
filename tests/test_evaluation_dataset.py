
import json

import pytest

from app.evaluation.dataset import (
    EvaluationCase,
    load_dataset,
)


def test_load_default_dataset():
    cases = load_dataset()

    assert len(cases) == 10
    assert cases[0].case_id == "CF-001"


def test_dataset_rejects_duplicate_case_ids(tmp_path):
    path = tmp_path / "duplicate.json"

    case = {
        "case_id": "CF-001",
        "input": "My order arrived late.",
        "expected_category": "general_feedback",
        "expected_priority": "low",
    }

    path.write_text(
        json.dumps([case, case]),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="duplicate case IDs",
    ):
        load_dataset(path)


def test_dataset_rejects_missing_file(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_dataset(path)


def test_evaluation_case_rejects_empty_input():
    with pytest.raises(ValueError):
        EvaluationCase(
            case_id="CF-001",
            input="",
            expected_category="billing",
            expected_priority="high",
        )
