from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.arbitration.router import router as arbitration_router
from app.arbitration.autonomous_arbitration import AutonomousArbitrationEngine
from app.auth.router import router as auth_router
from app.compliance.router import router as compliance_router
from app.collective_ai.legal_agi import FederatedLegalAGI
from app.collective_ai.legal_memory import EcosystemLegalMemory
from app.contracts.router import router as contract_router
from app.db.migrations import run_migrations_async
from app.db.session import init_models
from app.events.router import router as events_router
from app.federation.federation_runtime import FederationRuntime
from app.interplanetary.interplanetary_regulation import InterplanetaryRegulationRuntime
from app.legal_runtime.causal_runtime import CANONICAL_NATS_EVENTS, CausalLegalRuntime
from app.legal_runtime.legal_twin import LegalDigitalTwin
from app.legal_runtime.unified_identity import UnifiedLegalIdentity
from app.middleware.tenant import TenantMiddleware
from app.patents.patent_runtime import PatentIntelligenceRuntime
from app.routers.federation_runtime import router as federation_runtime_router
from app.replay.router import router as replay_router

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except Exception:
    FastAPIInstrumentor = None

from app.observability.tracing import tracer


federation_runtime = FederationRuntime()
interplanetary_runtime = InterplanetaryRegulationRuntime()
arbitration_engine = AutonomousArbitrationEngine()
federated_agi = FederatedLegalAGI()
ecosystem_memory = EcosystemLegalMemory()
causal_runtime = CausalLegalRuntime()
patent_runtime = PatentIntelligenceRuntime()
legal_twin = LegalDigitalTwin()
unified_identity = UnifiedLegalIdentity()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        await run_migrations_async()
    except Exception:
        await init_models()

    with tracer.start_as_current_span("runtime.startup"):
        federation_result = await federation_runtime.register()
        ecosystem_memory.store(
            {
                "event": "liceu.legal.runtime.started",
                "federation": federation_result,
            }
        )

    yield

app = FastAPI(title="JURIDICOTECH", version="6.0.0", lifespan=lifespan)
if FastAPIInstrumentor is not None:
    FastAPIInstrumentor.instrument_app(app)

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
app.include_router(federation_runtime_router)
app.include_router(events_router, prefix="/events", tags=["events"])
app.include_router(replay_router, prefix="/replay", tags=["replay"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/runtime/status")
async def runtime_status() -> dict[str, Any]:
    return {
        "monolith": "juridicotech",
        "runtime": "federated",
        "legal_ai": "enabled",
        "interplanetary_regulation": "active",
        "digital_twin": "online",
        "memory_items": len(ecosystem_memory.latest()),
    }


@app.post("/runtime/interplanetary")
async def runtime_interplanetary() -> dict[str, object]:
    result = interplanetary_runtime.evaluate("mars_mining")
    ecosystem_memory.store({"event": "liceu.legal.interplanetary.regulation", "result": result})
    return result


@app.post("/runtime/arbitration")
async def runtime_arbitration() -> dict[str, str]:
    result = arbitration_engine.arbitrate({"severity": 0.84})
    ecosystem_memory.store({"event": "liceu.legal.arbitration.executed", "result": result})
    return result


@app.post("/runtime/agi")
async def runtime_agi() -> dict[str, str]:
    result = federated_agi.deliberate()
    ecosystem_memory.store({"event": "liceu.legal.collective_ai.sync", "result": result})
    return result


@app.post("/runtime/patent")
async def runtime_patent() -> dict[str, float | bool]:
    result = patent_runtime.validate({"innovation_score": 0.92, "market_potential": 0.86})
    ecosystem_memory.store({"event": "liceu.legal.case.created", "result": result})
    return result


@app.post("/runtime/causal")
async def runtime_causal() -> dict[str, Any]:
    result = causal_runtime.analyze({"type": "unauthorized_patent_use"})
    ecosystem_memory.store({"event": "liceu.legal.ip.violation", "result": result})
    return result


@app.get("/runtime/digital-twin")
async def runtime_digital_twin() -> dict[str, float]:
    return legal_twin.simulate_global_risk()


@app.get("/runtime/identity")
async def runtime_identity() -> dict[str, Any]:
    return unified_identity.issue_identity(
        subject="john_legal_collective",
        roles=["federated_agi", "arbitration", "planetary_compliance"],
    )


@app.get("/runtime/events")
async def runtime_events() -> dict[str, list[str]]:
    return {"subjects": CANONICAL_NATS_EVENTS}


@app.get("/runtime/memory")
async def runtime_memory() -> dict[str, list[dict[str, Any]]]:
    return {"latest": ecosystem_memory.latest()}
