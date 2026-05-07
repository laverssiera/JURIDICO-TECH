from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.arbitration.router import router as arbitration_router
from app.auth.router import router as auth_router
from app.compliance.router import router as compliance_router
from app.contracts.router import router as contract_router
from app.db.migrations import run_migrations_async
from app.db.session import init_models
from app.events.router import router as events_router
from app.middleware.tenant import TenantMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        await run_migrations_async()
    except Exception:
        await init_models()
    yield

app = FastAPI(title="JURIDICOTECH", version="6.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(contract_router, prefix="/contracts", tags=["contracts"])
app.include_router(arbitration_router, prefix="/arbitration", tags=["arbitration"])
app.include_router(compliance_router, prefix="/compliance", tags=["compliance"])
app.include_router(events_router, prefix="/events", tags=["events"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
