from __future__ import annotations

from typing import Any


def _safe_number(value: Any, default: float | None = 0.0) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_investor_context(
    user_id: str | None = None,
    profile: dict[str, Any] | None = None,
    latest_stress: dict[str, Any] | None = None,
    history_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = profile or {}
    investment = profile.get("investment", {}) or {}
    goal = profile.get("goal", {}) or {}
    risk = profile.get("risk_assessment", {}) or {}
    liquidity = profile.get("liquidity", {}) or {}
    investor = {
        "user_id": user_id or profile.get("user_id") or "unknown-user",
        "age": profile.get("age"),
        "income": _safe_number(profile.get("monthly_income"), None),
        "monthly_contribution": _safe_number(profile.get("monthly_contribution"), None),
        "risk_level": risk.get("risk_profile"),
        "horizon": investment.get("horizon"),
    }
    target_amount = _safe_number(goal.get("target_amount") or investment.get("target_amount"), None)
    current_progress = _safe_number(goal.get("current_progress") or investment.get("current_progress"), None)
    total_value = _safe_number(profile.get("portfolio_total_value"), None)
    if total_value is None and latest_stress:
        result = latest_stress.get("result", {}) or {}
        total_value = _safe_number(result.get("portfolio_after") or result.get("portfolio_before"), None)
    portfolio = {
        "total_value": total_value,
        "equity": profile.get("portfolio_equity"),
        "debt": profile.get("portfolio_debt"),
        "gold": profile.get("portfolio_gold"),
        "cash": profile.get("portfolio_cash"),
    }
    if latest_stress:
        result = latest_stress.get("result", {}) or {}
        portfolio["total_value"] = _safe_number(result.get("portfolio_after") or result.get("portfolio_before") or portfolio.get("total_value"), portfolio.get("total_value"))
        portfolio["stress_scenario"] = latest_stress.get("scenario_type")
    if history_summary:
        summary = history_summary.get("summary", {}) or {}
        losses = history_summary.get("loss_contributions", []) or []
        largest_loss = losses[0].get("loss") if losses else None
        historical = {
            "total_invested": _safe_number(summary.get("total_invested"), None),
            "current_value": _safe_number(summary.get("current_portfolio_value"), None),
            "unrealized_loss": _safe_number(summary.get("unrealized_gain_loss"), None),
            "largest_loss_contributor": losses[0].get("asset_id") if losses else None,
            "largest_loss_value": _safe_number(largest_loss, None),
        }
    else:
        historical = {
            "total_invested": None,
            "current_value": None,
            "unrealized_loss": None,
            "largest_loss_contributor": None,
            "largest_loss_value": None,
        }
    stress_test = {
        "scenario": latest_stress.get("scenario_type") if latest_stress else None,
        "severity": latest_stress.get("severity") if latest_stress else None,
        "portfolio_change": _safe_number((latest_stress or {}).get("result", {}).get("impact_percent"), None),
        "goal_gap_change": _safe_number((latest_stress or {}).get("result", {}).get("goal_after", {}).get("gap"), None),
    }
    return {
        "investor": investor,
        "goal": {
            "type": goal.get("type") or (investment.get("goal") or "Goal"),
            "target_amount": target_amount,
            "target_date": goal.get("target_date") or investment.get("target_date"),
            "current_progress": current_progress,
            "gap": max(target_amount - total_value, 0.0) if target_amount is not None and total_value is not None else None,
        },
        "portfolio": portfolio,
        "market_analysis": {
            "trend": None,
            "volatility": None,
            "max_drawdown": None,
            "data_status": "unavailable",
        },
        "historical_analysis": historical,
        "stress_test": stress_test,
        "risk_summary": {
            "risk_level": investor["risk_level"],
            "liquidity_status": liquidity.get("emergency_fund_status") or "Unavailable",
        },
    }
