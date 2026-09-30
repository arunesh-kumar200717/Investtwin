from fastapi import APIRouter, Depends, HTTPException, Query

from app.config.settings import Settings, get_settings
from app.data.market_models import HistoricalBar, NormalizedMarketData
from app.data.mutual_fund_service import MutualFundDataService
from app.data.provider_client import ProviderError
from app.data.stock_data_service import StockDataService

router = APIRouter(prefix="/market", tags=["market-data"])


@router.get("/stocks/{symbol}", response_model=NormalizedMarketData)
def stock_quote(symbol: str, settings: Settings = Depends(get_settings)) -> NormalizedMarketData:
    try:
        return StockDataService(settings).current_price(symbol)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail="Live stock data is temporarily unavailable.") from exc


@router.get("/stocks/{symbol}/history", response_model=list[HistoricalBar])
def stock_history(symbol: str, settings: Settings = Depends(get_settings)) -> list[HistoricalBar]:
    try:
        return StockDataService(settings).history(symbol)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail="Historical stock data is temporarily unavailable.") from exc


@router.get("/mutual-funds", response_model=list[NormalizedMarketData])
def mutual_funds(query: str | None = Query(default=None, max_length=100), settings: Settings = Depends(get_settings)) -> list[NormalizedMarketData]:
    try:
        return MutualFundDataService(settings).latest(query)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail="Live mutual-fund NAV data is temporarily unavailable.") from exc


@router.get("/mutual-funds/{scheme_id}", response_model=NormalizedMarketData)
def mutual_fund(scheme_id: str, settings: Settings = Depends(get_settings)) -> NormalizedMarketData:
    try:
        values = MutualFundDataService(settings).latest(scheme_id)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail="Live mutual-fund NAV data is temporarily unavailable.") from exc
    if not values or values[0].asset_id != scheme_id:
        raise HTTPException(status_code=404, detail="Mutual-fund scheme was not found in the official NAV source.")
    return values[0]