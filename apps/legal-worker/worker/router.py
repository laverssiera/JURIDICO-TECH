from __future__ import annotations

from fastapi import APIRouter

from worker.engine import get_stats

router = APIRouter()


@router.get("/status")
async def worker_status() -> dict:
    """Operational metrics for the outbox poller."""
    return get_stats()


@router.post("/flush", summary="Trigger an immediate flush cycle (manual)")
async def worker_flush() -> dict:
    """Manually trigger one flush cycle outside the poll interval."""
    from worker.engine import WorkerEngine

    engine = WorkerEngine()
    await engine._cycle()
    return {"triggered": True, "stats": get_stats()}
