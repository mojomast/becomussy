"""
becomussy – application configuration.

Uses pydantic-settings to load from environment / .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings, populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://becoming:becoming@db:5432/becoming"
    SYNC_DATABASE_URL: str = "postgresql://becoming:becoming@db:5432/becoming"

    # ── Redis ───────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── Security ────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"

    # ── Environment ─────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── App metadata ────────────────────────────────────────────────────
    APP_NAME: str = "becomussy"
    API_V1_PREFIX: str = "/api/v1"


# Singleton – import this wherever you need settings.
settings = Settings()
