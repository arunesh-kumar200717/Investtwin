from pydantic import BaseModel

from app.analysis.portfolio_impact import PortfolioImpactInput
from app.analysis.portfolio_exposure import ExposureInput, GoalProgressInput


class AnalysisResponse(BaseModel):
    symbol: str
    source: str | None = None
    data_status: str
    data_timestamp: str | None = None
    analysis_timestamp: str | None = None
    message: str | None = None
    price: dict | None = None
    returns: dict | None = None
    moving_averages: dict | None = None
    trend_structure: str | None = None
    risk: dict | None = None
    momentum: dict | None = None
    volume: dict | None = None
    alerts: list[dict] = []


class ChartHistoryResponse(BaseModel):
    symbol: str
    data_status: str
    data: list[dict] = []


class PortfolioImpactResponse(BaseModel):
    status: str
    asset_id: str | None = None
    portfolio_value: float | None = None
    asset_value: float | None = None
    portfolio_weight_percent: float | None = None
    movement_percent: float | None = None
    illustrative_portfolio_impact_percent: float | None = None
    assumption: str | None = None
    message: str | None = None


class PortfolioExposureResponse(BaseModel):
    status: str
    total_value: float | None = None
    allocation: dict[str, float] = {}
    holdings: list[dict] = []
    alerts: list[dict] = []
    message: str | None = None


class GoalProgressResponse(BaseModel):
    status: str
    target_amount: float | None = None
    current_portfolio_value: float | None = None
    goal_progress_percent: float | None = None
    remaining_amount: float | None = None
    calculation_date: str | None = None
    message: str | None = None