from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.market import router as market_router
from app.api.v1.data_sources import router as data_sources_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.profile import router as profile_router
from app.api.v1.history import router as history_router
from app.api.v1.stress import router as stress_router
from app.api.v1.ai import router as ai_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.demo import router as demo_router
from app.api.v1.system import router as system_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(health_router, prefix="/v1")
api_router.include_router(profile_router, prefix="/v1")
api_router.include_router(history_router, prefix="/v1")
api_router.include_router(stress_router, prefix="/v1")
api_router.include_router(market_router, prefix="/v1")
api_router.include_router(data_sources_router, prefix="/v1")
api_router.include_router(analysis_router, prefix="/v1")
api_router.include_router(portfolio_router, prefix="/v1")
api_router.include_router(ai_router, prefix="/v1")
api_router.include_router(monitoring_router, prefix="/v1")
api_router.include_router(demo_router, prefix="/v1")
api_router.include_router(system_router, prefix="/v1")