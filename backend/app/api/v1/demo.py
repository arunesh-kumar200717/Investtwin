from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient

from app.api.v1.monitoring import alert_service, monitoring_service
from app.config.settings import Settings, get_settings

router = APIRouter(prefix="/demo", tags=["demo"])
DEMO_USER_ID = "demo-investor"
DEMO_COLLECTIONS = ("user_profiles", "investment_transactions", "stress_tests")


@router.post("/reset")
def reset_demo(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    if not settings.demo_mode:
        raise HTTPException(status_code=404, detail="Demo reset is not enabled.")

    deleted = {collection: 0 for collection in DEMO_COLLECTIONS}
    if settings.database_url:
        client = None
        try:
            client = MongoClient(settings.database_url, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
            database = client[settings.database_name]
            for collection_name in DEMO_COLLECTIONS:
                deleted[collection_name] = database[collection_name].delete_many({"user_id": DEMO_USER_ID}).deleted_count
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Demo data storage is temporarily unavailable.") from exc
        finally:
            if client is not None:
                client.close()

    monitoring_service.snapshots.pop(DEMO_USER_ID, None)
    monitoring_service.events = [event for event in monitoring_service.events if event.get("user_id") != DEMO_USER_ID]
    alert_service.alerts = {
        fingerprint: alert
        for fingerprint, alert in alert_service.alerts.items()
        if alert.get("user_id") != DEMO_USER_ID
    }

    return {"success": True, "user_id": DEMO_USER_ID, "deleted_records": deleted}
