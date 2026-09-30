from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AssetType = Literal["stock", "mutual_fund", "gold", "bond", "fd", "nps", "ppf"]
DataStatus = Literal["available", "cached", "unavailable", "error"]


class HistoricalBar(BaseModel):
    symbol: str
    date: str
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float | None = Field(default=None, ge=0)
    source: str


class NormalizedMarketData(BaseModel):
    asset_id: str
    name: str
    asset_type: AssetType
    symbol: str | None = None
    currency: str = "INR"
    exchange: str | None = None
    current_value: float | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, gt=0)
    nav: float | None = Field(default=None, gt=0)
    historical_data: list[HistoricalBar] = Field(default_factory=list)
    source: str
    timestamp: datetime
    data_status: DataStatus = "available"
    freshness: str = "end_of_day"
    cache_expires_at: datetime | None = None


class DataSourceStatus(BaseModel):
    status: DataStatus
    source: str | None = None
    message: str | None = None
    rate_limit: str | None = None


class DataSourcesStatus(BaseModel):
    stocks: DataSourceStatus
    mutual_funds: DataSourceStatus
    gold: DataSourceStatus
    nps: DataSourceStatus
    bonds: DataSourceStatus
    fd: DataSourceStatus
    ppf: DataSourceStatus