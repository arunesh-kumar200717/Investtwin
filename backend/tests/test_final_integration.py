import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.v1.monitoring import alert_service, monitoring_service
from app.ai.context_builder import build_investor_context
from app.ai.provider import FallbackExplanationProvider
from app.config.settings import Settings, get_settings
from app.main import app


class FinalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_missing_context_is_unavailable_not_invented(self):
        context = build_investor_context(user_id="context-test")
        self.assertIsNone(context["investor"]["risk_level"])
        self.assertIsNone(context["investor"]["horizon"])
        self.assertIsNone(context["portfolio"]["total_value"])
        self.assertIsNone(context["portfolio"]["equity"])
        self.assertEqual(context["market_analysis"]["data_status"], "unavailable")
        self.assertIsNone(context["historical_analysis"]["unrealized_loss"])

    def test_fallback_explains_unavailable_without_fabricating_numbers(self):
        provider = FallbackExplanationProvider()
        result = provider.generate_explanation("PORTFOLIO", "Explain my portfolio", build_investor_context())
        self.assertIn("unavailable", result["summary"])
        history = provider.generate_explanation("LOSS", "Explain my loss", build_investor_context())
        self.assertIn("unavailable", history["summary"])

    def test_top_level_health_contract(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "investtwin"})

    def test_cors_allows_only_the_configured_local_frontend_origin(self):
        allowed = self.client.options("/api/v1/ai/status", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        })
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.headers.get("access-control-allow-origin"), "http://localhost:5173")
        self.assertNotIn("access-control-allow-credentials", allowed.headers)

        denied = self.client.options("/api/v1/ai/status", headers={
            "Origin": "https://untrusted.invalid",
            "Access-Control-Request-Method": "GET",
        })
        self.assertNotIn("access-control-allow-origin", denied.headers)

    def test_system_status_reports_components_without_credentials(self):
        response = self.client.get("/api/v1/system/status")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["backend"]["status"], "available")
        self.assertEqual(body["database"]["status"], "unavailable")
        self.assertEqual(body["market_data"]["live_probe"], "not_performed")
        self.assertIn(body["ai"]["status"], {"available", "unavailable"})
        self.assertFalse(body["monitoring"]["persistent"])
        self.assertNotIn("mongodb://", str(body).lower())
        self.assertNotIn("mongodb+srv://", str(body).lower())
        self.assertNotIn("api_key", str(body).lower())

    def test_demo_reset_is_disabled_without_explicit_demo_setting(self):
        app.dependency_overrides[get_settings] = lambda: Settings(demo_mode=False)
        response = self.client.post("/api/v1/demo/reset", json={})
        self.assertEqual(response.status_code, 404)

    def test_monitoring_rejects_missing_stale_and_empty_baselines(self):
        user_id = f"quality-{uuid4()}"
        missing = self.client.post("/api/v1/monitoring/run", json={"user_id": user_id})
        self.assertEqual(missing.status_code, 422)

        missing_timestamp = self.client.post("/api/v1/monitoring/run", json={
            "user_id": user_id,
            "current_snapshot": {"user_id": user_id, "portfolio_value": 1000},
        })
        self.assertEqual(missing_timestamp.json()["comparison_status"], "timestamp_missing")
        self.assertFalse(missing_timestamp.json()["snapshot_saved"])
        self.assertEqual(missing_timestamp.json()["events"], [])

        stale_timestamp = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        stale = self.client.post("/api/v1/monitoring/run", json={
            "user_id": user_id,
            "current_snapshot": {"user_id": user_id, "timestamp": stale_timestamp, "portfolio_value": 1000},
        })
        self.assertEqual(stale.json()["comparison_status"], "stale_data")
        self.assertFalse(stale.json()["snapshot_saved"])
        self.assertEqual(stale.json()["events"], [])

        empty = self.client.post("/api/v1/monitoring/run", json={
            "user_id": user_id,
            "current_snapshot": {"user_id": user_id, "timestamp": datetime.now(timezone.utc).isoformat(), "portfolio_value": 0},
        })
        self.assertEqual(empty.json()["comparison_status"], "empty_portfolio")
        self.assertFalse(empty.json()["snapshot_saved"])
        self.assertEqual(empty.json()["events"], [])

        baseline = self.client.post("/api/v1/monitoring/run", json={
            "user_id": user_id,
            "current_snapshot": {
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "portfolio_value": 1000,
            },
        })
        self.assertEqual(baseline.json()["comparison_status"], "baseline_only")
        self.assertTrue(baseline.json()["snapshot_saved"])
        self.assertEqual(baseline.json()["events"], [])

        self.assertEqual(len(monitoring_service.get_snapshot_history(user_id)), 1)

    def test_enabled_demo_reset_preserves_non_demo_monitoring_state(self):
        original_snapshots = monitoring_service.snapshots
        original_events = monitoring_service.events
        original_alerts = alert_service.alerts
        try:
            monitoring_service.snapshots = {"demo-investor": [{"portfolio_value": 10}], "real-user": [{"portfolio_value": 20}]}
            monitoring_service.events = [
                {"event_id": "demo-event", "user_id": "demo-investor"},
                {"event_id": "real-event", "user_id": "real-user"},
            ]
            alert_service.alerts = {
                "demo-alert": {"user_id": "demo-investor"},
                "real-alert": {"user_id": "real-user"},
            }
            app.dependency_overrides[get_settings] = lambda: Settings(demo_mode=True)
            response = self.client.post("/api/v1/demo/reset", json={})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["user_id"], "demo-investor")
            self.assertNotIn("demo-investor", monitoring_service.snapshots)
            self.assertIn("real-user", monitoring_service.snapshots)
            self.assertEqual([event["event_id"] for event in monitoring_service.events], ["real-event"])
            self.assertEqual(set(alert_service.alerts), {"real-alert"})
        finally:
            monitoring_service.snapshots = original_snapshots
            monitoring_service.events = original_events
            alert_service.alerts = original_alerts

    def test_demo_reset_database_failure_is_sanitized_and_non_destructive(self):
        original_snapshots = monitoring_service.snapshots
        original_events = monitoring_service.events
        original_alerts = alert_service.alerts
        try:
            monitoring_service.snapshots = {"demo-investor": [{"portfolio_value": 100}]}
            monitoring_service.events = [{"event_id": "demo-event", "user_id": "demo-investor"}]
            alert_service.alerts = {"demo-alert": {"user_id": "demo-investor"}}
            demo_settings = Settings(demo_mode=True)
            demo_settings.database_url = "mocked"
            app.dependency_overrides[get_settings] = lambda: demo_settings
            with patch("app.api.v1.demo.MongoClient", side_effect=RuntimeError("connection details must not leak")):
                response = self.client.post("/api/v1/demo/reset", json={})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("connection details", response.text)
            self.assertIn("demo-investor", monitoring_service.snapshots)
            self.assertEqual(len(monitoring_service.events), 1)
            self.assertIn("demo-alert", alert_service.alerts)
        finally:
            monitoring_service.snapshots = original_snapshots
            monitoring_service.events = original_events
            alert_service.alerts = original_alerts

    def test_stress_monitor_and_reevaluate_flow(self):
        user_id = f"integration-{uuid4()}"
        stress = self.client.post("/api/v1/stress-tests/run", json={
            "user_id": user_id,
            "scenario_type": "market_shock",
            "severity": "custom",
            "parameters": {
                "equity_change_percent": -15,
                "debt_change_percent": -3,
                "gold_change_percent": 1,
                "cash_change_percent": 0,
            },
            "holdings": [
                {"asset_id": "sample-equity", "asset_type": "equity", "value": 6000},
                {"asset_id": "sample-debt", "asset_type": "debt", "value": 4000},
            ],
            "goal_target": 20000,
            "monthly_income": 50000,
            "monthly_contribution": 2000,
        })
        self.assertEqual(stress.status_code, 200)
        self.assertTrue(stress.json()["is_simulation"])
        self.assertLess(stress.json()["impact_percent"], 0)

        timestamp = datetime.now(timezone.utc).isoformat()
        previous = {"user_id": user_id, "timestamp": timestamp, "portfolio_value": 10000, "goal_gap": 10000, "monthly_contribution": 2000}
        current = {"user_id": user_id, "timestamp": timestamp, "portfolio_value": 10000, "goal_gap": 12000, "monthly_contribution": 1500}
        monitored = self.client.post("/api/v1/monitoring/check", json={
            "user_id": user_id,
            "previous_snapshot": previous,
            "current_snapshot": current,
        })
        self.assertEqual(monitored.status_code, 200)
        self.assertTrue(any(event["event_type"] == "CONTRIBUTION_CHANGE" for event in monitored.json()["events"]))
        contribution_event = next(event for event in monitored.json()["events"] if event["event_type"] == "CONTRIBUTION_CHANGE")
        dismissed = self.client.post(f"/api/v1/monitoring/events/{contribution_event['event_id']}/dismiss")
        self.assertEqual(dismissed.status_code, 200)
        self.assertEqual(dismissed.json()["data"]["status"], "DISMISSED")

        reevaluated = self.client.post("/api/v1/monitoring/reevaluate", json={
            "user_id": user_id,
            "trigger_event": "CONTRIBUTION_CHANGE",
            "previous_snapshot": previous,
            "current_snapshot": current,
        })
        self.assertEqual(reevaluated.status_code, 200)
        self.assertIn("goal_analysis", reevaluated.json()["data"]["affected_modules"])
        self.assertTrue(reevaluated.json()["data"]["requires_review"])

    def test_changes_endpoint_compares_previous_and_latest_snapshots(self):
        user_id = f"changes-{uuid4()}"
        for value in (10000, 9400):
            response = self.client.post("/api/v1/monitoring/run", json={
                "user_id": user_id,
                "current_snapshot": {
                    "user_id": user_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "portfolio_value": value,
                    "allocation": {"equity": 50 if value == 10000 else 55},
                    "goal_progress": 25 if value == 10000 else 26,
                    "goal_gap": 100000,
                    "monthly_contribution": 2000,
                    "risk_level": "Moderate",
                },
            })
            self.assertEqual(response.status_code, 200)

        changes = self.client.get("/api/v1/monitoring/changes", params={"user_id": user_id})
        self.assertEqual(changes.status_code, 200)
        changed_metrics = {item["metric"]: item for item in changes.json()["data"]}
        self.assertEqual(changed_metrics["portfolio_value"]["previous"], 10000)
        self.assertEqual(changed_metrics["portfolio_value"]["current"], 9400)
        self.assertEqual(changed_metrics["equity_allocation"]["previous"], 50)
        self.assertEqual(changed_metrics["equity_allocation"]["current"], 55)


if __name__ == "__main__":
    unittest.main()
