import pandas as pd


def add_moving_averages(frame: pd.DataFrame, windows: tuple[int, ...] = (20, 50, 200)) -> pd.DataFrame:
    result = frame.copy()
    for window in windows:
        result[f"ma{window}"] = result["close"].rolling(window=window, min_periods=window).mean()
    return result


def trend_structure(frame: pd.DataFrame) -> str:
    latest = frame.iloc[-1]
    if pd.notna(latest.get("ma20")) and pd.notna(latest.get("ma50")):
        if latest["close"] > latest["ma20"] > latest["ma50"]:
            return "upward"
        if latest["close"] < latest["ma20"] < latest["ma50"]:
            return "downward"
    return "mixed"