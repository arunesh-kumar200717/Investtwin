from pydantic import BaseModel, Field


class ExistingHolding(BaseModel):
    asset_id: str
    asset_type: str
    value: float = Field(ge=0)


class PortfolioRecommendationRequest(BaseModel):
    user_id: str = Field(min_length=8, max_length=100)
    holdings: list[ExistingHolding] = Field(default_factory=list)


class PortfolioRecommendationResponse(BaseModel):
    status: str
    profile: dict
    candidate_allocation: dict[str, float]
    monthly_contribution: dict[str, float]
    candidates: list[dict]
    current_allocation: dict[str, float]
    drift: list[dict]
    goal_progress: dict
    risk_flags: list[dict]
    data_status: str
    rules_note: str