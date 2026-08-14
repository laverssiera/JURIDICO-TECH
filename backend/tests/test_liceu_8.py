from fastapi.testclient import TestClient

from app.main import app
from app.integration.legal_event_registry import subject_for_event

client = TestClient(app)


def test_legal_digital_twin_upsert_and_get():
    payload = {
        "entity_type": "supplier",
        "entity_id": "SUP-22",
        "contracts": {"overdue": 2, "conflicts": 1},
        "compliance": {"critical_non_conformities": 1},
        "litigation": {"active_cases": 2},
        "behavior": {"high_delay_risk": True, "litigious_trend": True},
    }
    upsert = client.post("/liceu/twin/upsert", json=payload)
    assert upsert.status_code == 200
    assert upsert.json()["legal_exposure"] > 0

    get_resp = client.get("/liceu/twin/supplier/SUP-22")
    assert get_resp.status_code == 200
    assert get_resp.json()["predicted_claim_probability"] >= 1


def test_regulatory_radar_signal_flow():
    sig = client.post(
        "/liceu/radar-global/signals",
        json={
            "source": "NR",
            "title": "Nova NR de segurança em altura",
            "summary": "Treinamento obrigatório para operação em 15 dias",
            "tags": ["nr", "sst"],
            "severity": "high",
        },
    )
    assert sig.status_code == 200
    signal_id = sig.json()["signal_id"]
    assert "OPERA" in sig.json()["impact"]["impacted_systems"]

    dis = client.post(f"/liceu/radar-global/signals/{signal_id}/disseminate")
    assert dis.status_code == 200
    assert dis.json()["status"] == "disseminated"


def test_autonomous_arbitration_settlement():
    med = client.post(
        "/liceu/arbitragem-autonoma/mediations",
        json={
            "conflict_type": "atraso_fornecedor",
            "claimant": "SPE A",
            "respondent": "Fornecedor B",
            "contract_id": "CTR-999",
            "claimed_amount": 200000,
        },
    )
    assert med.status_code == 200
    mid = med.json()["mediation_id"]

    client.post(
        f"/liceu/arbitragem-autonoma/mediations/{mid}/evidence",
        json={"source": "ANCHOR", "event": "laudo confirma atraso", "weight": 5},
    )
    suggestion = client.post(f"/liceu/arbitragem-autonoma/mediations/{mid}/settlement")
    assert suggestion.status_code == 200
    assert suggestion.json()["suggested_amount"] > 0


def test_war_room_incident_response():
    inc = client.post(
        "/liceu/war-room/incidents",
        json={
            "title": "Acidente estrutural obra 41",
            "severity": "critical",
            "category": "acidente_grave",
            "summary": "Interdição parcial da área",
        },
    )
    assert inc.status_code == 200
    iid = inc.json()["incident_id"]

    ev = client.post(
        f"/liceu/war-room/incidents/{iid}/evidence",
        json={"description": "Vídeo drone perícia", "source": "ANCHOR"},
    )
    assert ev.status_code == 200

    official = client.post(f"/liceu/war-room/incidents/{iid}/official-response")
    assert official.status_code == 200
    assert "resposta jurídica" in official.json()["narrative"].lower()


def test_psycholegal_assessment():
    resp = client.post(
        "/liceu/psycholegal/assess",
        json={
            "entity_id": "SUP-31",
            "signals": {
                "pattern_change": True,
                "contract_aggressiveness": True,
                "recurring_delays": 4,
                "fraud_indicators": True,
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json()["risk_level"] in ["HIGH", "CRITICAL"]


def test_esg_human_rights_engine():
    resp = client.post(
        "/liceu/esg-human-rights/evaluate",
        json={
            "entity_id": "OBR-500",
            "indicators": {
                "analogous_slave_labor_risk": False,
                "sst_compliant": False,
                "accessibility_compliant": True,
                "waste_disposal_compliant": False,
                "high_emissions": True,
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json()["esg_human_rights_score"] < 100


def test_smart_clause_recommendation():
    clause = client.post(
        "/liceu/smart-clause/",
        json={"type": "retenção garantia", "text": "Cláusula de retenção de 5% até aceite final."},
    )
    assert clause.status_code == 200
    cid = clause.json()["clause_id"]

    client.post(f"/liceu/smart-clause/{cid}/performance", json={"prevented_litigation": True})
    client.post(f"/liceu/smart-clause/{cid}/performance", json={"prevented_litigation": True})
    third = client.post(f"/liceu/smart-clause/{cid}/performance", json={"prevented_litigation": True})
    assert third.status_code == 200
    assert third.json()["recommended"] is True


def test_knowledge_graph_flow():
    client.post("/liceu/knowledge-graph/nodes", json={"node_id": "SUP-1", "node_type": "supplier"})
    client.post("/liceu/knowledge-graph/nodes", json={"node_id": "CTR-1", "node_type": "contract"})
    edge = client.post(
        "/liceu/knowledge-graph/edges",
        json={"source_id": "SUP-1", "target_id": "CTR-1", "relation": "supplies"},
    )
    assert edge.status_code == 200

    neighbors = client.get("/liceu/knowledge-graph/neighbors/SUP-1")
    assert neighbors.status_code == 200
    assert "CTR-1" in neighbors.json()["neighbors"]


def test_legal_os_gate_block_and_list():
    blocked = client.post(
        "/liceu/legal-os/gate",
        json={
            "operation_type": "sign_contract",
            "risk_score": 85,
            "trust_score": 40,
            "mandatory_docs_ok": False,
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["allow"] is False

    listed = client.get("/liceu/legal-os/decisions")
    assert listed.status_code == 200
    assert len(listed.json()["decisions"]) >= 1


def test_trust_engine_score():
    resp = client.post(
        "/liceu/trust/score",
        json={
            "entity_id": "INV-10",
            "entity_type": "investidor",
            "metrics": {
                "compliance": 90,
                "historico": 80,
                "litigios": 70,
                "performance": 85,
                "esg": 88,
                "financeiro": 92,
                "comportamento": 75,
                "reputacao": 80,
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json()["trust_tier"] in ["MEDIUM", "HIGH"]


def test_governance_ai_block():
    resp = client.post(
        "/liceu/governance-ai/evaluate",
        json={"operation_id": "OP-900", "risk_score": 90, "environmental_critical": True},
    )
    assert resp.status_code == 200
    assert resp.json()["action"] == "block"


def test_marketplace_and_university():
    req = client.post(
        "/liceu/marketplace/requests",
        json={
            "client_name": "Construtora Externa Z",
            "service_type": "pericia",
            "description": "Perícia de vício estrutural",
            "budget": 45000,
        },
    )
    assert req.status_code == 200

    en = client.post(
        "/liceu/universidade/enroll",
        json={"person_id": "USR-1", "profile": "engenheiros"},
    )
    assert en.status_code == 200
    assert len(en.json()["courses"]) >= 1


def test_event_registry_next_layers_subjects():
    cases = [
        ("twin.updated", "liceu.events.legal.twin.updated"),
        ("radar.signal.ingested", "liceu.events.legal.radar.signal.ingested"),
        ("autonomous_arbitration.settlement.suggested", "liceu.events.arbitration.settlement.suggested"),
        ("war_room.incident.opened", "liceu.events.legal.warroom.incident.opened"),
        ("trust.score.updated", "liceu.events.legal.trust.score.updated"),
    ]
    for event, subject in cases:
        assert subject_for_event(event) == subject
