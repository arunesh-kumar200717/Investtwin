from __future__ import annotations

from typing import Any


class ReevaluationService:
    DEPENDENCY_MAP = {
        "CONTRIBUTION_CHANGE": ["goal_analysis", "goal_gap", "goal_timeline"],
        "PORTFOLIO_DRIFT": ["portfolio_risk", "drift", "concentration", "stress_test"],
        "MARKET_VOLATILITY_CHANGE": ["market_analysis", "portfolio_impact", "stress_test"],
        "GOAL_DEADLINE_CHANGE": ["goal_analysis", "contribution_gap", "portfolio_suitability", "stress_test"],
        "RISK_CHANGE": ["risk_review", "stress_test", "portfolio_analysis"],
        "LIQUIDITY_CHANGE": ["liquidity_review", "goal_analysis"],
    }

    def reevaluate_investment_twin(
        self,
        user_id: str,
        trigger_event: str,
        previous_snapshot: dict[str, Any] | None = None,
        current_snapshot: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        affected_modules = self.DEPENDENCY_MAP.get(trigger_event, ["portfolio_analysis"])
        requires_review = self._requires_review(trigger_event, previous_snapshot, current_snapshot)
        updates = {
            "user_id": user_id,
            "trigger": trigger_event,
            "affected_modules": affected_modules,
            "changes": [],
            "alerts": [],
            "updated_metrics": current_snapshot or {},
            "requires_review": requires_review,
            "ai_summary": {
                "event": trigger_event,
                "summary": "The monitoring system detected a meaningful change requiring investor review.",
            },
        }
        return updates

    def _requires_review(self, trigger_event: str, previous_snapshot: dict[str, Any] | None, current_snapshot: dict[str, Any] | None) -> bool:
        if trigger_event == "CONTRIBUTION_CHANGE":
            if not previous_snapshot or not current_snapshot:
                return True
            previous = float(previous_snapshot.get("monthly_contribution") or 0)
            current = float(current_snapshot.get("monthly_contribution") or 0)
            return abs(previous - current) > 0
        if previous_snapshot and current_snapshot:
            prev_gap = float(previous_snapshot.get("goal_gap") or 0)
            curr_gap = float(current_snapshot.get("goal_gap") or 0)
            if abs(curr_gap - prev_gap) > 0:
                return True
        return trigger_event in {"PORTFOLIO_DRIFT", "RISK_CHANGE", "LIQUIDITY_CHANGE", "GOAL_DEADLINE_CHANGE"}
