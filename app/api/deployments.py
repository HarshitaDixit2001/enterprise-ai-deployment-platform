from fastapi import APIRouter, HTTPException

from app.api.use_cases import find_use_case
from app.models.deployment import DeploymentDecision, DeploymentRequest
from app.services.audit_service import list_release_decisions
from app.services.deployment_policy import evaluate_deployment_policy

router = APIRouter(prefix="/deployments", tags=["Deployments"])


@router.post(
    "/{use_case_id}/policy-check",
    response_model=DeploymentDecision,
)
async def check_deployment_policy(
    use_case_id: str,
    request: DeploymentRequest,
) -> DeploymentDecision:
    config = find_use_case(use_case_id)

    if config is None:
        raise HTTPException(
            status_code=404,
            detail="Use case not found.",
        )

    # Find the latest recorded release decision for this exact candidate.
    history = list_release_decisions(use_case_id)

    matching_records = [
        record
        for record in history
        if record.get("candidate_id") == request.candidate_id
    ]

    release_approved = (
        matching_records[-1].get("decision") == "approved"
        if matching_records
        else False
    )

    return evaluate_deployment_policy(
        candidate_id=request.candidate_id,
        release_approved=release_approved,
        human_approval_granted=request.human_approval_granted,
        config=config,
    )