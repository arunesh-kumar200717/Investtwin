from datetime import date, datetime

from pydantic import BaseModel, Field


class InvestmentDetails(BaseModel):
    initial_amount: float = Field(ge=0)
    horizon: str
    goal: str
    custom_goal: str | None = None
    target_amount: float = Field(gt=0)
    target_date: date | None = None


class RiskAnswers(BaseModel):
    temporary_loss: str
    investment_time: str
    capital_protection: str
    value_fluctuations: str


class RiskAssessment(BaseModel):
    answers: RiskAnswers
    risk_profile: str
    score: int = Field(ge=0)


class LiquidityDetails(BaseModel):
    emergency_fund_status: str
    coverage: str | None = None


class UserProfile(BaseModel):
    user_id: str
    name: str
    age: int = Field(gt=0, le=120)
    employment_status: str
    monthly_income: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    investment: InvestmentDetails
    risk_assessment: RiskAssessment
    liquidity: LiquidityDetails
    existing_investments: list[str] = Field(default_factory=list)
    preferred_categories: list[str] = Field(default_factory=list)
    completion_percentage: int = Field(ge=0, le=100)
    created_at: datetime
    updated_at: datetime