"""Tests for legal-worker engine (offline — NATS fallback, SQLite outbox)."""
from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from worker.outbox_model import OutboxRow, _Base

# ── fixtures ──────────────────────────────────────────────────────────────────
TEST_DB = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture()
async def db_session():
    engine = create_async_engine(TEST_DB, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(_Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("WORKER_DATABASE_URL", TEST_DB)
    from worker.main import app as _app
    return _app


# ── tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_worker_status_zero(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/worker/status")
    assert r.status_code == 200
    data = r.json()
    assert "cycles" in data
    assert data["published_total"] == 0


@pytest.mark.asyncio
async def test_engine_cycle_marks_retry_then_dead(monkeypatch):
    """Engine marks events as retry when NATS is unavailable, then dead after max_attempts."""
    import worker.engine as eng_mod
    from worker.config import settings

    # build isolated in-memory DB
    async_engine = create_async_engine(TEST_DB, echo=False)
    async with async_engine.begin() as conn:
        await conn.run_sync(_Base.metadata.create_all)
    factory = async_sessionmaker(async_engine, expire_on_commit=False)

    # seed one pending event
    async with factory() as session:
        row = OutboxRow(subject="legal.contracts.created", payload_json='{"id":1}', status="pending", attempts=0)
        session.add(row)
        await session.commit()
        row_id = row.id

    monkeypatch.setattr(eng_mod, "_make_session_factory", lambda: factory)
    monkeypatch.setattr(settings, "max_attempts", 2, raising=False)
    monkeypatch.setattr(settings, "backoff_base", 0.0, raising=False)

    from worker.engine import WorkerEngine
    from sqlalchemy import select

    engine = WorkerEngine()
    engine._session_factory = factory

    # cycle 1 — NATS down → retry
    await engine._cycle()
    async with factory() as s:
        r = await s.get(OutboxRow, row_id)
        assert r.status == "retry"
        assert r.attempts == 1

    # cycle 2 — NATS still down → dead (max_attempts=2)
    await engine._cycle()
    async with factory() as s:
        r = await s.get(OutboxRow, row_id)
        assert r.status == "dead"
        assert r.attempts == 2
