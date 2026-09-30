import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.config.settings import Settings
from app.data.market_models import NormalizedMarketData
from app.data.mutual_fund_service import MutualFundDataService, parse_amfi_latest


class MutualFundDataTests(unittest.TestCase):
    def test_amfi_record_without_source_date_is_discarded(self):
        missing_date = "100;ISIN1;ISIN2;Example Fund;NA;NA;12.34"
        self.assertEqual(parse_amfi_latest(missing_date), [])

    def test_amfi_timestamp_comes_from_source_record(self):
        dated_record = "100;ISIN1;ISIN2;Example Fund;NA;NA;12.34;29-Sep-2026"
        result = parse_amfi_latest(dated_record)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].timestamp.date().isoformat(), "2026-09-29")
        self.assertEqual(result[0].data_status, "available")

    def test_cache_hit_is_labeled_cached(self):
        observed_at = datetime.now(timezone.utc)
        cached_until = observed_at + timedelta(minutes=20)
        item = NormalizedMarketData(
            asset_id="100",
            name="Example Fund",
            asset_type="mutual_fund",
            symbol="100",
            currency="INR",
            nav=12.34,
            source="AMFI India",
            timestamp=observed_at,
            freshness="latest_nav",
        )
        cache = Mock()
        cache.get.return_value = SimpleNamespace(value=[item.model_dump(mode="json")], expires_at=cached_until)
        with patch("app.data.mutual_fund_service.market_data_cache", cache):
            response = MutualFundDataService(Settings()).latest()
        self.assertEqual(response[0].data_status, "cached")
        self.assertEqual(response[0].cache_expires_at, cached_until)


if __name__ == "__main__":
    unittest.main()
