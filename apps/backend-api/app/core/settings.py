import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "JURIDICOTECH"
    app_version: str = "6.0.0"
    database_url: str = "sqlite+aiosqlite:///./legal.db"
    redis_url: str = "redis://localhost:6379/0"
    nats_url: str = "nats://localhost:4222"

    # JWT
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_256_BIT_SECRET"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


settings = Settings()
