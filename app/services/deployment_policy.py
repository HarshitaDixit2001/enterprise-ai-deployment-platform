from app.models.deployment import DeploymentDecision
from app.models.use_case import UseCaseConfig


def evaluate_deployment_policy(
    candidate_id: str,
    release_approved: bool,
    human_approval_granted: bool,
    config: UseCaseConfig,
) -> DeploymentDecision:
    checks = {
        "release_gate_approved": release_approved,
        "human_approval": (
            human_approval_granted
            if config.requires_human_approval
            else True
        ),
    }

    reasons = []

    if not checks["release_gate_approved"]:
        reasons.append(
            "Deployment blocked because no approved release record "
            "exists for this candidate."
        )

    if not checks["human_approval"]:
        reasons.append(
            "Deployment blocked because required human approval is missing."
        )

    return DeploymentDecision(
        candidate_id=candidate_id,
        decision="permitted" if all(checks.values()) else "blocked",
        reasons=reasons,
        checks=checks,
    )