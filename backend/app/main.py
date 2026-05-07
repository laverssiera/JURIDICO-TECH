from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.integration.event_bus import event_bus
from app.integration.event_subscribers import register_integration_subscribers
from app.integration.ws_stream import event_stream_hub
from app.persistence.store import persistence_store
from app.routers import legal_services, legal_radar, compliance, crm, legal_core, legal_admin
from app.routers import events_stream
from app.routers import preventive, contract_learning, arbitration, governance
from app.routers import tax, corporate, litigation, forensic, legal_nlp, evidence_vault
from app.routers import legal_digital_twin, regulatory_radar_global, trust, governance_ai, legal_os
from app.routers import legal_war_room, psycholegal, esg_human_rights, smart_clause
from app.routers import legal_knowledge_graph, autonomous_arbitration, legal_marketplace, legal_university
from app.routers import global_legal_simulation
from app.john import john_legal
from app.integration import mae_liceu
from juridicotech.modules.contracts import router as core_v2_contract_router
from juridicotech.modules.risk import router as core_v2_risk_router
from juridicotech.modules.bypass import router as core_v2_bypass_router
from juridicotech.modules.events import router as core_v2_events_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Persistência — inicializa SQLite e injeta store nos domínios críticos
    persistence_store.init()
    from app.routers import legal_digital_twin as _ldt_router
    from app.routers import legal_war_room as _wr_router
    from app.routers import global_legal_simulation as _sim_router
    from app.routers import trust as _trust_router
    _ldt_router._twin._store = persistence_store
    _ldt_router._twin._twins.update(
        {f"{r['entity_type']}:{r['entity_id']}": r for r in persistence_store.list("legal_digital_twin")}
    )
    _wr_router._wr._store = persistence_store
    _wr_router._wr._incidents.update(
        {r["incident_id"]: r for r in persistence_store.list("legal_war_room")}
    )
    _sim_router._sim._store = persistence_store
    _sim_router._sim._scenarios.update(
        {r["scenario_id"]: r for r in persistence_store.list("global_legal_simulation")}
    )
    _trust_router._trust._store = persistence_store

    register_integration_subscribers()
    event_stream_hub.register_subscribers()
    await event_bus.startup()
    try:
        yield
    finally:
        await event_bus.shutdown()
        persistence_store.close()


app = FastAPI(
    title="JURIDICO-TECH — LICEU 6.x",
    version="6.1.0",
    description=(
        "Infraestrutura Cognitiva Regulatória de Longo Prazo. "
        "Legal OS com Digital Twin Jurídico, Radar Regulatório, Arbitragem Autônoma, "
        "Forensic Intelligence, Trust Engine e Governança Assistida por IA."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registra listeners no bootstrap para cenários sem ciclo de startup explícito.
register_integration_subscribers()
event_stream_hub.register_subscribers()

@app.get("/")
def read_root() -> dict:
    return {
        "name": "JURIDICO-TECH — LICEU 6.x",
        "version": "6.1.0",
        "status": "online",
        "mission": "Infraestrutura Cognitiva Regulatória de Longo Prazo",
        "scope": [
            "engenharia societária",
            "constituição de SPE",
            "constituição de SCP",
            "estruturação incorporações",
            "auditoria contratual",
            "compliance LGPD",
            "blindagem patrimonial",
            "consultoria jurídica",
            "radar legislativo",
            "compliance trabalhista",
            "compliance imobiliário",
            "score jurídico vivo",
            "melhoria contínua contratual",
            "arbitragem",
            "governança corporativa",
            "john jurídico — general counsel cognitivo",
            "legal digital twin",
            "regulatory radar global",
            "arbitragem autônoma",
            "forensic intelligence center",
            "psycholegal engine",
            "esg + human rights engine",
            "smart clause engine",
            "legal knowledge graph",
            "legal operating system runtime",
            "trust engine",
            "governance ai",
            "legal war room",
            "legal marketplace",
            "universidade jurídica liceu",
            "global legal simulation",
        ],
    }


@app.get("/core-v2/health")
def core_v2_health() -> dict:
    return {"status": "ok"}

app.include_router(legal_services.router, prefix="/legal", tags=["Serviços Jurídicos"])
app.include_router(legal_core.router, prefix="/legal", tags=["Core Legal"])
app.include_router(legal_admin.router)
app.include_router(legal_radar.router, prefix="/legal/radar", tags=["Radar Legal"])
app.include_router(compliance.router, prefix="/legal/compliance", tags=["Compliance"])
app.include_router(crm.router, prefix="/legal", tags=["CRM Jurídico"])
app.include_router(john_legal.router, prefix="/john/legal", tags=["John Juridico"])
app.include_router(mae_liceu.router, prefix="/integration", tags=["Integração Mãe LICEU"])
app.include_router(legal_core.contract_router, tags=["Contract SDK"])
app.include_router(events_stream.router)
app.include_router(core_v2_contract_router, prefix="/core-v2/contracts", tags=["JuridicoTech Core V2"])
app.include_router(core_v2_risk_router, prefix="/core-v2/risk", tags=["JuridicoTech Core V2"])
app.include_router(core_v2_bypass_router, prefix="/core-v2/bypass", tags=["JuridicoTech Core V2"])
app.include_router(core_v2_events_router, prefix="/core-v2/events", tags=["JuridicoTech Core V2"])

# ── LICEU 6.0 — Módulos Cognitivos ──────────────────────────────────────────
app.include_router(preventive.router, prefix="/liceu/preventivo", tags=["LICEU 6.0 — Preventivo"])
app.include_router(contract_learning.router, prefix="/liceu/aprendizado", tags=["LICEU 6.0 — Aprendizado Contratual"])
app.include_router(arbitration.router, prefix="/liceu/arbitragem", tags=["LICEU 6.0 — Arbitragem"])
app.include_router(governance.router, prefix="/liceu/governanca", tags=["LICEU 6.0 — Governança"])
app.include_router(tax.router, prefix="/liceu/tributario", tags=["LICEU 6.0 — Tributário"])
app.include_router(corporate.router, prefix="/liceu/societario", tags=["LICEU 6.0 — Societário"])
app.include_router(litigation.router, prefix="/liceu/contencioso", tags=["LICEU 6.0 — Contencioso"])
app.include_router(forensic.router, prefix="/liceu/forense", tags=["LICEU 6.0 — Forense"])
app.include_router(legal_nlp.router, prefix="/liceu/nlp", tags=["LICEU 6.0 — Legal NLP/AI"])
app.include_router(evidence_vault.router, prefix="/liceu/cofre", tags=["LICEU 6.0 — Evidence Vault"])
app.include_router(legal_digital_twin.router, prefix="/liceu/twin", tags=["LICEU 6.x — Legal Digital Twin"])
app.include_router(regulatory_radar_global.router, prefix="/liceu/radar-global", tags=["LICEU 6.x — Regulatory Radar"])
app.include_router(autonomous_arbitration.router, prefix="/liceu/arbitragem-autonoma", tags=["LICEU 6.x — Autonomous Arbitration"])
app.include_router(legal_war_room.router, prefix="/liceu/war-room", tags=["LICEU 6.x — Legal War Room"])
app.include_router(psycholegal.router, prefix="/liceu/psycholegal", tags=["LICEU 6.x — Psycholegal"])
app.include_router(esg_human_rights.router, prefix="/liceu/esg-human-rights", tags=["LICEU 6.x — ESG Human Rights"])
app.include_router(smart_clause.router, prefix="/liceu/smart-clause", tags=["LICEU 6.x — Smart Clause"])
app.include_router(legal_knowledge_graph.router, prefix="/liceu/knowledge-graph", tags=["LICEU 6.x — Legal Knowledge Graph"])
app.include_router(legal_os.router, prefix="/liceu/legal-os", tags=["LICEU 6.x — Legal OS"])
app.include_router(trust.router, prefix="/liceu/trust", tags=["LICEU 6.x — Trust Engine"])
app.include_router(governance_ai.router, prefix="/liceu/governance-ai", tags=["LICEU 6.x — Governance AI"])
app.include_router(legal_marketplace.router, prefix="/liceu/marketplace", tags=["LICEU 6.x — Marketplace Jurídico"])
app.include_router(legal_university.router, prefix="/liceu/universidade", tags=["LICEU 6.x — Universidade Jurídica"])
app.include_router(global_legal_simulation.router, prefix="/liceu/simulacao-global", tags=["LICEU 6.x — Global Legal Simulation"])
