import pandas as pd


def volume_summary(frame: pd.DataFrame) -> dict:
    if "volume" not in frame or frame["volume"].dropna().empty:
        return {"status": "unavailable", "message": "Volume is not available from the provider"}
    volumes = frame["volume"].dropna()
    current = float(volumes.iloc[-1])
    average_20d = float(volumes.tail(20).mean()) if len(volumes) >= 20 else None
    change = ((current / average_20d) - 1) * 100 if average_20d else None
    return {"current": current, "average_20d": average_20d, "change_percent": round(change, 4) if change is not None else None, "status": "available" if average_20d else "unavailable", "message": None if average_20d else "Insufficient observations for a 20-day volume average"}