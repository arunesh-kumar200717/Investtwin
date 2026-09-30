from datetime import date

from pydantic import BaseModel, Field


class ExposureHolding(BaseModel):
    asset_id: str
    asset_type: str
    value: float = Field(ge=0)


class ExposureInput(BaseModel):
    holdings: list[ExposureHolding] = Field(min_length=1)
    concentration_threshold_percent: float = Field(default=40, gt=0, le=100)


class GoalProgressInput(BaseModel):
    target_amount: float = Field(gt=0)
    current_portfolio_value: float = Field(ge=0)


def calculate_exposure(payload: ExposureInput) -> dict:
    total = sum(holding.value for holding in payload.holdings)
    if total <= 0:
        return {"status": "unavailable", "message": "A positive portfolio total is required"}
    categories: dict[str, float] = {}
    holdings = []
    alerts = []
    for holding in payload.holdings:
        weight = holding.value / total * 100
        categories[holding.asset_type] = categories.get(holding.asset_type, 0) + weight
        holdings.append({"asset_id": holding.asset_id, "asset_type": holding.asset_type, "value": holding.value, "weight_percent": round(weight, 4)})
        if weight > payload.concentration_threshold_percent:
            alerts.append({"type": "concentration", "severity": "medium", "message": f"{weight:.2f}% of the current portfolio is exposed to a single asset.", "metric": "portfolio_weight_percent", "value": round(weight, 4), "rule": f"Application threshold: {payload.concentration_threshold_percent:.2f}%"})
    return {"status": "available", "total_value": total, "allocation": {key: round(value, 4) for key, value in categories.items()}, "holdings": holdings, "alerts": alerts}


def calculate_goal_progress(payload: GoalProgressInput) -> dict:
    progress = min(payload.current_portfolio_value / payload.target_amount * 100, 100)
    return {"status": "available", "target_amount": payload.target_amount, "current_portfolio_value": payload.current_portfolio_value, "goal_progress_percent": round(progress, 4), "remaining_amount": max(payload.target_amount - payload.current_portfolio_value, 0), "calculation_date": date.today().isoformat()}