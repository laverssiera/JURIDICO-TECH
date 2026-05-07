from fastapi.testclient import TestClient

from app.integration.event_bus import event_bus
from app.integration.legal_event_registry import subject_for_event
from app.main import app

client = TestClient(app)


def test_global_simulation_supplier_failure_shape():
    resp = client.post(
        "/liceu/simulacao-global/supplier-failure",
        json={
            "supplier_id": "SUP-22",
            "affected_works": 4,
            "affected_contracts": 3,
            "financial_exposure": 8_000_000,
            "contingency_ready": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_type"] == "supplier_failure"
    assert data["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]
    assert data["impact"]["works_disrupted"] == 4


def test_global_simulation_regulatory_change_shape():
    resp = client.post(
        "/liceu/simulacao-global/regulatory-change",
        json={
            "regulation_name": "Nova NR de Trabalho em Altura",
            "impacted_units": ["OPERA", "RH", "ANCHOR"],
            "adaptation_days": 12,
            "penalty_estimate": 1_200_000,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_type"] == "regulatory_change"
    assert "recommended_actions" in data
    assert len(data["recommended_actions"]) >= 1


def test_global_simulation_list_and_get():
    created = client.post(
        "/liceu/simulacao-global/supplier-failure",
        json={
            "supplier_id": "SUP-33",
            "affected_works": 1,
            "affected_contracts": 1,
            "financial_exposure": 100_000,
        },
    ).json()
    sid = created["scenario_id"]

    listed = client.get("/liceu/simulacao-global/")
    assert listed.status_code == 200
    assert len(listed.json()["scenarios"]) >= 1

    fetched = client.get(f"/liceu/simulacao-global/{sid}")
    assert fetched.status_code == 200
    assert fetched.json()["scenario_id"] == sid


def test_global_simulation_event_emitted():
    captured = []

    def handler(payload: dict) -> dict:
        captured.append(payload)
        return {"ok": True}

    event_bus.subscribe("simulation.global.executed", handler)

    resp = client.post(
        "/liceu/simulacao-global/supplier-failure",
        json={
            "supplier_id": "SUP-44",
            "affected_works": 2,
            "affected_contracts": 2,
            "financial_exposure": 600_000,
        },
    )
    assert resp.status_code == 200
    assert len(captured) >= 1
    assert captured[-1]["scenario_type"] == "supplier_failure"


def test_global_simulation_event_subjects_registered():
    assert subject_for_event("simulation.global.executed") == "liceu.events.legal.simulation.executed"
    assert subject_for_event("simulation.global.risk.high") == "liceu.events.legal.simulation.risk.high"
