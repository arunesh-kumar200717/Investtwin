from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta

from app.analysis.analysis_service import analyze_history, chart_history
from app.analysis.portfolio_exposure import ExposureInput, GoalProgressInput, calculate_exposure, calculate_goal_progress
from app.analysis.portfolio_impact import PortfolioImpactInput, portfolio_impact
from app.config.settings import Settings, get_settings
from app.data.provider_client import ProviderError
from app.data.stock_data_service import StockDataService
from app.schemas.analysis_schema import AnalysisResponse, ChartHistoryResponse, GoalProgressResponse, PortfolioExposureResponse, PortfolioImpactResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])


def history_for(symbol: str, settings: Settings) -> list[dict]:
    return [bar.model_dump(mode="json") for bar in StockDataService(settings).history(symbol)]


@router.get("/stocks/{symbol}", response_model=AnalysisResponse)
def stock_analysis(symbol: str, settings: Settings = Depends(get_settings)) -> AnalysisResponse:
    try:
        bars = history_for(symbol, settings)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail="Historical data is temporarily unavailable for this instrument.") from exc
    return AnalysisResponse.model_validate(analyze_history(symbol.upper(), bars, "Alpha Vantage"))


@router.get("/stocks/{symbol}/history", response_model=ChartHistoryResponse)
def stock_analysis_history(symbol: str, period: str | None = Query(default=None), start_date: str | None = Query(default=None), end_date: str | None = Query(default=None), settings: Settings = Depends(get_settings)) -> ChartHistoryResponse:
    try:
        bars = history_for(symbol, settings)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail="Historical data is temporarily unavailable for this instrument.") from exc
    bars = filter_history(bars, period, start_date, end_date)
    return ChartHistoryResponse.model_validate(chart_history(symbol.upper(), bars))


@router.post("/portfolio-impact", response_model=PortfolioImpactResponse)
def calculate_portfolio_impact(payload: PortfolioImpactInput) -> PortfolioImpactResponse:
    return PortfolioImpactResponse.model_validate(portfolio_impact(payload))


@router.post("/portfolio-exposure", response_model=PortfolioExposureResponse)
def calculate_portfolio_exposure(payload: ExposureInput) -> PortfolioExposureResponse:
    return PortfolioExposureResponse.model_validate(calculate_exposure(payload))


@router.post("/goal-progress", response_model=GoalProgressResponse)
def calculate_goal_progress_endpoint(payload: GoalProgressInput) -> GoalProgressResponse:
    return GoalProgressResponse.model_validate(calculate_goal_progress(payload))


def filter_history(bars: list[dict], period: str | None, start_date: str | None, end_date: str | None) -> list[dict]:
    filtered = bars
    if start_date:
        start = datetime.fromisoformat(start_date).date()
        filtered = [bar for bar in filtered if datetime.fromisoformat(bar["date"]).date() >= start]
    if end_date:
        end = datetime.fromisoformat(end_date).date()
        filtered = [bar for bar in filtered if datetime.fromisoformat(bar["date"]).date() <= end]
    if period:
        days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}.get(period.upper())
        if days:
            latest = max(datetime.fromisoformat(bar["date"]).date() for bar in filtered)
            threshold = latest - timedelta(days=days)
            filtered = [bar for bar in filtered if datetime.fromisoformat(bar["date"]).date() >= threshold]
    return filtered