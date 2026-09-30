from math import isfinite
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.stress.scenario_config import SCENARIOS

StressAssetType = Literal["equity", "mutual_funds", "debt", "gold", "cash", "fd", "liquid"]
ALLOWED_PARAMETERS = {
    "asset_id", "asset_change_percent", "value", "equity_change_percent",
    "mutual_funds_change_percent", "debt_change_percent", "gold_change_percent",
    "cash_change_percent", "fd_change_percent", "liquid_change_percent",
    "income_change_percent", "contribution_change_percent", "new_monthly_contribution",
    "emergency_expense", "goal_deadline_change_months",
}


class StressHolding(BaseModel):
    asset_id: str = Field(min_length=1, max_length=100)
    asset_type: StressAssetType
    value: float = Field(ge=0)


class StressRequest(BaseModel):
    user_id: str = Field(min_length=8, max_length=100)
    scenario_type: str = Field(min_length=1)
    severity: str = "moderate"
    parameters: dict[str, float | str] = Field(default_factory=dict)
    holdings: list[StressHolding] = Field(min_length=1)
    goal_target: float | None = Field(default=None, gt=0)
    monthly_income: float = Field(default=0, ge=0)
    monthly_contribution: float = Field(default=0, ge=0)

    @field_validator("scenario_type")
    @classmethod
    def validate_scenario_type(cls, value: str) -> str:
        if value not in SCENARIOS:
            raise ValueError("Unsupported stress scenario")
        return value

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        if value not in {"mild", "moderate", "severe", "custom"}:
            raise ValueError("Unsupported scenario severity")
        return value

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, parameters: dict[str, float | str]) -> dict[str, float | str]:
        for key, value in parameters.items():
            if key not in ALLOWED_PARAMETERS:
                raise ValueError("Unsupported stress parameter")
            if key == "asset_id":
                if not isinstance(value, str) or len(value) > 100:
                    raise ValueError("Invalid stress asset identifier")
                continue
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError("Stress parameters must be numeric") from exc
            if not isfinite(number):
                raise ValueError("Stress parameters must be finite")
            if key.endswith("_change_percent") and not -100 <= number <= 100:
                raise ValueError("Scenario percentage changes must be between -100 and 100")
            if key in {"emergency_expense", "new_monthly_contribution"} and number < 0:
                raise ValueError("Stress amounts cannot be negative")
            parameters[key] = number
        return parameters

    @model_validator(mode="after")
    def validate_asset_reference(self):
        if self.scenario_type in {"asset_shock", "concentration_shock"}:
            target_asset = self.parameters.get("asset_id")
            if target_asset and target_asset not in {holding.asset_id for holding in self.holdings}:
                raise ValueError("Stress asset must be one of the supplied holdings")
        return self


class StressTestRecord(StressRequest):
    stress_test_id: str
    result: dict