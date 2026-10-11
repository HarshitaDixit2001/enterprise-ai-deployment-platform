from pydantic import BaseModel, Field

from app.evaluation.runner import Prediction


class ReleaseEvaluationRequest(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=100)
    predictions: list[Prediction] = Field(min_length=1)
