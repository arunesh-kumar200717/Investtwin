import unittest

import pandas as pd

from app.analysis.analysis_service import analyze_history
from app.analysis.portfolio_impact import HoldingInput, PortfolioImpactInput, portfolio_impact
from app.analysis.portfolio_exposure import ExposureHolding, ExposureInput, GoalProgressInput, calculate_exposure, calculate_goal_progress


def make_bars(values: list[float]) -> list[dict]:
    dates = pd.date_range("2026-01-01", periods=len(values), freq="D")
    return [{"symbol": "TEST", "date": date.date().isoformat(), "open": value, "high": value + 1, "low": value - 1, "close": value, "volume": 1000, "source": "test"} for date, value in zip(dates, values)]


class AnalysisTests(unittest.TestCase):
    def test_returns_moving_average_and_drawdown(self) -> None:
        result = analyze_history("TEST", make_bars([100, 110, 99] + [100] * 57), "test")
        self.assertEqual(result["data_status"], "available")
        self.assertEqual(result["returns"]["1D"]["return_percent"], 0.0)
        self.assertLess(result["risk"]["maximum_drawdown_percent"], 0)
        self.assertIsNotNone(result["moving_averages"]["MA20"])

    def test_return_and_drawdown_formula_examples(self) -> None:
        result = analyze_history("TEST", make_bars([100, 80, 100]), "test")
        self.assertEqual(result["returns"]["1D"]["return_percent"], 25.0)
        self.assertEqual(result["risk"]["maximum_drawdown_percent"], -20.0)

    def test_insufficient_history_does_not_fabricate_long_average(self) -> None:
        result = analyze_history("TEST", make_bars([100, 101, 102]), "test")
        self.assertIsNone(result["moving_averages"]["MA20"])
        self.assertEqual(result["returns"]["30D"]["status"], "unavailable")

    def test_illustrative_portfolio_impact(self) -> None:
        result = portfolio_impact(PortfolioImpactInput(holdings=[HoldingInput(asset_id="A", asset_type="stock", value=3000), HoldingInput(asset_id="B", asset_type="stock", value=7000)], asset_id="A", movement_percent=-10))
        self.assertEqual(result["illustrative_portfolio_impact_percent"], -3.0)

    def test_exposure_concentration_and_goal_progress(self) -> None:
        exposure = calculate_exposure(ExposureInput(holdings=[ExposureHolding(asset_id="A", asset_type="equity", value=6000), ExposureHolding(asset_id="B", asset_type="debt", value=4000)]))
        self.assertEqual(exposure["allocation"]["equity"], 60.0)
        self.assertEqual(exposure["alerts"][0]["type"], "concentration")
        progress = calculate_goal_progress(GoalProgressInput(target_amount=500000, current_portfolio_value=320000))
        self.assertEqual(progress["goal_progress_percent"], 64.0)


if __name__ == "__main__":
    unittest.main()