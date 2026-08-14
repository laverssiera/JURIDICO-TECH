"""Legal Worker — JURIDICOTECH LICEU 6.0
Polls the transactional outbox and publishes pending events to NATS JetStream.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from worker.config import settings
from worker.engine import WorkerEngine
from worker.router import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("legal-worker")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    engine = WorkerEngine()
    task = asyncio.create_task(engine.run(), name="outbox-poller")
    logger.info("Outbox poller started (interval=%ss, max_attempts=%s)", settings.poll_interval, settings.max_attempts)
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Outbox poller stopped")


app = FastAPI(
    title="JURIDICOTECH Legal Worker",
    version="6.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/worker", tags=["worker"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "legal-worker"}
