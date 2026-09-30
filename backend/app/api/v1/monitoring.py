from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.alert_service import AlertService
from app.services.change_summary_service import ChangeSummaryService
from app.services.monitoring_service import MonitoringService
from app.services.reevaluation_service import ReevaluationService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

monitoring_service = MonitoringService()
alert_service = AlertService()
change_summary_service = ChangeSummaryService()
reevaluation_service = ReevaluationService()


@router.post("/run")
def run_monitoring(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required.")
    current = payload.get("current_snapshot")
    if current is None:
        current = payload.get("snapshot")
    if current is None:
        legacy_fields = {
            key: payload[key]
            for key in (
                "timestamp", "portfolio_value", "allocation", "risk_level", "goal_progress",
                "goal_gap", "monthly_contribution", "liquidity", "concentration",
                "market_metrics", "portfolio_drift", "data_status",
            )
            if key in payload
        }
        current = legacy_fields or None
    if not isinstance(current, dict):
        raise HTTPException(status_code=422, detail="A current_snapshot with timestamp and portfolio_value is required.")
    current = dict(current)
    snapshot_user_id = current.get("user_id")
    if snapshot_user_id and snapshot_user_id != user_id:
        raise HTTPException(status_code=400, detail="Snapshot user_id does not match the request.")
    current["user_id"] = user_id

    if "previous_snapshot" in payload:
        previous = payload["previous_snapshot"]
    else:
        previous = monitoring_service.get_latest_snapshot(user_id)
    if isinstance(previous, dict) and previous.get("user_id") not in (None, user_id):
        raise HTTPException(status_code=400, detail="Previous snapshot user_id does not match the request.")
    comparison_status = monitoring_service.comparison_status(previous, current)
    valid_current = monitoring_service.comparison_status(None, current) == "baseline_only"
    if comparison_status == "insufficient_previous_data" and valid_current:
        comparison_status = "baseline_replaced"

    events = monitoring_service.detect_changes(previous, current) if comparison_status == "compared" else []
    for event in events:
        alert_service.create_or_update_alert(
            user_id=event["user_id"],
            event_type=event["event_type"],
            severity=event.get("severity", "LOW"),
            details={
                "threshold": event.get("threshold"),
                "previous_value": event.get("previous_value"),
                "current_value": event.get("current_value"),
                "source": event.get("source", "monitoring"),
                "event_id": event.get("event_id"),
            },
        )
    snapshot_saved = valid_current
    if snapshot_saved:
        monitoring_service.snapshots.setdefault(user_id, []).append(current)
    return {
        "success": True,
        "timestamp": current.get("timestamp"),
        "data": current,
        "alerts": alert_service.list_alerts(user_id=user_id),
        "requires_review": any(event.get("severity") in {"MEDIUM", "HIGH", "CRITICAL"} for event in events),
        "events": events,
        "comparison_status": comparison_status,
        "snapshot_saved": snapshot_saved,
        "message": None if events else "Insufficient reliable data for comparison. No new alert generated." if comparison_status not in {"baseline_only", "baseline_replaced", "compared"} else None,
    }


@router.get("/status")
def monitoring_status() -> dict[str, Any]:
    return {"success": True, "status": "available", "mode": "manual", "requires_review": False}


@router.get("/events")
def list_events(user_id: str | None = None) -> dict[str, Any]:
    events = monitoring_service.events
    if user_id is not None:
        events = [event for event in events if event.get("user_id") == user_id]
    return {"success": True, "data": events}


@router.get("/events/{event_id}")
def get_event(event_id: str) -> dict[str, Any]:
    event = next((item for item in monitoring_service.events if item.get("event_id") == event_id), None)
    if event is None:
        raise HTTPException(status_code=404, detail="Monitoring event not found.")
    return {"success": True, "data": event}


@router.post("/events/{event_id}/read")
def mark_event_read(event_id: str) -> dict[str, Any]:
    alert = alert_service.get_alert(event_id)
    if alert is None:
        event = next((item for item in monitoring_service.events if item.get("event_id") == event_id), None)
        if event is None:
            raise HTTPException(status_code=404, detail="Monitoring event not found.")
        event["status"] = "READ"
        return {"success": True, "data": event}
    return {"success": True, "data": alert_service.mark_read(event_id)}


@router.post("/events/{event_id}/dismiss")
def dismiss_event(event_id: str) -> dict[str, Any]:
    alert = alert_service.dismiss(event_id)
    if alert is not None:
        return {"success": True, "data": alert}
    event = next((item for item in monitoring_service.events if item.get("event_id") == event_id), None)
    if event is not None:
        event["status"] = "DISMISSED"
        return {"success": True, "data": event}
    raise HTTPException(status_code=404, detail="Monitoring event not found.")


@router.post("/events/{event_id}/resolve")
def resolve_event(event_id: str) -> dict[str, Any]:
    alert = alert_service.resolve(event_id)
    if alert is not None:
        return {"success": True, "data": alert}
    event = next((item for item in monitoring_service.events if item.get("event_id") == event_id), None)
    if event is not None:
        event["status"] = "RESOLVED"
        return {"success": True, "data": event}
    raise HTTPException(status_code=404, detail="Monitoring event not found.")


@router.get("/changes")
def get_changes(user_id: str, previous_snapshot: dict[str, Any] | None = None, current_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshots = monitoring_service.get_snapshot_history(user_id)
    previous = previous_snapshot or (snapshots[-2] if len(snapshots) > 1 else None)
    current = current_snapshot or monitoring_service.get_latest_snapshot(user_id)
    if current is None:
        return {"success": True, "data": []}
    return {"success": True, "data": change_summary_service.summarize_changes(previous, current)}


@router.get("/snapshot/latest")
def latest_snapshot(user_id: str) -> dict[str, Any]:
    snapshot = monitoring_service.get_latest_snapshot(user_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No snapshot found for this user.")
    return {"success": True, "data": snapshot}


@router.get("/snapshot/history")
def history_snapshots(user_id: str) -> dict[str, Any]:
    return {"success": True, "data": monitoring_service.get_snapshot_history(user_id)}


@router.post("/reevaluate")
def reevaluate(payload: dict[str, Any]) -> dict[str, Any]:
    result = reevaluation_service.reevaluate_investment_twin(
        user_id=payload.get("user_id", "unknown"),
        trigger_event=payload.get("trigger_event", "PORTFOLIO_DRIFT"),
        previous_snapshot=payload.get("previous_snapshot"),
        current_snapshot=payload.get("current_snapshot"),
    )
    return {"success": True, "data": result}


@router.post("/check")
def check_monitoring(payload: dict[str, Any]) -> dict[str, Any]:
    return run_monitoring(payload)
