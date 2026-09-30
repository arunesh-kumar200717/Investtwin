from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.config.settings import get_settings


class MonitoringService:
    def __init__(self) -> None:
        self.snapshots: dict[str, list[dict[str, Any]]] = {}
        self.events: list[dict[str, Any]] = []

    def build_snapshot(
        self,
        user_id: str,
        portfolio_value: float | None = None,
        allocation: dict[str, Any] | None = None,
        risk_level: str | None = None,
        goal_progress: float | None = None,
        goal_gap: float | None = None,
        monthly_contribution: float | None = None,
        liquidity: float | None = None,
        concentration: float | None = None,
        market_metrics: dict[str, Any] | None = None,
        portfolio_drift: float | None = None,
        active_stress_result: dict[str, Any] | None = None,
        timestamp: str | None = None,
        data_status: str | None = None,
    ) -> dict[str, Any]:
        snapshot = {
            "user_id": user_id,
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "portfolio_value": self._optional_float(portfolio_value),
            "allocation": allocation,
            "risk_level": risk_level,
            "goal_progress": self._optional_float(goal_progress),
            "goal_gap": self._optional_float(goal_gap),
            "monthly_contribution": self._optional_float(monthly_contribution),
            "liquidity": self._optional_float(liquidity),
            "concentration": self._optional_float(concentration),
            "market_metrics": market_metrics,
            "portfolio_drift": self._optional_float(portfolio_drift),
            "active_stress_result": active_stress_result,
            "data_status": data_status,
        }
        self.snapshots.setdefault(user_id, []).append(snapshot)
        return snapshot

    def get_latest_snapshot(self, user_id: str, include_last: bool = False) -> dict[str, Any] | None:
        snapshots = self.snapshots.get(user_id, [])
        if not snapshots:
            return None
        return snapshots[-1] if include_last else snapshots[-1]

    def get_snapshot_history(self, user_id: str) -> list[dict[str, Any]]:
        return self.snapshots.get(user_id, [])

    def comparison_status(self, previous: dict[str, Any] | None, current: dict[str, Any] | None) -> str:
        current_status = self._snapshot_status(current)
        if current_status != "reliable":
            return current_status
        if previous is None:
            return "baseline_only"
        previous_status = self._snapshot_status(previous)
        if previous_status != "reliable":
            return "insufficient_previous_data"
        return "compared"

    def _snapshot_status(self, snapshot: dict[str, Any] | None) -> str:
        if not isinstance(snapshot, dict):
            return "snapshot_missing"
        timestamp = snapshot.get("timestamp")
        if not isinstance(timestamp, str) or not timestamp.strip():
            return "timestamp_missing"
        try:
            observed_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return "timestamp_invalid"
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age_seconds = (now - observed_at.astimezone(timezone.utc)).total_seconds()
        if age_seconds < -300 or age_seconds > get_settings().monitoring_snapshot_max_age_seconds:
            return "stale_data"
        data_statuses = {
            str(snapshot.get(key) or "").lower()
            for key in ("data_status", "market_data_status")
        }
        if data_statuses & {"stale", "unavailable", "error"}:
            return "unreliable_data"
        portfolio_value = self._optional_float(snapshot.get("portfolio_value"))
        if portfolio_value is None:
            return "portfolio_value_missing"
        if portfolio_value <= 0:
            return "empty_portfolio"
        return "reliable"

    def detect_changes(self, previous: dict[str, Any] | None, current: dict[str, Any] | None) -> list[dict[str, Any]]:
        if self.comparison_status(previous, current) != "compared":
            return []

        events: list[dict[str, Any]] = []
        thresholds = get_settings().monitoring_thresholds

        risk = self._compare_metric("portfolio_value", previous, current, thresholds["portfolio_value_change_percent"], "%")
        if risk:
            events.append(risk)

        previous_drift = self._optional_float(previous.get("portfolio_drift"))
        current_drift = self._optional_float(current.get("portfolio_drift"))
        drift_change = current_drift - previous_drift if previous_drift is not None and current_drift is not None else None
        if drift_change is not None and abs(drift_change) >= float(thresholds["allocation_drift_percentage_points"]):
            events.append({
                "event_id": self._new_event_id(),
                "user_id": current.get("user_id") or previous.get("user_id"),
                "event_type": "PORTFOLIO_DRIFT",
                "severity": self._severity_for(abs(drift_change)),
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "previous_value": previous.get("portfolio_drift"),
                "current_value": current.get("portfolio_drift"),
                "change": drift_change,
                "threshold": thresholds["allocation_drift_percentage_points"],
                "source": "portfolio_analysis",
                "status": "UNREAD",
            })

        if previous.get("risk_level") is not None and current.get("risk_level") is not None and previous.get("risk_level") != current.get("risk_level"):
            events.append({
                "event_id": self._new_event_id(),
                "user_id": current.get("user_id") or previous.get("user_id"),
                "event_type": "RISK_CHANGE",
                "severity": "MEDIUM",
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "previous_value": previous.get("risk_level"),
                "current_value": current.get("risk_level"),
                "change": 1,
                "threshold": 0,
                "source": "risk_analysis",
                "status": "UNREAD",
            })

        previous_contribution = self._optional_float(previous.get("monthly_contribution"))
        current_contribution = self._optional_float(current.get("monthly_contribution"))
        if previous_contribution is not None and current_contribution is not None and previous_contribution != current_contribution:
            events.append({
                "event_id": self._new_event_id(),
                "user_id": current.get("user_id") or previous.get("user_id"),
                "event_type": "CONTRIBUTION_CHANGE",
                "severity": "MEDIUM",
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "previous_value": previous.get("monthly_contribution"),
                "current_value": current.get("monthly_contribution"),
                "change": current_contribution - previous_contribution,
                "threshold": 0,
                "source": "goal_analysis",
                "status": "UNREAD",
            })

        previous_goal_gap = self._optional_float(previous.get("goal_gap"))
        current_goal_gap = self._optional_float(current.get("goal_gap"))
        if previous_goal_gap is not None and current_goal_gap is not None:
            percent_change = self._pct_change(previous_goal_gap, current_goal_gap)
            if abs(percent_change) >= float(thresholds["goal_gap_change_percent"]):
                events.append({
                    "event_id": self._new_event_id(),
                    "user_id": current.get("user_id") or previous.get("user_id"),
                    "event_type": "GOAL_GAP_CHANGE",
                    "severity": self._severity_for(abs(percent_change)),
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "previous_value": previous.get("goal_gap"),
                    "current_value": current.get("goal_gap"),
                    "change": percent_change,
                    "threshold": thresholds["goal_gap_change_percent"],
                    "source": "goal_analysis",
                    "status": "UNREAD",
                })

        previous_concentration = self._optional_float(previous.get("concentration"))
        current_concentration = self._optional_float(current.get("concentration"))
        if previous_concentration is not None and current_concentration is not None:
            concentration_change = abs(current_concentration - previous_concentration)
            if concentration_change >= float(thresholds["concentration_percentage"]):
                events.append({
                    "event_id": self._new_event_id(),
                    "user_id": current.get("user_id") or previous.get("user_id"),
                    "event_type": "CONCENTRATION",
                    "severity": self._severity_for(concentration_change),
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "previous_value": previous.get("concentration"),
                    "current_value": current.get("concentration"),
                    "change": concentration_change,
                    "threshold": thresholds["concentration_percentage"],
                    "source": "portfolio_analysis",
                    "status": "UNREAD",
                })

        previous_market = self._reliable_market_metrics(previous)
        current_market = self._reliable_market_metrics(current)
        prev_vol = self._optional_float(previous_market.get("volatility"))
        curr_vol = self._optional_float(current_market.get("volatility"))
        vol_change = self._pct_change(prev_vol, curr_vol) if prev_vol is not None and curr_vol is not None else None
        if vol_change is not None and abs(vol_change) >= float(thresholds["volatility_change_percent"]):
            events.append({
                "event_id": self._new_event_id(),
                "user_id": current.get("user_id") or previous.get("user_id"),
                "event_type": "VOLATILITY_CHANGE",
                "severity": self._severity_for(abs(vol_change)),
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "previous_value": prev_vol,
                "current_value": curr_vol,
                "change": vol_change,
                "threshold": thresholds["volatility_change_percent"],
                "source": "market_data",
                "status": "UNREAD",
            })

        prev_draw = self._optional_float(previous_market.get("drawdown"))
        curr_draw = self._optional_float(current_market.get("drawdown"))
        if prev_draw is not None and curr_draw is not None and abs(curr_draw - prev_draw) >= float(thresholds["drawdown_percentage"]):
            events.append({
                "event_id": self._new_event_id(),
                "user_id": current.get("user_id") or previous.get("user_id"),
                "event_type": "DRAWDOWN",
                "severity": self._severity_for(abs(curr_draw - prev_draw)),
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "previous_value": prev_draw,
                "current_value": curr_draw,
                "change": curr_draw - prev_draw,
                "threshold": thresholds["drawdown_percentage"],
                "source": "market_data",
                "status": "UNREAD",
            })

        self.events.extend(events)
        return events

    def _reliable_market_metrics(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        metrics = snapshot.get("market_metrics")
        if not isinstance(metrics, dict):
            return {}
        status = str(metrics.get("data_status") or snapshot.get("market_data_status") or "").lower()
        if status in {"stale", "unavailable", "error"}:
            return {}
        timestamp = metrics.get("timestamp") or snapshot.get("market_data_timestamp")
        if not isinstance(timestamp, str) or not timestamp.strip():
            return {}
        try:
            observed_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return {}
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)
        age_seconds = (datetime.now(timezone.utc) - observed_at.astimezone(timezone.utc)).total_seconds()
        if age_seconds < -300 or age_seconds > get_settings().monitoring_snapshot_max_age_seconds:
            return {}
        return metrics

    def _compare_metric(self, metric: str, previous: dict[str, Any], current: dict[str, Any], threshold: float, unit: str) -> dict[str, Any] | None:
        prev_value = self._optional_float(previous.get(metric))
        curr_value = self._optional_float(current.get(metric))
        if prev_value is None or curr_value is None:
            return None
        change = curr_value - prev_value
        if abs(change) == 0:
            return None
        if metric == "portfolio_value":
            percent_change = self._pct_change(prev_value, curr_value)
            if abs(percent_change) >= threshold:
                return {
                    "event_id": self._new_event_id(),
                    "user_id": current.get("user_id") or previous.get("user_id"),
                    "event_type": "PORTFOLIO_VALUE_CHANGE",
                    "severity": self._severity_for(abs(percent_change)),
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "previous_value": prev_value,
                    "current_value": curr_value,
                    "change": percent_change,
                    "threshold": threshold,
                    "source": "portfolio_analysis",
                    "status": "UNREAD",
                    "details": {"unit": unit},
                }
        return None

    def _new_event_id(self) -> str:
        return f"event-{datetime.now(timezone.utc).timestamp()}"

    def _pct_change(self, previous_value: float, current_value: float) -> float:
        if previous_value == 0:
            return 0.0 if current_value == 0 else 100.0
        return ((current_value - previous_value) / abs(previous_value)) * 100

    def _optional_float(self, value: Any) -> float | None:
        if value is None or isinstance(value, bool):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _severity_for(self, value: float) -> str:
        if value < 2:
            return "INFO"
        if value < 5:
            return "LOW"
        if value < 10:
            return "MEDIUM"
        if value < 20:
            return "HIGH"
        return "CRITICAL"
