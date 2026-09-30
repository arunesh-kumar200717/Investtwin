def risk_alerts(analysis: dict) -> list[dict]:
    alerts = []
    volatility = analysis.get("risk", {}).get("annualized_volatility")
    if volatility is not None and volatility > 0.25:
        alerts.append({"type": "volatility", "severity": "medium", "message": "Historical volatility is relatively high compared with the application threshold.", "metric": "annualized_volatility", "value": volatility})
    drawdown = analysis.get("risk", {}).get("maximum_drawdown_percent")
    if drawdown is not None and drawdown <= -20:
        alerts.append({"type": "drawdown", "severity": "medium", "message": "The asset has experienced a significant historical drawdown.", "metric": "maximum_drawdown_percent", "value": drawdown})
    volume = analysis.get("volume", {})
    if volume.get("change_percent") is not None and abs(volume["change_percent"]) > 50:
        alerts.append({"type": "volume", "severity": "low", "message": "Recent trading volume is significantly different from its recent average.", "metric": "volume_change_percent", "value": volume["change_percent"]})
    return alerts