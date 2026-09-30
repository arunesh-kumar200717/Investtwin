from typing import Any

from fastapi import APIRouter, Depends
from pymongo import MongoClient

from app.ai.service import AIService
from app.config.settings import Settings, get_settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status")
def system_status(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    ai_status = AIService().status()
    ai_status.update({"enabled": settings.ai_enabled, "live_probe": "not_performed"})
    return {
        "backend": {"status": "available"},
        "database": database_status(settings),
        "market_data": market_data_status(settings),
        "ai": ai_status,
        "monitoring": {"status": "available", "storage": "process-memory", "persistent": False},
        "demo_mode": {"enabled": settings.demo_mode},
    }


def database_status(settings: Settings) -> dict[str, Any]:
    if not settings.database_url:
        return {"status": "unavailable", "configured": False, "message": "DATABASE_URL is not configured."}
    client = None
    try:
        client = MongoClient(settings.database_url, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000)
        client.admin.command("ping")
        return {"status": "available", "configured": True}
    except Exception:
        return {"status": "unavailable", "configured": True, "message": "Database connection is unavailable."}
    finally:
        if client is not None:
            client.close()


def market_data_status(settings: Settings) -> dict[str, Any]:
    stock_configured = bool(settings.stock_api_key and settings.stock_api_base_url)
    return {
        "status": "configured",
        "live_probe": "not_performed",
        "providers": {
            "stocks": "configured" if stock_configured else "unavailable",
            "mutual_funds": "configured",
            "gold": "unavailable",
            "nps": "unavailable",
            "bonds": "unavailable",
            "fd": "unavailable",
            "ppf": "unavailable",
        },
    }
