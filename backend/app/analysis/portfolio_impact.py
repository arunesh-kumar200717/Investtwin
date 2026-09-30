from pydantic import BaseModel, Field


class HoldingInput(BaseModel):
    asset_id: str
    asset_type: str
    value: float = Field(ge=0)


class PortfolioImpactInput(BaseModel):
    holdings: list[HoldingInput] = Field(min_length=1)
    asset_id: str
    movement_percent: float


def portfolio_impact(payload: PortfolioImpactInput) -> dict:
    total = sum(holding.value for holding in payload.holdings)
    selected = next((holding for holding in payload.holdings if holding.asset_id == payload.asset_id), None)
    if total <= 0 or selected is None:
        return {"status": "unavailable", "message": "A positive portfolio total and matching holding are required"}
    weight = selected.value / total
    return {"status": "available", "asset_id": payload.asset_id, "portfolio_value": total, "asset_value": selected.value, "portfolio_weight_percent": round(weight * 100, 4), "movement_percent": payload.movement_percent, "illustrative_portfolio_impact_percent": round(weight * payload.movement_percent, 4), "assumption": "Other holdings remain unchanged; this is an illustrative scenario, not a prediction."}