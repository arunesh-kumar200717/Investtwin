from datetime import datetime, timezone

from app.config.settings import Settings
from app.data.cache import market_data_cache
from app.data.market_models import HistoricalBar, NormalizedMarketData
from app.data.provider_client import ProviderError, get_json

SOURCE = "Alpha Vantage"


class StockDataService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _require_configuration(self) -> None:
        if not self.settings.stock_api_key or not self.settings.stock_api_base_url:
            raise ProviderError("No verified stock provider is configured")

    def _request(self, function: str, symbol: str, **extra: str) -> dict:
        self._require_configuration()
        data = get_json(self.settings.stock_api_base_url, {"function": function, "symbol": symbol, "apikey": self.settings.stock_api_key, **extra}, self.settings.external_request_timeout_seconds)
        if not isinstance(data, dict):
            raise ProviderError("The stock provider returned an invalid object")
        if "Error Message" in data or "Note" in data or "Information" in data:
            raise ProviderError(str(data.get("Error Message") or data.get("Note") or data.get("Information")))
        return data

    def current_price(self, symbol: str) -> NormalizedMarketData:
        cache_key = f"stock:quote:{symbol.upper()}"
        cached = market_data_cache.get(cache_key)
        if cached:
            value = NormalizedMarketData.model_validate(cached.value)
            value.data_status = "cached"
            value.cache_expires_at = cached.expires_at
            return value
        payload = self._request("GLOBAL_QUOTE", symbol.upper())
        quote = payload.get("Global Quote") or {}
        price = positive_number(quote.get("05. price"))
        if price is None:
            raise ProviderError("The stock provider did not return a valid price")
        now = datetime.now(timezone.utc)
        normalized = NormalizedMarketData(asset_id=symbol.upper(), name=symbol.upper(), asset_type="stock", symbol=symbol.upper(), currency="USD", current_value=price, price=price, source=SOURCE, timestamp=now, freshness="end_of_day")
        entry = market_data_cache.set(cache_key, normalized.model_dump(mode="json"), self.settings.stock_cache_ttl_seconds)
        normalized.cache_expires_at = entry.expires_at
        return normalized

    def history(self, symbol: str) -> list[HistoricalBar]:
        cache_key = f"stock:history:{symbol.upper()}"
        cached = market_data_cache.get(cache_key)
        if cached:
            return [HistoricalBar.model_validate(item) for item in cached.value]
        payload = self._request("TIME_SERIES_DAILY", symbol.upper(), outputsize="compact")
        series = payload.get("Time Series (Daily)")
        if not isinstance(series, dict):
            raise ProviderError("The stock provider did not return daily history")
        bars = []
        for date, values in series.items():
            try:
                bar = HistoricalBar(symbol=symbol.upper(), date=date, open=float(values["1. open"]), high=float(values["2. high"]), low=float(values["3. low"]), close=float(values["4. close"]), volume=float(values["5. volume"]), source=SOURCE)
            except (KeyError, TypeError, ValueError) as exc:
                raise ProviderError("The stock provider returned invalid historical data") from exc
            if bar.low > bar.high or bar.open > bar.high or bar.open < bar.low or bar.close > bar.high or bar.close < bar.low:
                raise ProviderError("The stock provider returned inconsistent OHLC data")
            bars.append(bar)
        bars.sort(key=lambda item: item.date)
        market_data_cache.set(cache_key, [bar.model_dump(mode="json") for bar in bars], self.settings.stock_cache_ttl_seconds)
        return bars


def positive_number(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None