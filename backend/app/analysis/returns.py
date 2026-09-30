from datetime import timedelta

import pandas as pd


def add_daily_returns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["daily_return"] = result["close"].pct_change()
    return result


def period_returns(frame: pd.DataFrame, periods: dict[str, int] | None = None) -> dict[str, dict]:
    periods = periods or {"1D": 1, "7D": 7, "30D": 30, "90D": 90, "1Y": 365}
    if frame.empty:
        return {name: unavailable("No historical observations") for name in periods}
    latest_date = frame["date"].iloc[-1]
    latest_close = float(frame["close"].iloc[-1])
    results = {}
    for name, days in periods.items():
        target_date = latest_date - timedelta(days=days)
        prior = frame[frame["date"] <= target_date]
        if prior.empty:
            results[name] = unavailable(f"Insufficient history for {name}")
            continue
        previous_close = float(prior["close"].iloc[-1])
        results[name] = {"period": name, "return_percent": round((latest_close / previous_close - 1) * 100, 4), "status": "available"}
    return results


def unavailable(message: str) -> dict:
    return {"period": None, "return_percent": None, "status": "unavailable", "message": message}