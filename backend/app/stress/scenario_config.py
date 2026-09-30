SCENARIOS = {
    "market_shock": {
        "mild": {"equity_change_percent": -10, "mutual_funds_change_percent": -5, "debt_change_percent": -3, "gold_change_percent": 0, "cash_change_percent": 0},
        "moderate": {"equity_change_percent": -20, "mutual_funds_change_percent": -8, "debt_change_percent": -5, "gold_change_percent": 2, "cash_change_percent": 0},
        "severe": {"equity_change_percent": -35, "mutual_funds_change_percent": -18, "debt_change_percent": -10, "gold_change_percent": 5, "cash_change_percent": 0},
    },
    "asset_shock": {"mild": -10, "moderate": -20, "severe": -40},
    "concentration_shock": {"mild": -10, "moderate": -25, "severe": -40},
    "income_reduction": {"mild": -10, "moderate": -25, "severe": -40},
    "contribution_reduction": {"mild": -20, "moderate": -40, "severe": -70},
    "emergency_expense": {"mild": 10000, "moderate": 50000, "severe": 100000},
    "goal_deadline_change": {"mild": -3, "moderate": -6, "severe": -12},
    "combined": {
        "mild": {"equity_change_percent": -10, "mutual_funds_change_percent": -5, "debt_change_percent": -3, "gold_change_percent": 2, "cash_change_percent": 0, "income_change_percent": -10, "contribution_change_percent": -20, "emergency_expense": 25000, "goal_deadline_change_months": -3},
        "moderate": {"equity_change_percent": -20, "mutual_funds_change_percent": -8, "debt_change_percent": -5, "gold_change_percent": 2, "cash_change_percent": 0, "income_change_percent": -25, "contribution_change_percent": -30, "emergency_expense": 50000, "goal_deadline_change_months": -6},
        "severe": {"equity_change_percent": -35, "mutual_funds_change_percent": -18, "debt_change_percent": -10, "gold_change_percent": 5, "cash_change_percent": 0, "income_change_percent": -40, "contribution_change_percent": -50, "emergency_expense": 100000, "goal_deadline_change_months": -12},
    },
}
