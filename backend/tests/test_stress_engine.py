import unittest
from pydantic import ValidationError

from app.stress.models import StressHolding, StressRequest
from app.stress.stress_engine import run_stress


class StressEngineTests(unittest.TestCase):
    def holdings(self):
        return [StressHolding(asset_id="equity", asset_type="equity", value=50000), StressHolding(asset_id="debt", asset_type="debt", value=50000)]

    def test_market_shock_is_simulation(self):
        result = run_stress(StressRequest(user_id="user-12345678", scenario_type="market_shock", severity="moderate", holdings=self.holdings(), goal_target=200000))
        self.assertTrue(result["is_simulation"])
        self.assertEqual(result["portfolio_before"], 100000)
        self.assertEqual(result["portfolio_after"], 87500)
        self.assertEqual(result["impact_percent"], -12.5)

    def test_asset_shock_uses_weight(self):
        result = run_stress(StressRequest(user_id="user-12345678", scenario_type="asset_shock", severity="custom", parameters={"asset_id": "equity", "asset_change_percent": -20}, holdings=self.holdings()))
        self.assertEqual(result["impact_percent"], -10.0)

    def test_emergency_expense_reports_liquidity_gap(self):
        result = run_stress(StressRequest(user_id="user-12345678", scenario_type="emergency_expense", severity="custom", parameters={"emergency_expense": 80000}, holdings=[StressHolding(asset_id="cash", asset_type="cash", value=50000), StressHolding(asset_id="equity", asset_type="equity", value=50000)]))
        self.assertEqual(result["liquidity_gap"], 30000)
        self.assertEqual(result["portfolio_after"], 20000)

    def test_recovery_mathematics(self):
        result = run_stress(StressRequest(user_id="user-12345678", scenario_type="asset_shock", severity="custom", parameters={"asset_id": "equity", "asset_change_percent": -30}, holdings=[StressHolding(asset_id="equity", asset_type="equity", value=10000)]))
        self.assertAlmostEqual(result["recovery_requirement_percent"], 42.8571, places=3)

    def test_twenty_percent_loss_requires_twenty_five_percent_recovery(self):
        result = run_stress(StressRequest(
            user_id="user-12345678",
            scenario_type="asset_shock",
            severity="custom",
            parameters={"asset_id": "equity", "asset_change_percent": -20},
            holdings=[StressHolding(asset_id="equity", asset_type="equity", value=100)],
        ))
        self.assertEqual(result["portfolio_after"], 80)
        self.assertEqual(result["impact_percent"], -20)
        self.assertEqual(result["recovery_requirement_percent"], 25)

    def test_expense_cannot_create_negative_portfolio_or_fake_recovery(self):
        result = run_stress(StressRequest(
            user_id="user-12345678",
            scenario_type="emergency_expense",
            severity="custom",
            parameters={"emergency_expense": 150},
            holdings=[StressHolding(asset_id="cash", asset_type="cash", value=100)],
        ))
        self.assertEqual(result["portfolio_after"], 0)
        self.assertEqual(result["impact_percent"], -100)
        self.assertIsNone(result["recovery_requirement_percent"])

    def test_unknown_scenarios_and_assets_are_rejected(self):
        with self.assertRaises(ValidationError):
            StressRequest(user_id="user-12345678", scenario_type="unknown", holdings=self.holdings())
        with self.assertRaises(ValidationError):
            StressRequest(user_id="user-12345678", scenario_type="asset_shock", parameters={"asset_id": "missing", "asset_change_percent": -20}, holdings=self.holdings())
        with self.assertRaises(ValidationError):
            StressHolding(asset_id="asset", asset_type="not-an-asset", value=100)


if __name__ == "__main__":
    unittest.main()