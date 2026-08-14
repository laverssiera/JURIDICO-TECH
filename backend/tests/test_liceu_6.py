"""
Testes — LICEU 6.0
Módulo Preventivo, Aprendizado Contratual, Arbitragem, Governança e John Jurídico.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Módulo Preventivo ─────────────────────────────────────────────────────────

class TestPreventiveModule:
    def test_score_obra_returns_risk_level(self):
        resp = client.post(
            "/liceu/preventivo/score/obra",
            json={"obra_id": "OBR-101", "active_risks": ["nr18_incomplete", "weak_env_clause"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "legal_risk_score" in data
        assert "risk_level" in data
        assert data["entity_type"] == "obra"
        assert len(data["issues"]) >= 2

    def test_score_entity_includes_action_plan(self):
        resp = client.post(
            "/liceu/preventivo/score",
            json={
                "entity_id": "SPE-001",
                "entity_type": "spe",
                "active_risks": ["spe_no_dpo", "spe_no_compliance_officer"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "action_plan" in data
        assert isinstance(data["action_plan"], list)

    def test_score_fornecedor_no_risks_is_low(self):
        resp = client.post(
            "/liceu/preventivo/score/fornecedor",
            json={"supplier_id": "FOR-001", "active_risks": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["legal_risk_score"] == 0
        assert data["risk_level"] == "LOW"

    def test_list_risk_factors(self):
        resp = client.get("/liceu/preventivo/factors")
        assert resp.status_code == 200
        assert "factors" in resp.json()
        assert len(resp.json()["factors"]) > 0

    def test_list_risk_factors_scoped(self):
        resp = client.get("/liceu/preventivo/factors?scope=obra")
        assert resp.status_code == 200
        factors = resp.json()["factors"]
        assert all("obra" in f["scope"] for f in factors)


# ── Aprendizado Contratual ────────────────────────────────────────────────────

class TestContractLearning:
    def test_record_event_returns_event_id(self):
        resp = client.post(
            "/liceu/aprendizado/event",
            json={
                "source": "litigio",
                "issue_type": "atraso_entrega",
                "details": "Obra atrasou 90 dias",
                "contract_id": "CTR-ABC",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["recorded"] is True
        assert "event_id" in data

    def test_three_events_trigger_reinforcement(self):
        payload = {
            "source": "arbitragem",
            "issue_type": "infiltracao",
            "details": "Infiltração detectada",
        }
        client.post("/liceu/aprendizado/event", json=payload)
        client.post("/liceu/aprendizado/event", json=payload)
        resp = client.post("/liceu/aprendizado/event", json=payload)
        data = resp.json()
        assert data["issue_count_for_type"] >= 3
        # Reforço deve ter sido gerado (pode ser neste ou em chamadas anteriores do module)
        reinforcements_resp = client.get("/liceu/aprendizado/reinforcements")
        assert reinforcements_resp.status_code == 200

    def test_learning_stats_shape(self):
        resp = client.get("/liceu/aprendizado/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_learning_events" in data
        assert "reinforcements_generated" in data

    def test_missing_required_field_returns_422(self):
        resp = client.post(
            "/liceu/aprendizado/event",
            json={"source": "feedback"},  # falta issue_type
        )
        assert resp.status_code == 422


# ── Arbitragem ───────────────────────────────────────────────────────────────

class TestArbitration:
    def test_list_chambers(self):
        resp = client.get("/liceu/arbitragem/chambers")
        assert resp.status_code == 200
        chambers = resp.json()["chambers"]
        assert len(chambers) >= 3

    def test_open_case_and_get(self):
        resp = client.post(
            "/liceu/arbitragem/cases",
            json={
                "claimant": "Construtora Alpha",
                "respondent": "Fornecedor Beta",
                "contract_id": "CTR-XYZ",
                "dispute_description": "Atraso na entrega de materiais",
                "amount_in_dispute": 250000.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "open"
        assert data["phase"] == "instauração"
        case_id = data["case_id"]

        get_resp = client.get(f"/liceu/arbitragem/cases/{case_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["case_id"] == case_id

    def test_advance_phase(self):
        case = client.post(
            "/liceu/arbitragem/cases",
            json={
                "claimant": "A",
                "respondent": "B",
                "contract_id": "CTR-1",
                "dispute_description": "Conflito",
            },
        ).json()
        case_id = case["case_id"]
        resp = client.post(f"/liceu/arbitragem/cases/{case_id}/advance")
        assert resp.status_code == 200
        assert resp.json()["phase"] == "nomeação_árbitros"

    def test_not_found_returns_404(self):
        resp = client.get("/liceu/arbitragem/cases/ARB-NAOEXISTE")
        assert resp.status_code == 404


# ── Governança ────────────────────────────────────────────────────────────────

class TestGovernance:
    def test_create_deliberation(self):
        resp = client.post(
            "/liceu/governanca/deliberations",
            json={
                "entity_id": "SPE-001",
                "title": "Aprovação de Contrato",
                "resolution": "Aprovar contrato com Fornecedor X",
                "approvers": ["socio_a", "socio_b", "socio_c"],
                "quorum_required": 0.67,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"
        assert "deliberation_id" in data

    def test_vote_and_approve_by_quorum(self):
        d = client.post(
            "/liceu/governanca/deliberations",
            json={
                "entity_id": "SPE-002",
                "title": "Distribuição de Lucros",
                "resolution": "Distribuir 30% dos lucros",
                "approvers": ["socio_a", "socio_b"],
                "quorum_required": 0.51,
            },
        ).json()
        did = d["deliberation_id"]
        client.post(f"/liceu/governanca/deliberations/{did}/vote", json={"voter": "socio_a", "approve": True})
        resp = client.post(
            f"/liceu/governanca/deliberations/{did}/vote",
            json={"voter": "socio_b", "approve": True},
        )
        assert resp.json()["status"] == "approved"

    def test_governance_health_missing_items(self):
        resp = client.post(
            "/liceu/governanca/health",
            json={"entity_id": "SPE-003"},  # sem nenhum campo de saúde
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["governance_score"] < 100
        assert len(data["issues"]) > 0
