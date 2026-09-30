from app.config.settings import Settings
from app.data.market_models import DataSourceStatus, DataSourcesStatus


def data_sources_status(settings: Settings) -> DataSourcesStatus:
    stock_status = DataSourceStatus(status="available" if settings.stock_api_key else "unavailable", source="Alpha Vantage" if settings.stock_api_key else None, message=None if settings.stock_api_key else "No verified stock provider key configured", rate_limit="Free key: 25 requests/day for most datasets; realtime and 15-minute US quotes are premium")
    return DataSourcesStatus(stocks=stock_status, mutual_funds=DataSourceStatus(status="available", source="AMFI India", message="Latest NAV endpoint configured; historical NAV range retrieval is not exposed yet"), gold=unavailable("No verified free INR gold source configured"), nps=unavailable("No verified structured public NPS NAV provider configured"), bonds=unavailable("No verified bond subset provider configured"), fd=unavailable("No verified structured FD rate provider configured"), ppf=unavailable("No verified current PPF rules provider configured"))


def unavailable(message: str) -> DataSourceStatus:
    return DataSourceStatus(status="unavailable", message=message)