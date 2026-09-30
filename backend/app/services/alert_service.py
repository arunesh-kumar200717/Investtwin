from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


class AlertService:
    def __init__(self) -> None:
        self.alerts: dict[str, dict[str, Any]] = {}

    def create_or_update_alert(self, user_id: str, event_type: str, severity: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        details = details or {}
        fingerprint = self._fingerprint(user_id, event_type, details)
        now = datetime.now(timezone.utc).isoformat()
        if fingerprint in self.alerts:
            alert = self.alerts[fingerprint]
            alert["current_value"] = details.get("current_value", alert.get("current_value"))
            alert["previous_value"] = details.get("previous_value", alert.get("previous_value"))
            alert["last_detected_at"] = now
            alert["occurrence_count"] = int(alert.get("occurrence_count", 1)) + 1
            alert["status"] = "ACTIVE"
            alert["severity"] = severity
            alert["details"] = details
            return dict(alert)

        alert = {
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "event_type": event_type,
            "severity": severity,
            "status": "UNREAD",
            "detected_at": now,
            "last_detected_at": now,
            "current_value": details.get("current_value"),
            "previous_value": details.get("previous_value"),
            "threshold": details.get("threshold"),
            "source": details.get("source", "monitoring"),
            "details": details,
            "occurrence_count": 1,
        }
        self.alerts[fingerprint] = alert
        return dict(alert)

    def list_alerts(self, user_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        alerts = list(self.alerts.values())
        if user_id is not None:
            alerts = [alert for alert in alerts if alert["user_id"] == user_id]
        if status is not None:
            alerts = [alert for alert in alerts if alert["status"] == status]
        return sorted(alerts, key=lambda item: item.get("last_detected_at", ""), reverse=True)

    def get_alert(self, event_id: str) -> dict[str, Any] | None:
        for alert in self.alerts.values():
            if alert["event_id"] == event_id:
                return alert
        return None

    def mark_read(self, event_id: str) -> dict[str, Any] | None:
        alert = self.get_alert(event_id)
        if alert is None:
            return None
        alert["status"] = "READ"
        return alert

    def dismiss(self, event_id: str) -> dict[str, Any] | None:
        alert = self.get_alert(event_id)
        if alert is None:
            return None
        alert["status"] = "DISMISSED"
        return alert

    def resolve(self, event_id: str) -> dict[str, Any] | None:
        alert = self.get_alert(event_id)
        if alert is None:
            return None
        alert["status"] = "RESOLVED"
        return alert

    def _fingerprint(self, user_id: str, event_type: str, details: dict[str, Any]) -> str:
        return f"{user_id}:{event_type}:{details.get('asset_id') or details.get('source') or 'global'}:{details.get('threshold') or 'default'}"
