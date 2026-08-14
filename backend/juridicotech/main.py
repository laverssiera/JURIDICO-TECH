from __future__ import annotations

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from juridicotech.core.db import init_schema
from juridicotech.integrations.nats import nats_bus
from juridicotech.modules.bypass import router as bypass_router
from juridicotech.modules.contracts import router as contract_router
from juridicotech.modules.events import router as events_router
from juridicotech.modules.risk import router as risk_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("JURIDICO_INIT_SCHEMA", "0") == "1":
        init_schema()

    nats_url = os.getenv("NATS_URL")
    if nats_url:
        await nats_bus.connect(nats_url)

    try:
        yield
    finally:
        if nats_url:
            await nats_bus.close()


app = FastAPI(title="JuridicoTech Core", lifespan=lifespan)

app.include_router(contract_router, prefix="/contracts", tags=["contracts"])
app.include_router(risk_router, prefix="/risk", tags=["risk"])
app.include_router(bypass_router, prefix="/bypass", tags=["bypass"])
app.include_router(events_router, prefix="/events", tags=["events"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
