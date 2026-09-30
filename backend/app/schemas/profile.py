from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user_profile import (
    InvestmentDetails,
    LiquidityDetails,
    RiskAnswers,
    RiskAssessment,
    UserProfile,
)


class ProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(gt=0, le=120)
    employment_status: str = Field(min_length=1, max_length=50)
    monthly_income: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    investment: InvestmentDetails
    risk_assessment: RiskAnswers
    liquidity: LiquidityDetails
    existing_investments: list[str] = Field(default_factory=list, max_length=20)
    preferred_categories: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("name")
    @classmethod
    def name_must_contain_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name is required")
        return value.strip()

    @field_validator("monthly_income", "monthly_contribution", mode="before")
    @classmethod
    def reject_negative_money(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Amounts cannot be negative")
        return value


class ProfileResponse(UserProfile):
    pass


class ProfileUpdate(ProfileCreate):
    pass


def profile_to_response(document: dict) -> ProfileResponse:
    return ProfileResponse.model_validate(document)