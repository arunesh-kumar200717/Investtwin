from __future__ import annotations

from typing import Any


class ChangeSummaryService:
    def summarize_changes(self, previous: dict[str, Any] | None, current: dict[str, Any] | None) -> list[dict[str, Any]]:
        previous = previous or {}
        current = current or {}
        changes: list[dict[str, Any]] = []

        comparisons = [
            ("portfolio", "portfolio_value", "currency", "portfolio_value"),
            ("portfolio", "equity_allocation", "percentage_points", "allocation.equity"),
            ("goal", "goal_progress", "percentage_points", "goal_progress"),
            ("goal", "goal_gap", "currency", "goal_gap"),
            ("contribution", "monthly_contribution", "currency", "monthly_contribution"),
            ("risk", "risk_level", "text", "risk_level"),
        ]

        for category, metric, unit, path in comparisons:
            prev_value = self._value_for(previous, path)
            curr_value = self._value_for(current, path)
            if prev_value is None or curr_value is None:
                continue
            if prev_value == curr_value:
                continue
            if unit == "currency":
                change = float(curr_value) - float(prev_value)
            elif unit == "percentage_points":
                change = float(curr_value) - float(prev_value)
            elif unit == "text":
                change = f"{prev_value} -> {curr_value}"
            else:
                change = float(curr_value) - float(prev_value)
            changes.append({
                "category": category,
                "metric": metric,
                "previous": prev_value,
                "current": curr_value,
                "change": change,
                "unit": unit,
            })
        return changes

    def _value_for(self, payload: dict[str, Any], path: str) -> Any:
        current = payload
        for part in path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current
