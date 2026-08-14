from pathlib import Path
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.compliance.runtime import ComplianceRuntime
from app.db.base import Base
from app.db.session import get_session
from app.main import app

TEST_DB = Path("./test_runtime_replay_lifecycle.db")


def _build_override_sessionmaker() -> async_sessionmaker[AsyncSession]:
    test_engine = create_async_engine("sqlite+aiosqlite:///./test_runtime_replay_lifecycle.db", future=True)
    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def _init() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio

    asyncio.run(_init())
    return session_maker


def _prepare_client() -> TestClient:
    if TEST_DB.exists():
        TEST_DB.unlink()

    session_maker = _build_override_sessionmaker()

    async def _override_get_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    return TestClient(app)


def _teardown() -> None:
    app.dependency_overrides.clear()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_contract_lifecycle_and_outbox_replay_flow() -> None:
    client = _prepare_client()

    created = client.post(
        "/contracts/",
        headers={"x-tenant-id": "tenant-a"},
        json={
            "title": "Contrato de Operacao Orbital",
            "contract_type": "science",
            "content": "Contrato com clausulas de responsabilidade e auditoria continua.",
        },
    )
    assert created.status_code == 200
    contract_id = created.json()["contract_id"]

    sign = client.patch(f"/contracts/{contract_id}/sign", json={"signatory": "counsel-01"})
    assert sign.status_code == 200
    assert sign.json()["status"] == "signed"

    activate = client.patch(f"/contracts/{contract_id}/activate")
    assert activate.status_code == 200
    assert activate.json()["status"] == "active"

    breach = client.patch(f"/contracts/{contract_id}/breach", json={"reason": "violacao de SLA"})
    assert breach.status_code == 200
    assert breach.json()["status"] == "breached"

    pending = client.get("/events/outbox/pending")
    assert pending.status_code == 200
    assert pending.json()["total"] >= 4

    replay_run = client.post("/replay/run", json={"subject_filter": "legal.contract", "limit": 20})
    assert replay_run.status_code == 201
    assert replay_run.json()["replayed"] >= 1

    replay_status = client.get("/replay/status")
    assert replay_status.status_code == 200
    assert replay_status.json()["total_outbox_events"] >= pending.json()["total"]

    _teardown()


def test_contract_terminate_emits_terminated_event() -> None:
    client = _prepare_client()

    created = client.post(
        "/contracts/",
        headers={"x-tenant-id": "tenant-b"},
        json={
            "title": "Contrato Habitat Oceanico",
            "contract_type": "engineering",
            "content": "Contrato para manutencao de habitat submerso.",
        },
    )
    contract_id = created.json()["contract_id"]

    sign = client.patch(f"/contracts/{contract_id}/sign", json={"signatory": "counsel-02"})
    assert sign.status_code == 200

    activate = client.patch(f"/contracts/{contract_id}/activate")
    assert activate.status_code == 200

    terminate = client.patch(f"/contracts/{contract_id}/terminate", json={"reason": "encerramento planejado"})
    assert terminate.status_code == 200
    assert terminate.json()["status"] == "terminated"

    events = client.get("/events/outbox?status=pending").json()["items"]
    subjects = [ev["subject"] for ev in events]
    assert "legal.contract.terminated" in subjects

    _teardown()


def test_compliance_runtime_endpoints_flow() -> None:
    client = _prepare_client()

    started = client.post("/compliance/runtime/start", json={"entity_id": "empresa-777", "scope": "global"})
    assert started.status_code == 201
    data = started.json()
    assert data["entity_id"] == "empresa-777"
    assert data["active"] is True
    assert data["check_count"] >= 1

    listed_all = client.get("/compliance/runtime")
    assert listed_all.status_code == 200
    assert listed_all.json()["total"] >= 1
    assert listed_all.json()["limit"] == 100
    assert listed_all.json()["offset"] == 0

    paged_one = client.get("/compliance/runtime?limit=1&offset=0")
    assert paged_one.status_code == 200
    assert paged_one.json()["limit"] == 1
    assert paged_one.json()["offset"] == 0
    assert len(paged_one.json()["items"]) == 1

    listed_active = client.get("/compliance/runtime?active=true")
    assert listed_active.status_code == 200
    active_items = [item for item in listed_active.json()["items"] if item["entity_id"] == "empresa-777"]
    assert len(active_items) == 1
    assert active_items[0]["active"] is True

    status = client.get("/compliance/runtime/empresa-777/status")
    assert status.status_code == 200
    assert status.json()["entity_id"] == "empresa-777"

    pulse = client.post("/compliance/runtime/empresa-777/pulse")
    assert pulse.status_code == 200
    assert pulse.json()["check_count"] >= 2

    update_scope = client.patch(
        "/compliance/runtime/empresa-777/scope",
        json={"scope": "interplanetary", "pulse_after_update": True},
    )
    assert update_scope.status_code == 200
    assert update_scope.json()["scope"] == "interplanetary"
    assert update_scope.json()["check_count"] >= 3

    stop = client.delete("/compliance/runtime/empresa-777")
    assert stop.status_code == 200
    assert stop.json()["stopped"] is True

    listed_inactive = client.get("/compliance/runtime?active=false")
    assert listed_inactive.status_code == 200
    inactive_items = [item for item in listed_inactive.json()["items"] if item["entity_id"] == "empresa-777"]
    assert len(inactive_items) == 1
    assert inactive_items[0]["active"] is False

    outbox = client.get("/events/outbox?status=pending")
    assert outbox.status_code == 200
    subjects = [item["subject"] for item in outbox.json()["items"]]
    assert "legal.compliance.runtime.started" in subjects
    assert "legal.compliance.runtime.pulsed" in subjects
    assert "legal.compliance.runtime.scope_updated" in subjects
    assert "legal.compliance.runtime.stopped" in subjects

    _teardown()


def test_compliance_runtime_isolde_mars_case_profile() -> None:
    client = _prepare_client()

    started = client.post(
        "/compliance/runtime/start",
        json={
            "entity_id": "isolde-mars-base",
            "scope": "interplanetary",
            "case_code": "CASE 3",
            "case_name": "ISOLDE-MARS",
        },
    )
    assert started.status_code == 201

    data = started.json()
    assert data["entity_id"] == "isolde-mars-base"
    assert data["case_code"] == "CASE 3"
    assert data["case_name"] == "ISOLDE-MARS"
    assert data["mission_profile"]["jurisdiction"] == "martian-base"
    assert "space-law" in data["objective_tracks"]
    assert "Pesquisar" not in data["mission_profile"].get("objectives", [])
    assert data["mission_profile"]["objectives"] == [
        "Pesquisa de núcleos exóticos",
        "Descoberta de materiais",
        "Blindagem radiológica",
        "Materiais para construção civil URIDICOTECH",
    ]

    status = client.get("/compliance/runtime/isolde-mars-base/status")
    assert status.status_code == 200
    assert status.json()["mission_profile"]["mission_class"] == "mars_base"

    _teardown()


def test_compliance_runtime_list_ordering() -> None:
    client = _prepare_client()

    first = client.post("/compliance/runtime/start", json={"entity_id": "empresa-001", "scope": "global"})
    assert first.status_code == 201

    second = client.post("/compliance/runtime/start", json={"entity_id": "empresa-002", "scope": "global"})
    assert second.status_code == 201

    desc = client.get("/compliance/runtime?order_by=registered_at&direction=desc")
    assert desc.status_code == 200
    desc_ids = [item["entity_id"] for item in desc.json()["items"]]
    assert desc_ids.index("empresa-002") < desc_ids.index("empresa-001")

    asc = client.get("/compliance/runtime?order_by=registered_at&direction=asc")
    assert asc.status_code == 200
    asc_ids = [item["entity_id"] for item in asc.json()["items"]]
    assert asc_ids.index("empresa-001") < asc_ids.index("empresa-002")

    _teardown()


def test_compliance_runtime_list_ordering_tie_breaks_by_entity_id() -> None:
    client = _prepare_client()

    r1 = client.post("/compliance/runtime/start", json={"entity_id": "empresa-b", "scope": "global"})
    assert r1.status_code == 201

    r2 = client.post("/compliance/runtime/start", json={"entity_id": "empresa-a", "scope": "global"})
    assert r2.status_code == 201

    # Force equal timestamps to verify deterministic secondary ordering.
    same_ts = datetime.now(UTC)
    e1 = ComplianceRuntime.status("empresa-b")
    e2 = ComplianceRuntime.status("empresa-a")
    assert e1 is not None and e2 is not None
    e1.registered_at = same_ts
    e2.registered_at = same_ts

    asc = client.get("/compliance/runtime?order_by=registered_at&direction=asc")
    assert asc.status_code == 200
    ids = [item["entity_id"] for item in asc.json()["items"] if item["entity_id"] in {"empresa-a", "empresa-b"}]
    assert ids == ["empresa-a", "empresa-b"]

    desc = client.get("/compliance/runtime?order_by=registered_at&direction=desc")
    assert desc.status_code == 200
    ids = [item["entity_id"] for item in desc.json()["items"] if item["entity_id"] in {"empresa-a", "empresa-b"}]
    assert ids == ["empresa-a", "empresa-b"]

    _teardown()
