from datetime import date

from app.stress.scenario_config import SCENARIOS


def scenario_defaults(scenario_type: str, severity: str) -> dict:
    values = SCENARIOS.get(scenario_type, {}).get(severity)
    if values is None:
        raise ValueError("Unsupported scenario or severity")
    return dict(values) if isinstance(values, dict) else {"value": values}


def run_stress(payload) -> dict:
    parameters = dict(payload.parameters)
    if payload.scenario_type in SCENARIOS and payload.severity != "custom":
        defaults = scenario_defaults(payload.scenario_type, payload.severity)
        defaults.update(parameters)
        parameters = defaults
    if payload.scenario_type == "combined":
        parameters.setdefault("asset_id", largest_asset(payload.holdings).asset_id if payload.holdings else None)
        parameters.setdefault("asset_change_percent", -20)
        parameters.setdefault("income_change_percent", -25)
        parameters.setdefault("contribution_change_percent", -30)
        parameters.setdefault("emergency_expense", 50000)
        parameters.setdefault("goal_deadline_change_months", -6)
    before_total = sum(item.value for item in payload.holdings)
    if before_total <= 0:
        return {"is_simulation": True, "data_status": "unavailable", "message": "A positive portfolio value is required."}
    changes = {item.asset_id: movement_for(item, payload, parameters) for item in payload.holdings}
    stressed_values = [{"asset_id": item.asset_id, "asset_type": item.asset_type, "before_value": item.value, "change_percent": changes[item.asset_id], "after_value": round(item.value * (1 + changes[item.asset_id] / 100), 2)} for item in payload.holdings]
    expense = float(parameters.get("emergency_expense", 0) or 0)
    stressed_total = round(max(sum(item["after_value"] for item in stressed_values) - expense, 0), 2)
    impact = round(stressed_total - before_total, 2)
    goal_before = goal_snapshot(payload.goal_target, before_total)
    goal_after = goal_snapshot(payload.goal_target, stressed_total)
    if 0 < stressed_total < before_total:
        recovery = round((before_total / stressed_total - 1) * 100, 4)
    elif stressed_total == 0 and before_total > 0:
        recovery = None
    else:
        recovery = 0
    liquid_assets = sum(item.value for item in payload.holdings if item.asset_type in {"cash", "fd", "liquid"})
    liquidity_gap = max(expense - liquid_assets, 0)
    income_change = float(parameters.get("income_change_percent", 0) or 0)
    contribution_change = float(parameters.get("contribution_change_percent", 0) or 0)
    new_contribution = parameters.get("new_monthly_contribution")
    if new_contribution is None:
        new_contribution = payload.monthly_contribution * (1 + contribution_change / 100)
    goal_change = round(goal_after["progress_percent"] - goal_before["progress_percent"], 4) if goal_after["progress_percent"] is not None and goal_before["progress_percent"] is not None else None
    return {"is_simulation": True, "scenario": payload.scenario_type, "severity": payload.severity, "assumptions": parameters, "portfolio_before": round(before_total, 2), "portfolio_after": stressed_total, "impact_amount": impact, "impact_percent": round(impact / before_total * 100, 4), "holdings": stressed_values, "allocation_before": allocation(payload.holdings, before_total), "allocation_after": allocation_from_values(stressed_values, stressed_total), "goal_before": goal_before, "goal_after": goal_after, "goal_progress_change_points": goal_change, "recovery_requirement_percent": recovery, "income_before": payload.monthly_income, "income_after": round(payload.monthly_income * (1 + income_change / 100), 2), "contribution_before": payload.monthly_contribution, "contribution_after": round(max(float(new_contribution), 0), 2), "liquidity_gap": round(liquidity_gap, 2), "risk_changes": risk_changes(stressed_values), "historical_pattern_overlap": [], "resilience_breakdown": resilience_breakdown(impact, liquidity_gap, goal_change), "data_status": "available", "analysis_date": date.today().isoformat(), "assumptions_note": "This is a simulated scenario, not a prediction. Other factors are held constant unless shown in the assumptions."}


def movement_for(item, payload, parameters):
    if payload.scenario_type in {"asset_shock", "concentration_shock"}:
        target = parameters.get("asset_id") or largest_asset(payload.holdings).asset_id
        return float(parameters.get("asset_change_percent", parameters.get("value", 0))) if item.asset_id == target else 0
    key = f"{item.asset_type}_change_percent"
    return float(parameters.get(key, 0))


def largest_asset(holdings):
    return max(holdings, key=lambda item: item.value)


def goal_snapshot(target, value):
    if not target:
        return {"target_amount": None, "value": round(value, 2), "progress_percent": None, "gap": None}
    return {"target_amount": target, "value": round(value, 2), "progress_percent": round(min(value / target * 100, 100), 4), "gap": round(max(target - value, 0), 2)}


def allocation(holdings, total):
    return {item.asset_type: round(sum(h.value for h in holdings if h.asset_type == item.asset_type) / total * 100, 4) for item in holdings}


def allocation_from_values(holdings, total):
    return {asset_type: round(sum(item["after_value"] for item in holdings if item["asset_type"] == asset_type) / total * 100, 4) for asset_type in {item["asset_type"] for item in holdings} if total > 0}


def risk_changes(holdings):
    largest = max(holdings, key=lambda item: item["after_value"]) if holdings else None
    return [{"type": "largest_exposure", "value": largest["asset_id"], "after_value": largest["after_value"]}] if largest else []


def resilience_breakdown(impact, liquidity_gap, goal_change):
    return {"portfolio_impact": "high" if impact < 0 and abs(impact) > 0.2 else "moderate" if impact < 0 else "low", "liquidity_impact": "high" if liquidity_gap > 0 else "low", "goal_impact": "unavailable" if goal_change is None else "high" if goal_change < -10 else "moderate" if goal_change < 0 else "low"}