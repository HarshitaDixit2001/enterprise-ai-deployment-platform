from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.api.use_cases import find_use_case
from app.evaluation.dataset import load_named_dataset
from app.evaluation.health_check import check_evaluation_health
from app.evaluation.provider_predictor import predict_with_provider
from app.evaluation.runner import evaluate_predictions
from app.evaluation.summary import generate_evaluation_summary
from app.models.evaluation_request import ReleaseEvaluationRequest
from app.models.release import ReleaseDecision
from app.services.audit_service import (
    list_release_decisions,
    record_release_decision,
)
from app.services.release_gate import evaluate_release

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.get("/summary")
async def get_evaluation_summary() -> dict[str, Any]:
    return generate_evaluation_summary()


@router.get("/health")
async def get_evaluation_health() -> JSONResponse:
    result = check_evaluation_health()
    status_code = 200 if result["status"] == "healthy" else 503

    return JSONResponse(
        status_code=status_code,
        content=result,
    )


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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    try:
        report = evaluate_predictions(cases, request.predictions)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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


@router.post(
    "/{use_case_id}/provider-release-decision",
    response_model=ReleaseDecision,
)
def create_provider_release_decision(
    use_case_id: str,
    candidate_id: str = Query(min_length=1, max_length=100),
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    try:
        predictions = [
            predict_with_provider(case)
            for case in cases
        ]
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Provider evaluation failed. Check provider configuration, "
                "availability, response format, and token-pricing settings."
            ),
        ) from exc

    try:
        report = evaluate_predictions(cases, predictions)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    decision = evaluate_release(
        candidate_id=candidate_id,
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
