from fastapi.testclient import TestClient

from app.integration.event_bus import event_bus
from app.main import app

client = TestClient(app)


def test_twin_updated_event_is_emitted():
    captured = []

    def handler(payload: dict) -> dict:
        captured.append(payload)
        return {"ok": True}

    event_bus.subscribe("twin.updated", handler)

    resp = client.post(
        "/liceu/twin/upsert",
        json={
            "entity_type": "supplier",
            "entity_id": "SUP-EVT-1",
            "contracts": {"overdue": 1},
        },
    )
    assert resp.status_code == 200
    assert len(captured) >= 1
    assert captured[-1]["entity_id"] == "SUP-EVT-1"


def test_radar_ingested_event_is_emitted():
    captured = []

    def handler(payload: dict) -> dict:
        captured.append(payload)
        return {"ok": True}

    event_bus.subscribe("radar.signal.ingested", handler)

    resp = client.post(
        "/liceu/radar-global/signals",
        json={
            "source": "NR",
            "title": "Atualização NR 18",
            "summary": "Mudança de procedimento",
            "tags": ["nr", "sst"],
        },
    )
    assert resp.status_code == 200
    assert len(captured) >= 1
    assert captured[-1]["source"] == "NR"


def test_war_room_opened_event_is_emitted():
    captured = []

    def handler(payload: dict) -> dict:
        captured.append(payload)
        return {"ok": True}

    event_bus.subscribe("war_room.incident.opened", handler)

    resp = client.post(
        "/liceu/war-room/incidents",
        json={
            "title": "Evento crítico",
            "severity": "high",
            "category": "esg",
            "summary": "Incidente em obra",
        },
    )
    assert resp.status_code == 200
    assert len(captured) >= 1
    assert captured[-1]["title"] == "Evento crítico"


def test_legal_os_blocked_event_is_emitted():
    captured = []

    def handler(payload: dict) -> dict:
        captured.append(payload)
        return {"ok": True}

    event_bus.subscribe("legal_os.gate.blocked", handler)

    resp = client.post(
        "/liceu/legal-os/gate",
        json={
            "operation_type": "sign_contract",
            "risk_score": 90,
            "trust_score": 20,
            "mandatory_docs_ok": False,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["allow"] is False
    assert len(captured) >= 1
    assert captured[-1]["allow"] is False


def test_trust_score_updated_event_is_emitted():
    captured = []

    def handler(payload: dict) -> dict:
        captured.append(payload)
        return {"ok": True}

    event_bus.subscribe("trust.score.updated", handler)

    resp = client.post(
        "/liceu/trust/score",
        json={
            "entity_id": "SUP-EVT-2",
            "entity_type": "supplier",
            "metrics": {"compliance": 80, "historico": 75, "litigios": 70},
        },
    )
    assert resp.status_code == 200
    assert len(captured) >= 1
    assert captured[-1]["entity_id"] == "SUP-EVT-2"
