from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수(.env) 기반 애플리케이션 설정."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "faith-memory-backend"
    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = []

    # Database (PostgreSQL + pgvector)
    database_url: str = "postgresql+asyncpg://faith:faith@localhost:5432/faith_memory"
    db_echo: bool = False  # True면 SQL 파라미터(일기 원문 포함)가 로그에 남으므로 로컬에서만 사용
    db_pool_size: int = 5
    db_max_overflow: int = 5

    # AI (제공자 미정 — IR 6.3)
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_api_key: SecretStr | None = None
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 2
    embedding_model: str | None = None
    embedding_dimensions: int = 1536
    reflection_top_k: int = 5  # SR-04: 회고에 사용할 상위 K개 기록

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
