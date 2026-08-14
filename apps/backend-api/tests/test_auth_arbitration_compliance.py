"""Integration tests — auth, arbitration, compliance."""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.session import engine, init_models

pytest_plugins = ["anyio"]


@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    await init_models()
    yield
    from sqlalchemy import text
    async with engine.begin() as conn:
        for tbl in [
            "compliance_alerts", "compliance_checks",
            "arbitration_events", "arbitration_cases",
            "refresh_tokens", "users",
        ]:
            await conn.execute(text(f"DELETE FROM {tbl}"))


@pytest_asyncio.fixture()
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── Auth ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_auth_register_login_refresh_me(client: AsyncClient):
    # Register
    r = await client.post("/auth/register", json={
        "email": "advogado@test.com",
        "password": "Senha@1234",
        "role": "advogado",
    })
    assert r.status_code == 201
    assert r.json()["role"] == "advogado"

    # Login
    r = await client.post("/auth/login", json={
        "email": "advogado@test.com",
        "password": "Senha@1234",
    })
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # /me
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r.status_code == 200
    assert r.json()["email"] == "advogado@test.com"

    # Refresh → novo refresh token emitido (rotação)
    r = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    new_tokens = r.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    # Old refresh token revoked
    r = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 401

    # Logout
    r = await client.post("/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_auth_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={"email": "x@x.com", "password": "aaa"})
    r = await client.post("/auth/login", json={"email": "x@x.com", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_duplicate_email(client: AsyncClient):
    await client.post("/auth/register", json={"email": "dup@dup.com", "password": "pass"})
    r = await client.post("/auth/register", json={"email": "dup@dup.com", "password": "pass2"})
    assert r.status_code == 409


# ── Arbitration ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_arbitration_lifecycle(client: AsyncClient):
    # Create
    r = await client.post("/arbitration/", json={
        "title": "Disputa Contratual ACME vs Beta",
        "parties": ["ACME Ltd", "Beta SA"],
    })
    assert r.status_code == 201
    data = r.json()
    case_id = data["id"]
    assert data["status"] == "open"
    assert len(data["events"]) == 1
    assert data["events"][0]["event_type"] == "filed"

    # List
    r = await client.get("/arbitration/")
    assert r.json()["total"] == 1

    # Get
    r = await client.get(f"/arbitration/{case_id}")
    assert r.status_code == 200

    # Add event
    r = await client.post(f"/arbitration/{case_id}/events", json={
        "event_type": "hearing_scheduled",
        "description": "Audiência marcada para 20/06/2026",
    })
    assert r.status_code == 201

    # Update → award
    r = await client.patch(f"/arbitration/{case_id}", json={
        "status": "award",
        "award_amount": 150000.0,
        "award_summary": "Indenização por descumprimento contratual",
    })
    assert r.status_code == 200
    assert r.json()["award_amount"] == 150000.0

    # List events
    r = await client.get(f"/arbitration/{case_id}/events")
    assert len(r.json()) == 2


# ── Compliance ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_compliance_check_and_alerts(client: AsyncClient):
    # Run check
    r = await client.post("/compliance/check", json={
        "entity_id": "empresa-001",
        "scope": "brasil",
    })
    assert r.status_code == 201
    data = r.json()
    check_id = data["id"]
    assert data["score"] >= 0
    assert data["status"] in ("passed", "failed", "review")

    # Get check
    r = await client.get(f"/compliance/checks/{check_id}")
    assert r.status_code == 200
    alerts = r.json()["alerts"]

    # Open alerts
    r = await client.get("/compliance/alerts/open")
    assert r.status_code == 200
    open_count = len(r.json())

    if alerts:
        alert_id = alerts[0]["id"]
        r = await client.patch(f"/compliance/alerts/{alert_id}/resolve")
        assert r.status_code == 200
        assert r.json()["resolved"] is True

        # Open alerts count decreased
        r = await client.get("/compliance/alerts/open")
        assert len(r.json()) == open_count - 1

    # List checks
    r = await client.get("/compliance/checks")
    assert r.json()["total"] >= 1

    # Filter by entity
    r = await client.get("/compliance/checks?entity_id=empresa-001")
    assert r.json()["total"] >= 1
