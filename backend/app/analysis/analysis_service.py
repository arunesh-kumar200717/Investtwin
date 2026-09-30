from datetime import datetime, timezone

import pandas as pd

from app.analysis.alerts import risk_alerts
from app.analysis.drawdown import add_drawdown, maximum_drawdown
from app.analysis.momentum import add_rsi, momentum_summary
from app.analysis.moving_average import add_moving_averages, trend_structure
from app.analysis.returns import add_daily_returns, period_returns
from app.analysis.volatility import historical_volatility
from app.analysis.volume import volume_summary


def bars_to_frame(bars: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(bars)
    if frame.empty:
        return frame
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date", "close"]).sort_values("date").drop_duplicates("date").reset_index(drop=True)
    for column in ["open", "high", "low", "close", "volume"]:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["close"])


def analyze_history(symbol: str, bars: list[dict], source: str, data_timestamp: str | None = None) -> dict:
    frame = bars_to_frame(bars)
    if frame.empty:
        return {"symbol": symbol, "source": source, "data_status": "unavailable", "message": "Historical data is not available for this instrument."}
    frame = add_daily_returns(frame)
    frame = add_moving_averages(frame)
    frame = add_drawdown(frame)
    frame = add_rsi(frame)
    latest = frame.iloc[-1]
    price_change = float(latest["close"] - frame["close"].iloc[-2]) if len(frame) > 1 else None
    price_change_percent = float(price_change / frame["close"].iloc[-2] * 100) if price_change is not None else None
    response = {"symbol": symbol, "source": source, "data_status": "available", "data_timestamp": data_timestamp or frame["date"].iloc[-1].date().isoformat(), "analysis_timestamp": datetime.now(timezone.utc).isoformat(), "price": {"current": float(latest["close"]), "change": price_change, "change_percent": price_change_percent}, "returns": period_returns(frame), "moving_averages": {name: float(latest[column]) if pd.notna(latest[column]) else None for name, column in [("MA20", "ma20"), ("MA50", "ma50"), ("MA200", "ma200")]}, "trend_structure": trend_structure(frame), "risk": {**historical_volatility(frame), **maximum_drawdown(frame)}, "momentum": momentum_summary(frame), "volume": volume_summary(frame)}
    response["alerts"] = risk_alerts(response)
    return response


def chart_history(symbol: str, bars: list[dict]) -> dict:
    frame = add_rsi(add_drawdown(add_moving_averages(add_daily_returns(bars_to_frame(bars)))))
    if frame.empty:
        return {"symbol": symbol, "data_status": "unavailable", "data": []}
    columns = ["date", "open", "high", "low", "close", "volume", "daily_return", "ma20", "ma50", "ma200", "drawdown", "rsi"]
    records = []
    for row in frame[columns].itertuples(index=False):
        records.append({key: (value.date().isoformat() if key == "date" else None if pd.isna(value) else float(value)) for key, value in zip(columns, row)})
    return {"symbol": symbol, "data_status": "available", "data": records}