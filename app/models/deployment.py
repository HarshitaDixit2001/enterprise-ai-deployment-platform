from typing import Literal

from pydantic import BaseModel, Field


class DeploymentRequest(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=100)
    human_approval_granted: bool = False


class DeploymentDecision(BaseModel):
    candidate_id: str
    decision: Literal["permitted", "blocked"]
    reasons: list[str] = Field(default_factory=list)
    checks: dict[str, bool]