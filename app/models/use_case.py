
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from pydantic import BaseModel, Field, ConfigDict


class SuccessCriteria(BaseModel):
    min_task_success_rate: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Minimum acceptable task success rate.",
    )
    max_latency_ms: int = Field(
        default=2000,
        gt=0,
        description="Maximum acceptable response latency in milliseconds.",
    )
    max_cost_per_task: float = Field(
        default=0.05,
        ge=0.0,
        description="Maximum acceptable cost per task in USD.",
    )
    min_safety_score: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Minimum acceptable safety score.",
    )


class UseCaseConfig(BaseModel):
    use_case_id: str = Field(
        min_length=3,
        max_length=100,
    )
    name: str = Field(
        min_length=3,
        max_length=200,
    )
    business_objective: str = Field(
        min_length=10,
        max_length=1000,
    )
    risk_level: Literal["low", "medium", "high"] = "medium"
    evaluation_dataset: str = Field(
        min_length=1,
        max_length=255,
    )
    criteria: SuccessCriteria = Field(
        default_factory=SuccessCriteria,
    )
    requires_human_approval: bool = True

    @model_validator(mode="after")
    def enforce_high_risk_approval(self):
        if (
            self.risk_level == "high"
            and not self.requires_human_approval
        ):
            raise ValueError(
                "High-risk use cases require human approval."
            )

        return self


class ReleaseCriteria(BaseModel):
    model_config = ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
    )

    min_task_success_rate: float = Field(ge=0.0, le=1.0)
    max_latency_ms: float = Field(gt=0.0)
    max_cost_per_task: float = Field(ge=0.0)
    min_safety_score: float = Field(ge=0.0, le=1.0)