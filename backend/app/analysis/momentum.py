import pandas as pd


def add_rsi(frame: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    result = frame.copy()
    change = result["close"].diff()
    gain = change.clip(lower=0).ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    loss = (-change.clip(upper=0)).ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    result["rsi"] = 100 - (100 / (1 + gain / loss.replace(0, pd.NA)))
    return result


def momentum_summary(frame: pd.DataFrame) -> dict:
    value = frame["rsi"].dropna()
    if value.empty:
        return {"rsi": None, "range": None, "status": "unavailable", "message": "Insufficient observations for RSI"}
    rsi = float(value.iloc[-1])
    state = "historically low momentum range" if rsi < 30 else "historically high momentum range" if rsi > 70 else "neutral range"
    return {"rsi": round(rsi, 4), "range": state, "status": "available"}