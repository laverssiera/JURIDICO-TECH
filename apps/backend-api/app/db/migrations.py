import asyncio
import os
from pathlib import Path


def _to_sync_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite://"):
        return database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return database_url


def run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    root = Path(__file__).resolve().parents[2]
    cfg = Config(str(root / "alembic.ini"))

    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./juridicotech.db")
    cfg.set_main_option("sqlalchemy.url", _to_sync_database_url(database_url))

    command.upgrade(cfg, "head")


async def run_migrations_async() -> None:
    await asyncio.to_thread(run_migrations)
