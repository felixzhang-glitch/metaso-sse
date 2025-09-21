from __future__ import annotations

from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="METASO_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str = Field(..., description="Metaso API Bearer token")
    base_url: HttpUrl = Field(
        "https://metaso.cn",
        description="Root URL for the Metaso API",
    )
    request_timeout: float = Field(
        15.0,
        description="Client timeout (seconds) for outbound requests",
        gt=0,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
