
from typing import Literal

from pydantic import BaseModel, Field


class ReleaseDecision(BaseModel):
    candidate_id: str
    decision: Literal["approved", "rejected"]
    reasons: list[str] = Field(default_factory=list)
    checks: dict[str, bool]
    evaluated_metrics: dict[str, float | None]
