from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    db_path: str = "./pulse.db"
    allow_cors_origins: str = "http://localhost:3000"

    groq_api_key: str = ""
    api_key: str = ""
    rate_limit_per_minute: int = 120

    cost_per_1k_input_tokens: float = 0.00015
    cost_per_1k_output_tokens: float = 0.0006
    latency_alert_ms: float = 5000
    error_rate_alert_pct: float = 10
    daily_cost_alert_usd: float = 1.0

    @property
    def cors_origins(self) -> list[str]:
        return [v.strip() for v in self.allow_cors_origins.split(",") if v.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
