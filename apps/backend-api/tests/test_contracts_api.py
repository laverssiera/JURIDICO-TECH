from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_session
from app.main import app

TEST_DB = Path("./test_contracts.db")


def _build_override_sessionmaker() -> async_sessionmaker[AsyncSession]:
    test_engine = create_async_engine("sqlite+aiosqlite:///./test_contracts.db", future=True)
    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def _init() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio

    asyncio.run(_init())
    return session_maker


def test_create_and_list_contracts() -> None:
    if TEST_DB.exists():
        TEST_DB.unlink()

    session_maker = _build_override_sessionmaker()

    async def _override_get_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session

    client = TestClient(app)

    create_response = client.post(
        "/contracts/",
        headers={"x-tenant-id": "tenant-a"},
        json={
            "title": "Contrato de Obra SP-330",
            "contract_type": "engineering",
            "content": "Contrato com risco ambiental e multa por embargo NR18",
        },
    )

    assert create_response.status_code == 200
    payload = create_response.json()
    assert payload["status"] == "created"
    assert payload["contract_id"]
    assert payload["risk_score"] > 0
    assert payload["event_status"] == "outbox_pending"

    outbox_response = client.get("/events/outbox/pending")
    assert outbox_response.status_code == 200
    outbox_payload = outbox_response.json()
    assert outbox_payload["total"] == 1
    assert outbox_payload["items"][0]["subject"] == "legal.contract.created"

    flush_response = client.post("/events/outbox/flush")
    assert flush_response.status_code == 200
    flush_payload = flush_response.json()
    assert flush_payload["scanned"] >= 1

    list_response = client.get("/contracts/")
    assert list_response.status_code == 200

    listed = list_response.json()
    assert listed["total"] == 1
    assert listed["items"][0]["title"] == "Contrato de Obra SP-330"

    contract_id = payload["contract_id"]
    detail_response = client.get(f"/contracts/{contract_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["contract_id"] == contract_id
    assert detail["status"] == "created"

    create_clause_response = client.post(
        f"/contracts/{contract_id}/clauses",
        json={
            "clause_type": "rescisao",
            "clause_text": "Rescisao unilateral e multa sem proporcionalidade",
        },
    )
    assert create_clause_response.status_code == 200
    clause_payload = create_clause_response.json()
    assert clause_payload["clause_id"]
    assert clause_payload["contract_id"] == contract_id
    assert clause_payload["litigation_score"] >= 0

    clause_id = clause_payload["clause_id"]
    list_clauses_response = client.get(f"/contracts/{contract_id}/clauses")
    assert list_clauses_response.status_code == 200
    listed_clauses = list_clauses_response.json()
    assert listed_clauses["total"] == 1

    patch_clause_response = client.patch(
        f"/contracts/{contract_id}/clauses/{clause_id}",
        json={"clause_text": "Clausula revisada com limite de responsabilidade"},
    )
    assert patch_clause_response.status_code == 200
    patched_clause = patch_clause_response.json()
    assert patched_clause["clause_text"] == "Clausula revisada com limite de responsabilidade"

    delete_clause_response = client.delete(f"/contracts/{contract_id}/clauses/{clause_id}")
    assert delete_clause_response.status_code == 200
    assert delete_clause_response.json()["status"] == "deleted"

    app.dependency_overrides.clear()

    if TEST_DB.exists():
        TEST_DB.unlink()
