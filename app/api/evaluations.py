from fastapi import APIRouter, HTTPException, status

from app.api.use_cases import find_use_case
from app.evaluation.dataset import load_named_dataset
from app.evaluation.runner import evaluate_predictions
from app.models.evaluation_request import ReleaseEvaluationRequest
from app.models.release import ReleaseDecision
from app.services.release_gate import evaluate_release
from typing import Any

from app.services.audit_service import (
    list_release_decisions,
    record_release_decision,
)
router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post(
    "/{use_case_id}/release-decision",
    response_model=ReleaseDecision,
)
async def create_release_decision(
    use_case_id: str,
    request: ReleaseEvaluationRequest,
) -> ReleaseDecision:
    config = find_use_case(use_case_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found.",
        )

    try:
        cases = load_named_dataset(config.evaluation_dataset)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    try:
        report = evaluate_predictions(cases, request.predictions)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    decision = evaluate_release(
    candidate_id=request.candidate_id,
    report=report,
    config=config,
    )

    record_release_decision(
        decision=decision.model_dump(),
        use_case_id=use_case_id,
    )

    return decision


@router.get("/{use_case_id}/history")
async def get_release_history(
    use_case_id: str,
) -> list[dict[str, Any]]:
    config = find_use_case(use_case_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found.",
        )

    return list_release_decisions(use_case_id)