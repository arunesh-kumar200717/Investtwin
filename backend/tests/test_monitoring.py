import unittest
from datetime import datetime, timezone

from app.services.monitoring_service import MonitoringService
from app.services.alert_service import AlertService
from app.services.reevaluation_service import ReevaluationService


class MonitoringServiceTests(unittest.TestCase):
    def test_snapshot_creation_and_change_detection(self):
        service = MonitoringService()
        previous = service.build_snapshot(
            user_id="user-1",
            portfolio_value=100000,
            allocation={"equity": 42, "debt": 30, "gold": 10, "cash": 18},
            risk_level="Moderate",
            goal_progress=34,
            goal_gap=200000,
            monthly_contribution=5000,
            liquidity=120000,
            concentration=28,
            market_metrics={"volatility": 18, "drawdown": 6},
            portfolio_drift=3,
        )
        current = service.build_snapshot(
            user_id="user-1",
            portfolio_value=94000,
            allocation={"equity": 52, "debt": 24, "gold": 10, "cash": 14},
            risk_level="Moderately High",
            goal_progress=35,
            goal_gap=220000,
            monthly_contribution=3000,
            liquidity=105000,
            concentration=31,
            market_metrics={"volatility": 26, "drawdown": 12},
            portfolio_drift=10,
        )
        events = service.detect_changes(previous, current)
        self.assertTrue(any(event["event_type"] == "PORTFOLIO_VALUE_CHANGE" for event in events))
        self.assertTrue(any(event["event_type"] == "PORTFOLIO_DRIFT" for event in events))
        self.assertTrue(any(event["event_type"] == "CONTRIBUTION_CHANGE" for event in events))

    def test_alert_deduplication(self):
        alerts = AlertService()
        alert = alerts.create_or_update_alert(
            user_id="user-1",
            event_type="PORTFOLIO_DRIFT",
            severity="MEDIUM",
            details={"asset_id": "equity", "threshold": 5, "current_value": 58, "previous_value": 50},
        )
        alert2 = alerts.create_or_update_alert(
            user_id="user-1",
            event_type="PORTFOLIO_DRIFT",
            severity="MEDIUM",
            details={"asset_id": "equity", "threshold": 5, "current_value": 60, "previous_value": 50},
        )
        self.assertEqual(alert["event_id"], alert2["event_id"])
        self.assertGreater(alert2["occurrence_count"], alert["occurrence_count"])

    def test_reevaluation_dependency_selection(self):
        service = ReevaluationService()
        result = service.reevaluate_investment_twin(
            user_id="user-1",
            trigger_event="CONTRIBUTION_CHANGE",
            previous_snapshot={"goal_gap": 200000, "monthly_contribution": 5000},
            current_snapshot={"goal_gap": 240000, "monthly_contribution": 3000},
        )
        self.assertIn("goal_analysis", result["affected_modules"])
        self.assertIn("goal_gap", result["affected_modules"])
        self.assertTrue(result["requires_review"])

    def test_market_metrics_without_fresh_timestamp_do_not_alert(self):
        service = MonitoringService()
        now = datetime.now(timezone.utc).isoformat()
        previous = {"user_id": "user-1", "timestamp": now, "portfolio_value": 1000, "market_metrics": {"volatility": 10, "drawdown": 2}}
        current = {"user_id": "user-1", "timestamp": now, "portfolio_value": 1000, "market_metrics": {"volatility": 40, "drawdown": 20}}
        self.assertEqual(service.detect_changes(previous, current), [])

        current["market_metrics"]["timestamp"] = now
        current["market_metrics"]["data_status"] = "stale"
        self.assertEqual(service.detect_changes(previous, current), [])


if __name__ == "__main__":
    unittest.main()
