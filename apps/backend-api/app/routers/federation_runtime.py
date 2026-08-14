from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.federation.arbitration.runtime import PlanetaryArbitrationRuntime
from app.federation.authority.runtime import FederationAuthority
from app.federation.compliance.runtime import SovereignCompliance
from app.federation.config import settings
from app.federation.digital_twin.legal_twin import LegalDigitalTwin
from app.federation.graph.legal_graph import LegalKnowledgeGraph
from app.federation.hooks.john_brasileiro import JohnBrasileiroHooks
from app.federation.interplanetary.space_law_runtime import SpaceLawRuntime
from app.federation.legal_runtime.ip_runtime import IntellectualPropertyRuntime
from app.federation.memory.runtime_memory import LegalMemory
from app.federation.observability.tracing import UnifiedObservability
from app.federation.sovereign.runtime import SovereignRuntime
from app.federation.telemetry.runtime import TelemetryRuntime
from app.federation.warroom.runtime import LegalWarRoom


class TreatyRegistration(BaseModel):
    treaty_name: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=1)
    legal_scope: str = Field(min_length=1)


class MemoryRecord(BaseModel):
    payload: dict[str, Any]


class HookAnnotation(BaseModel):
    payload: dict[str, Any]


router = APIRouter(prefix="/federation/legal", tags=["Federation Legal Runtime"])

_authority = FederationAuthority()
_space_law = SpaceLawRuntime()
_ip_runtime = IntellectualPropertyRuntime()
_arbitration = PlanetaryArbitrationRuntime()
_digital_twin = LegalDigitalTwin()
_compliance = SovereignCompliance()
_war_room = LegalWarRoom()
_john_hooks = JohnBrasileiroHooks()
_sovereign_runtime = SovereignRuntime()
_telemetry_runtime = TelemetryRuntime()


@router.get("/summary")
async def federation_summary() -> dict[str, Any]:
    memory_snapshot = LegalMemory.snapshot()
    graph_snapshot = LegalKnowledgeGraph.snapshot()
    observability_snapshot = _telemetry_runtime.snapshot()

    return {
        "authority": _authority.snapshot(),
        "sovereign": _sovereign_runtime.status(),
        "telemetry": observability_snapshot,
        "memory": memory_snapshot,
        "graph": graph_snapshot,
        "diagnostics": {
            "configured": {
                "memory": settings.FEDERATION_MEMORY_BACKEND,
                "graph": settings.FEDERATION_GRAPH_BACKEND,
                "observability": settings.FEDERATION_OBSERVABILITY_BACKEND,
            },
            "effective": {
                "memory": memory_snapshot.get("backend", "unknown"),
                "graph": graph_snapshot.get("backend", "unknown"),
                "observability": observability_snapshot.get("backend", "unknown"),
            },
        },
        "john_hooks": _john_hooks.profile(),
        "space_law": _space_law.evaluate(),
        "ip": _ip_runtime.strategic_assets(),
        "arbitration": _arbitration.arbitration_status(),
        "digital_twin": _digital_twin.simulate_global_legal_risk(),
        "compliance": _compliance.evaluate(),
        "war_room": _war_room.status(),
    }


@router.get("/space-law")
async def space_law() -> dict[str, Any]:
    return _space_law.evaluate()


@router.get("/ip")
async def ip_runtime() -> dict[str, Any]:
    return _ip_runtime.strategic_assets()


@router.get("/arbitration")
async def arbitration_runtime() -> dict[str, Any]:
    return _arbitration.arbitration_status()


@router.get("/digital-twin")
async def legal_twin() -> dict[str, Any]:
    return _digital_twin.simulate_global_legal_risk()


@router.get("/compliance")
async def compliance() -> dict[str, Any]:
    return _compliance.evaluate()


@router.get("/war-room")
async def war_room() -> dict[str, Any]:
    return _war_room.status()


@router.get("/observability")
async def observability() -> dict[str, Any]:
    UnifiedObservability.record("federation", status="ok")
    return UnifiedObservability.snapshot()


@router.get("/diagnostics/backends")
async def diagnostics_backends() -> dict[str, Any]:
    memory_snapshot = LegalMemory.snapshot()
    graph_snapshot = LegalKnowledgeGraph.snapshot()
    observability_snapshot = _telemetry_runtime.snapshot()

    return {
        "configured": {
            "memory": settings.FEDERATION_MEMORY_BACKEND,
            "graph": settings.FEDERATION_GRAPH_BACKEND,
            "observability": settings.FEDERATION_OBSERVABILITY_BACKEND,
        },
        "effective": {
            "memory": memory_snapshot.get("backend", "unknown"),
            "graph": graph_snapshot.get("backend", "unknown"),
            "observability": observability_snapshot.get("backend", "unknown"),
        },
        "connection": {
            "authority_connected": _authority.snapshot().get("connected", False),
            "nats_url": settings.NATS_URL,
            "redis": {
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
            },
            "neo4j": {
                "uri": settings.NEO4J_URI,
                "user": settings.NEO4J_USER,
            },
            "otel_endpoint": settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        },
    }


@router.get("/graph")
async def graph_snapshot() -> dict[str, Any]:
    return LegalKnowledgeGraph.snapshot()


@router.post("/treaties")
async def register_treaty(payload: TreatyRegistration) -> dict[str, Any]:
    treaty = LegalKnowledgeGraph.register_treaty(
        treaty_name=payload.treaty_name,
        jurisdiction=payload.jurisdiction,
        legal_scope=payload.legal_scope,
    )
    LegalMemory.remember("treaty.registered", treaty)
    UnifiedObservability.record("graph", status="ok")
    return treaty


@router.post("/memory/cases/{case_id}")
async def save_case(case_id: str, payload: MemoryRecord) -> dict[str, Any]:
    return LegalMemory.save_case(case_id, payload.payload)


@router.get("/memory/cases/{case_id}")
async def get_case(case_id: str) -> dict[str, Any]:
    record = LegalMemory.get_case(case_id)
    if record is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    return record


@router.get("/john/hooks")
async def john_hooks() -> dict[str, Any]:
    return _john_hooks.profile()


@router.post("/john/hooks/annotate")
async def john_hook_annotation(payload: HookAnnotation) -> dict[str, Any]:
    return _john_hooks.annotate(payload.payload)
