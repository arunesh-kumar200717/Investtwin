from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    database_url: str | None = None
    database_name: str = "investtwin"
    market_data_api_key: str | None = None
    llm_api_key: str | None = None
    ai_api_key: str | None = None
    ai_provider: str = "fallback"
    ai_base_url: str | None = None
    ai_model: str | None = None
    ai_enabled: bool = True
    stock_api_key: str | None = None
    stock_api_base_url: str = "https://www.alphavantage.co/query"
    stock_cache_ttl_seconds: int = 900
    mutual_fund_cache_ttl_seconds: int = 3600
    external_request_timeout_seconds: float = 10.0
    monitoring_snapshot_max_age_seconds: int = 86400
    frontend_origin: str = "http://localhost:5173"
    demo_mode: bool = False
    backend_host: str = "127.0.0.1"
    backend_port: int = 8001
    monitoring_thresholds: dict[str, float] = {
        "portfolio_value_change_percent": 5.0,
        "allocation_drift_percentage_points": 5.0,
        "concentration_percentage": 25.0,
        "volatility_change_percent": 20.0,
        "drawdown_percentage": 10.0,
        "goal_gap_change_percent": 5.0,
        "goal_deadline_warning_days": 180.0,
    }

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", PROJECT_ROOT / "backend" / ".env"),
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()