"""Application-defined matching rules, intentionally easy to tune."""

RISK_ALLOCATIONS = {
    "conservative": {"equity": 20, "mutual_funds": 45, "gold": 10, "cash": 25},
    "moderate": {"equity": 35, "mutual_funds": 40, "gold": 10, "cash": 15},
    "growth": {"equity": 50, "mutual_funds": 35, "gold": 10, "cash": 5},
    "aggressive": {"equity": 65, "mutual_funds": 25, "gold": 5, "cash": 5},
}

MATCH_WEIGHTS = {"risk": 0.30, "horizon": 0.20, "liquidity": 0.15, "goal": 0.15, "diversification": 0.10, "data_quality": 0.10}
HORIZON_LABELS = {"less_than_1": "short_term", "one_to_three": "short_term", "three_to_five": "medium_term", "five_to_ten": "long_term", "more_than_10": "long_term"}


def normalize_allocations(allocations: dict[str, float]) -> dict[str, float]:
    total = sum(allocations.values())
    if total <= 0:
        return {"cash": 100.0}
    normalized = {key: round(value / total * 100, 4) for key, value in allocations.items() if value > 0}
    largest = max(normalized)
    normalized[largest] = round(normalized[largest] + 100 - sum(normalized.values()), 4)
    return normalized


def target_allocation(risk_profile: str, horizon: str, goal: str, available: set[str]) -> dict[str, float]:
    allocations = dict(RISK_ALLOCATIONS.get(risk_profile.lower(), RISK_ALLOCATIONS["moderate"]))
    horizon_class = HORIZON_LABELS.get(horizon, "medium_term")
    if horizon_class == "short_term":
        allocations["equity"] -= 10
        allocations["cash"] += 10
    elif horizon_class == "long_term":
        allocations["equity"] += 10
        allocations["cash"] -= 10
    if goal == "emergency_fund":
        allocations["cash"] += 20
        allocations["equity"] -= 15
        allocations["gold"] -= 5
    for category in list(allocations):
        if category not in available:
            replacement = "cash" if "cash" in available else next(iter(available), "cash")
            allocations[replacement] = allocations.get(replacement, 0) + allocations[category]
            allocations[category] = 0
    return normalize_allocations(allocations)