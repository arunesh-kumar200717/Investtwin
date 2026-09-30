import numpy as np
import pandas as pd


def historical_volatility(frame: pd.DataFrame) -> dict:
    returns = frame["close"].pct_change().dropna()
    if returns.empty:
        return {"daily_volatility": None, "annualized_volatility": None, "status": "unavailable", "message": "Insufficient returns for volatility"}
    daily = float(returns.std(ddof=1))
    return {"daily_volatility": round(daily, 6), "annualized_volatility": round(float(daily * np.sqrt(252)), 6), "status": "available"}