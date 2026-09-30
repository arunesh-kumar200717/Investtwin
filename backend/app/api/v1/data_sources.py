from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings
from app.data.market_models import DataSourcesStatus
from app.data.registry import data_sources_status

router = APIRouter(prefix="/data-sources", tags=["market-data"])


@router.get("/status", response_model=DataSourcesStatus)
def sources_status(settings: Settings = Depends(get_settings)) -> DataSourcesStatus:
    return data_sources_status(settings)