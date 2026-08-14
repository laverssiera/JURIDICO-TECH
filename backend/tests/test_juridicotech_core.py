from fastapi.testclient import TestClient

from juridicotech.main import app


client = TestClient(app)


def test_core_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_contract_create_sign_and_version_flow():
    create_response = client.post(
        "/contracts/",
        headers={"x-user-role": "SYSTEM_AUTOMATION"},
        json={
            "type": "intermediation",
            "created_by": "11111111-1111-1111-1111-111111111111",
            "deal_id": "22222222-2222-2222-2222-222222222222",
            "parties": ["buyer", "broker"],
        },
    )
    assert create_response.status_code == 200
    contract_id = create_response.json()["contract_id"]

    version_response = client.post(
        f"/contracts/{contract_id}/version",
        headers={"x-user-role": "JURIDICO_ANALYST"},
        json={
            "author_id": "11111111-1111-1111-1111-111111111111",
            "clause": "new-clause",
        },
    )
    assert version_response.status_code == 200
    assert version_response.json()["version"] == 2

    sign_response = client.post(
        f"/contracts/{contract_id}/sign",
        headers={"x-user-role": "JURIDICO_ANALYST"},
        json={
            "user_id": "11111111-1111-1111-1111-111111111111",
            "ip_address": "10.10.10.10",
        },
    )
    assert sign_response.status_code == 200
    assert sign_response.json()["status"] == "signed"


def test_risk_analyze_returns_expected_shape():
    response = client.post(
        "/risk/analyze",
        headers={"x-user-role": "JURIDICO_ANALYST"},
        json={
            "deal_id": "33333333-3333-3333-3333-333333333333",
            "actors": ["buyer"],
            "amount": 1_500_000,
            "has_documents": False,
            "user_age_days": 7,
            "actor_id": "11111111-1111-1111-1111-111111111111",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] in {"low", "medium", "high"}
    assert isinstance(payload["score"], float)
    assert isinstance(payload["flags"], list)


def test_bypass_protect_and_detect():
    protect_response = client.post(
        "/bypass/protect",
        headers={"x-user-role": "SYSTEM_AUTOMATION"},
        json={
            "lead_id": "44444444-4444-4444-4444-444444444444",
            "broker_id": "55555555-5555-5555-5555-555555555555",
            "property_id": "66666666-6666-6666-6666-666666666666",
            "commission_owner_id": "55555555-5555-5555-5555-555555555555",
        },
    )
    assert protect_response.status_code == 200

    check_response = client.post(
        "/bypass/check",
        headers={"x-user-role": "SYSTEM_AUTOMATION"},
        json={
            "lead_id": "44444444-4444-4444-4444-444444444444",
            "broker_id": "55555555-5555-5555-5555-555555555555",
            "property_id": "66666666-6666-6666-6666-666666666666",
            "candidate_broker_id": "77777777-7777-7777-7777-777777777777",
        },
    )
    assert check_response.status_code == 200
    assert check_response.json()["detected"] is True
    assert check_response.json()["blocked"] is True


def test_events_deal_created_end_to_end_fallback_mode():
    response = client.post(
        "/events/deal-created",
        headers={"x-user-role": "SYSTEM_AUTOMATION"},
        json={
            "deal_id": "88888888-8888-8888-8888-888888888888",
            "user_id": "11111111-1111-1111-1111-111111111111",
            "contract_type": "intermediation",
            "actors": ["buyer"],
            "amount": 100000,
            "has_documents": True,
            "user_age_days": 300,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "contract_id" in payload
    assert "risk" in payload
    assert "decision" in payload
    assert "blocked" in payload
