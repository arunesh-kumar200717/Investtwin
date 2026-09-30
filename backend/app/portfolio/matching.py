from dataclasses import dataclass

from app.models.user_profile import UserProfile
from app.portfolio.rules import HORIZON_LABELS, MATCH_WEIGHTS, target_allocation


@dataclass
class CandidateProduct:
    asset_type: str
    name: str
    source: str | None
    data_status: str
    liquidity: str
    risk_level: str
    horizon: str


def match_profile(profile: UserProfile, candidates: list[CandidateProduct], holdings: list[dict]) -> dict:
    risk = profile.risk_assessment.risk_profile.lower()
    horizon = HORIZON_LABELS.get(profile.investment.horizon, "medium_term")
    available = {candidate.asset_type for candidate in candidates if candidate.data_status in {"available", "cached"}}
    available.add("cash")
    allocation = target_allocation(risk, profile.investment.horizon, profile.investment.goal, available)
    total_contribution = profile.monthly_contribution
    contribution_split = {category: round(total_contribution * percent / 100, 2) for category, percent in allocation.items()}
    if contribution_split:
        largest = max(contribution_split)
        contribution_split[largest] = round(contribution_split[largest] + total_contribution - sum(contribution_split.values()), 2)
    matched = []
    for candidate in candidates:
        if candidate.asset_type not in allocation or allocation[candidate.asset_type] <= 0:
            continue
        score, reasons = score_candidate(candidate, risk, horizon, profile.investment.goal, profile.liquidity.emergency_fund_status)
        matched.append({"asset_type": candidate.asset_type, "name": candidate.name, "compatibility_score": score, "candidate_allocation_percent": allocation[candidate.asset_type], "candidate_contribution": contribution_split.get(candidate.asset_type, 0), "source": candidate.source, "data_status": candidate.data_status, "reasons": reasons})
    current = current_allocation(holdings)
    drift = [{"asset_type": category, "current_weight_percent": round(current.get(category, 0), 4), "target_weight_percent": allocation.get(category, 0), "drift_percentage_points": round(current.get(category, 0) - allocation.get(category, 0), 4)} for category in sorted(set(current) | set(allocation))]
    current_value = sum(float(item.get("value", 0)) for item in holdings)
    target = profile.investment.target_amount
    return {"status": "success", "profile": {"risk_category": profile.risk_assessment.risk_profile, "risk_score": profile.risk_assessment.score, "horizon": horizon, "goal": profile.investment.goal, "liquidity_status": profile.liquidity.emergency_fund_status}, "candidate_allocation": allocation, "monthly_contribution": {"total": total_contribution, **contribution_split}, "candidates": matched, "current_allocation": current, "drift": drift, "goal_progress": {"target_amount": target, "current_portfolio_value": current_value, "progress_percent": round(min(current_value / target * 100, 100), 4) if target else None, "remaining_amount": max(target - current_value, 0)}, "risk_flags": [], "data_status": "live" if any(item["data_status"] == "available" for item in matched) else "unavailable", "rules_note": "Allocation percentages and compatibility weights are application-defined decision-support rules, not guarantees."}


def score_candidate(candidate: CandidateProduct, risk: str, horizon: str, goal: str, emergency_status: str) -> tuple[float, list[str]]:
    risk_match = 1.0 if candidate.risk_level == risk else 0.7 if candidate.risk_level in {"moderate", "growth"} and risk in {"moderate", "growth"} else 0.45
    horizon_match = 1.0 if candidate.horizon == horizon else 0.6
    liquidity_match = 1.0 if emergency_status == "yes" or candidate.liquidity == "high" else 0.7
    goal_match = 1.0 if goal == "wealth_creation" and candidate.asset_type in {"equity", "mutual_funds"} else 0.8
    data_quality = 1.0 if candidate.data_status == "available" else 0.5
    score = round(sum([risk_match * MATCH_WEIGHTS["risk"], horizon_match * MATCH_WEIGHTS["horizon"], liquidity_match * MATCH_WEIGHTS["liquidity"], goal_match * MATCH_WEIGHTS["goal"], 0.8 * MATCH_WEIGHTS["diversification"], data_quality * MATCH_WEIGHTS["data_quality"]]) * 100, 2)
    reasons = ["Matches the configured risk and horizon rules" if risk_match >= 0.7 else "Has a partial match with the configured risk rules", "Supports the stated goal under application rules", "Adds a distinct category to the candidate allocation"]
    if liquidity_match >= 1:
        reasons.append("Compatible with the stated liquidity context")
    if candidate.data_status != "available":
        reasons.append("Data quality is limited or cached")
    return score, reasons


def current_allocation(holdings: list[dict]) -> dict[str, float]:
    total = sum(float(item.get("value", 0)) for item in holdings)
    if total <= 0:
        return {}
    categories: dict[str, float] = {}
    for item in holdings:
        category = item.get("asset_type", "other")
        categories[category] = categories.get(category, 0) + float(item.get("value", 0)) / total * 100
    return {key: round(value, 4) for key, value in categories.items()}