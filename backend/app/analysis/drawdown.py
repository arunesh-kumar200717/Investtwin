import pandas as pd


def maximum_drawdown(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"maximum_drawdown_percent": None, "status": "unavailable", "message": "No historical observations"}
    running_peak = frame["close"].cummax()
    drawdowns = frame["close"] / running_peak - 1
    trough_index = drawdowns.idxmin()
    trough_value = float(drawdowns.loc[trough_index])
    peak_slice = frame.loc[:trough_index]
    peak_index = peak_slice["close"].idxmax()
    return {"maximum_drawdown_percent": round(trough_value * 100, 4), "peak_date": frame.loc[peak_index, "date"].date().isoformat(), "trough_date": frame.loc[trough_index, "date"].date().isoformat(), "status": "available"}


def add_drawdown(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["drawdown"] = result["close"] / result["close"].cummax() - 1
    return result