from datetime import datetime, timezone

import httpx

from app.config.settings import Settings
from app.data.cache import market_data_cache
from app.data.market_models import NormalizedMarketData
from app.data.provider_client import ProviderError

AMFI_URL = "https://portal.amfiindia.com/spages/NAVAll.txt"
SOURCE = "AMFI India"


class MutualFundDataService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def latest(self, query: str | None = None) -> list[NormalizedMarketData]:
        cache_key = "mutual-funds:latest"
        cached = market_data_cache.get(cache_key)
        if cached:
            values = [NormalizedMarketData.model_validate(item) for item in cached.value]
            for value in values:
                value.data_status = "cached"
                value.cache_expires_at = cached.expires_at
        else:
            try:
                response = httpx.get(AMFI_URL, timeout=self.settings.external_request_timeout_seconds, follow_redirects=True)
                response.raise_for_status()
                text = response.content.decode("utf-8-sig")
            except (httpx.RequestError, httpx.HTTPStatusError, UnicodeDecodeError) as exc:
                raise ProviderError("AMFI NAV data is temporarily unavailable") from exc
            values = parse_amfi_latest(text)
            if not values:
                raise ProviderError("AMFI returned no valid NAV records")
            market_data_cache.set(cache_key, [value.model_dump(mode="json") for value in values], self.settings.mutual_fund_cache_ttl_seconds)
        if query:
            query_lower = query.lower()
            values = [value for value in values if query_lower in value.name.lower() or query_lower in (value.symbol or "").lower()]
        return values[:100]


def parse_amfi_latest(text: str) -> list[NormalizedMarketData]:
    records = []
    for line in text.splitlines():
        fields = [field.strip() for field in line.split(";")]
        if len(fields) < 8 or not fields[0].isdigit():
            continue
        try:
            nav = float(fields[6])
            if nav <= 0:
                continue
            nav_date = datetime.strptime(fields[7], "%d-%b-%Y").replace(tzinfo=timezone.utc)
        except (ValueError, IndexError):
            continue
        scheme_code = fields[0]
        records.append(NormalizedMarketData(asset_id=scheme_code, name=fields[3], asset_type="mutual_fund", symbol=scheme_code, currency="INR", nav=nav, source=SOURCE, timestamp=nav_date, freshness="latest_nav"))
    return records