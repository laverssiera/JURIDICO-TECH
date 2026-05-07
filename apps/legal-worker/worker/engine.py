from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from worker.config import settings

logger = logging.getLogger("legal-worker.engine")

# ── shared stats (in-memory for /worker/status) ──────────────────────────────
_stats: dict = {
    "cycles": 0,
    "published_total": 0,
    "dead_total": 0,
    "last_cycle_at": None,
    "last_cycle_published": 0,
    "last_cycle_pending": 0,
}


def get_stats() -> dict:
    return dict(_stats)


# ── DB session (reuses DATABASE_URL from backend-api via env) ─────────────────
def _make_session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(settings.database_url, echo=False)
    return async_sessionmaker(engine, expire_on_commit=False)


# ── NATS publish (optional — graceful fallback) ───────────────────────────────
async def _nats_publish(subject: str, payload: str) -> bool:
    try:
        import nats  # type: ignore

        nc = await nats.connect(settings.nats_url)
        js = nc.jetstream()
        await js.publish(subject, payload.encode())
        await nc.drain()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("NATS publish failed: %s", exc)
        return False


# ── WorkerEngine ──────────────────────────────────────────────────────────────
class WorkerEngine:
    """Polls legal_event_outbox table and publishes pending events to NATS."""

    def __init__(self) -> None:
        self._session_factory = _make_session_factory()

    async def run(self) -> None:
        while True:
            try:
                await self._cycle()
            except Exception as exc:  # noqa: BLE001
                logger.error("Worker cycle error: %s", exc)
            await asyncio.sleep(settings.poll_interval)

    async def _cycle(self) -> None:
        async with self._session_factory() as session:
            from sqlalchemy import select  # local import to keep module light

            # Import the shared model from backend-api DB — we connect to same DB
            # so we declare a minimal inline table mapping here to avoid coupling.
            from worker.outbox_model import OutboxRow

            result = await session.execute(
                select(OutboxRow)
                .where(OutboxRow.status.in_(["pending", "retry"]))
                .order_by(OutboxRow.created_at)
                .limit(settings.batch_size)
            )
            rows = result.scalars().all()

            published = 0
            dead = 0

            for row in rows:
                # Exponential backoff: skip if not yet ready for retry
                if row.attempts > 0 and row.last_error:
                    created_at = row.created_at
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=UTC)
                    delay = settings.backoff_base ** row.attempts
                    ready_at = created_at + timedelta(seconds=delay)
                    if datetime.now(UTC) < ready_at:
                        continue

                ok = await _nats_publish(row.subject, row.payload_json)

                if ok:
                    row.status = "published"
                    row.published_at = datetime.now(UTC)
                    published += 1
                else:
                    row.attempts = (row.attempts or 0) + 1
                    row.last_error = "nats_unavailable"
                    if row.attempts >= settings.max_attempts:
                        row.status = "dead"
                        dead += 1
                        logger.warning("Event %s moved to DLQ after %s attempts", row.id, row.attempts)
                    else:
                        row.status = "retry"

                session.add(row)

            await session.commit()

            pending_left = len(rows) - published - dead
            _stats["cycles"] += 1
            _stats["published_total"] += published
            _stats["dead_total"] += dead
            _stats["last_cycle_at"] = datetime.now(UTC).isoformat()
            _stats["last_cycle_published"] = published
            _stats["last_cycle_pending"] = pending_left

            if rows:
                logger.info(
                    "Cycle #%s — scanned=%s published=%s dead=%s pending=%s",
                    _stats["cycles"],
                    len(rows),
                    published,
                    dead,
                    pending_left,
                )
