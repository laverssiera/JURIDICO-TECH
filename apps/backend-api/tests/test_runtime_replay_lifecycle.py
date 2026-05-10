from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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

    status = client.get("/compliance/runtime/empresa-777/status")
    assert status.status_code == 200
    assert status.json()["entity_id"] == "empresa-777"

    pulse = client.post("/compliance/runtime/empresa-777/pulse")
    assert pulse.status_code == 200
    assert pulse.json()["check_count"] >= 2

    stop = client.delete("/compliance/runtime/empresa-777")
    assert stop.status_code == 200
    assert stop.json()["stopped"] is True

    _teardown()
