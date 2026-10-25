
import json
from unittest.mock import MagicMock, patch

import pytest

from app.evaluation.dataset import EvaluationCase
from app.evaluation.provider_predictor import predict_with_provider


@pytest.fixture
def provider_env(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER_BASE_URL", "https://provider.example/v1")
    monkeypatch.setenv("AI_PROVIDER_API_KEY", "test-key")
    monkeypatch.setenv("AI_PROVIDER_MODEL", "test-model")
    monkeypatch.setenv("AI_PROVIDER_INPUT_USD_PER_MILLION", "1.0")
    monkeypatch.setenv("AI_PROVIDER_OUTPUT_USD_PER_MILLION", "2.0")


@pytest.fixture
def evaluation_case():
    return EvaluationCase(
        case_id="CF-001",
        input="I was charged twice for my invoice.",
        expected_category="billing",
        expected_priority="high",
    )


def mock_client(payload):
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    client.post.return_value = response
    client.__enter__.return_value = client
    client.__exit__.return_value = False
    return client


def valid_payload():
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {"category": "billing", "priority": "high"}
                    )
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
        },
    }


def test_provider_prediction_uses_usage_and_leaves_safety_unscored(
    provider_env, evaluation_case
):
    client = mock_client(valid_payload())

    with patch(
        "app.evaluation.provider_predictor.httpx.Client",
        return_value=client,
    ):
        prediction = predict_with_provider(evaluation_case)

    assert prediction.case_id == "CF-001"
    assert prediction.predicted_category == "billing"
    assert prediction.predicted_priority == "high"
    assert prediction.latency_ms >= 0
    assert prediction.cost_usd == pytest.approx(0.00014)
    assert prediction.safety_score is None


def test_provider_rejects_missing_token_usage(provider_env, evaluation_case):
    payload = valid_payload()
    del payload["usage"]
    client = mock_client(payload)

    with patch(
        "app.evaluation.provider_predictor.httpx.Client",
        return_value=client,
    ):
        with pytest.raises(RuntimeError, match="token-usage"):
            predict_with_provider(evaluation_case)


def test_provider_errors_are_reported(provider_env, evaluation_case):
    client = MagicMock()
    client.__enter__.return_value = client
    client.__exit__.return_value = False
    client.post.side_effect = __import__("httpx").ConnectError(
        "connection failed"
    )

    with patch(
        "app.evaluation.provider_predictor.httpx.Client",
        return_value=client,
    ):
        with pytest.raises(RuntimeError, match="Provider request failed"):
            predict_with_provider(evaluation_case)


def test_provider_requires_configuration(monkeypatch, evaluation_case):
    for name in (
        "AI_PROVIDER_BASE_URL",
        "AI_PROVIDER_API_KEY",
        "AI_PROVIDER_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError, match="Configure AI_PROVIDER"):
        predict_with_provider(evaluation_case)
