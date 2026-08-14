from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WORKER_", env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./legal_worker.db"
    nats_url: str = "nats://localhost:4222"
    poll_interval: float = 5.0       # seconds between polls
    max_attempts: int = 5            # after this many failures → dead letter
    backoff_base: float = 2.0        # exponential backoff base (seconds)
    batch_size: int = 50             # max events per flush cycle


settings = Settings()
