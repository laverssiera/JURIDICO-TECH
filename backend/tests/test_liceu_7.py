"""
Testes — LICEU 6.0 — Fase 2
Tax, Corporate, Litigation, Forensic, Legal NLP, Evidence Vault, Event Registry.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Tax Intelligence ──────────────────────────────────────────────────────────

class TestTaxIntelligence:
    def test_suggest_regime_spe_ret(self):
        resp = client.post(
            "/liceu/tributario/regime/suggest",
            json={
                "annual_revenue": 10_000_000,
                "entity_type": "spe_incorporacao",
                "has_patrimonio_afetacao": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["recommended"] == "ret"
        assert len(data["suggestions"]) >= 1

    def test_suggest_regime_small_company(self):
        resp = client.post(
            "/liceu/tributario/regime/suggest",
            json={"annual_revenue": 1_000_000, "entity_type": "ltda"},
        )
        assert resp.status_code == 200
        assert resp.json()["recommended"] == "simples_nacional"

    def test_estimate_burden_ret(self):
        resp = client.post(
            "/liceu/tributario/burden/estimate",
            json={"regime": "ret", "annual_revenue": 5_000_000},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_tax_burden"] == pytest.approx(200_000, rel=0.01)
        assert data["effective_rate_pct"] == pytest.approx(4.0, rel=0.01)

    def test_estimate_burden_lucro_presumido(self):
        resp = client.post(
            "/liceu/tributario/burden/estimate",
            json={"regime": "lucro_presumido", "annual_revenue": 2_000_000},
        )
        assert resp.status_code == 200
        assert "IRPJ" in resp.json()["estimated_taxes"]

    def test_tax_risk_check(self):
        resp = client.post(
            "/liceu/tributario/risk",
            json={"entity_id": "SPE-001"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tax_risk_score"] > 0
        assert len(data["issues"]) > 0

    def test_list_incentivos(self):
        resp = client.get("/liceu/tributario/incentivos")
        assert resp.status_code == 200
        assert len(resp.json()["incentivos"]) >= 3


# ── Corporate Engine ──────────────────────────────────────────────────────────

class TestCorporate:
    def test_spe_checklist(self):
        resp = client.get("/liceu/societario/checklist?entity_type=spe_ltda")
        assert resp.status_code == 200
        assert len(resp.json()["checklist"]) >= 5

    def test_register_and_get_entity(self):
        resp = client.post(
            "/liceu/societario/entities",
            json={
                "name": "SPE Residencial Alpha",
                "entity_type": "spe_ltda",
                "object": "Incorporação imobiliária — Residencial Alpha",
                "partners": [
                    {"name": "Sócio A", "participation_pct": 60.0},
                    {"name": "Sócio B", "participation_pct": 40.0},
                ],
            },
        )
        assert resp.status_code == 200
        entity_id = resp.json()["entity_id"]

        get_resp = client.get(f"/liceu/societario/entities/{entity_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "SPE Residencial Alpha"

    def test_cap_table_complete(self):
        entity = client.post(
            "/liceu/societario/entities",
            json={
                "name": "Holding XYZ",
                "entity_type": "holding",
                "object": "Participação societária",
                "partners": [{"name": "Fundador", "participation_pct": 100.0}],
            },
        ).json()
        eid = entity["entity_id"]
        ct = client.get(f"/liceu/societario/entities/{eid}/cap-table").json()
        assert ct["is_complete"] is True
        assert ct["total_pct"] == 100.0

    def test_record_ata(self):
        entity = client.post(
            "/liceu/societario/entities",
            json={
                "name": "SPE Beta",
                "entity_type": "spe_sa",
                "object": "Empreendimento Beta",
                "partners": [{"name": "P1", "participation_pct": 50}, {"name": "P2", "participation_pct": 50}],
            },
        ).json()
        eid = entity["entity_id"]
        resp = client.post(
            f"/liceu/societario/entities/{eid}/atas",
            json={
                "tipo": "assembleia_geral",
                "pauta": ["Aprovação de contratos", "Distribuição de resultados"],
                "resolucoes": ["Contratos aprovados", "30% distribuído"],
                "presentes": ["P1", "P2"],
            },
        )
        assert resp.status_code == 200
        assert "ata_id" in resp.json()

    def test_tokenization_flow(self):
        entity = client.post(
            "/liceu/societario/entities",
            json={
                "name": "SPE Token",
                "entity_type": "spe_ltda",
                "object": "Tokenização",
                "partners": [{"name": "Investidor", "participation_pct": 100}],
            },
        ).json()
        eid = entity["entity_id"]
        resp = client.post(
            f"/liceu/societario/entities/{eid}/tokenization",
            json={"token_supply": 100_000, "price_per_token": 10.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["market_cap"] == pytest.approx(1_000_000)
        assert "required_steps" in data


# ── Litigation ────────────────────────────────────────────────────────────────

class TestLitigation:
    def test_open_process(self):
        resp = client.post(
            "/liceu/contencioso/processes",
            json={
                "process_type": "rescisão_contratual",
                "plaintiff": "LICEU Incorporações",
                "defendant": "Fornecedor X",
                "description": "Inadimplemento contratual",
                "tribunal": "TJSP",
                "amount_in_dispute": 300_000,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["phase"] == "petição_inicial"
        assert "process_id" in data

    def test_advance_and_analytics(self):
        proc = client.post(
            "/liceu/contencioso/processes",
            json={
                "process_type": "ação_cobrança",
                "plaintiff": "A",
                "defendant": "B",
                "description": "Cobrança",
                "tribunal": "TJRJ",
                "amount_in_dispute": 50_000,
            },
        ).json()
        pid = proc["process_id"]
        adv = client.post(f"/liceu/contencioso/processes/{pid}/advance").json()
        assert adv["phase"] == "citação"

        analytics = client.get("/liceu/contencioso/analytics").json()
        assert analytics["total_processes"] >= 1
        assert "total_financial_exposure" in analytics

    def test_add_deadline(self):
        proc = client.post(
            "/liceu/contencioso/processes",
            json={
                "process_type": "ação_cobrança",
                "plaintiff": "X",
                "defendant": "Y",
                "description": "Test",
                "tribunal": "STJ",
            },
        ).json()
        resp = client.post(
            f"/liceu/contencioso/processes/{proc['process_id']}/deadlines",
            json={"description": "Contestação", "due_date": "2026-06-01"},
        )
        assert resp.status_code == 200
        assert "deadline_id" in resp.json()

    def test_tribunal_integrations(self):
        resp = client.get("/liceu/contencioso/tribunals")
        assert resp.status_code == 200
        assert len(resp.json()["tribunals"]) >= 3


# ── Forensic ──────────────────────────────────────────────────────────────────

class TestForensic:
    def test_open_and_conclude_laudo(self):
        resp = client.post(
            "/liceu/forense/laudos",
            json={
                "pericia_type": "laudo_infiltracao",
                "requester": "LICEU Incorporações",
                "subject": "Apartamento 204 — infiltração no banheiro",
                "location": "Rua A, 100, São Paulo",
            },
        )
        assert resp.status_code == 200
        lid = resp.json()["laudo_id"]

        finding = client.post(
            f"/liceu/forense/laudos/{lid}/findings",
            json={"finding": "Ausência de impermeabilização na laje", "severity": "high"},
        )
        assert finding.status_code == 200

        conclude = client.post(
            f"/liceu/forense/laudos/{lid}/conclude",
            json={"conclusion": "Vício construtivo confirmado — responsabilidade da construtora", "perito": "Eng. Silva"},
        )
        assert conclude.status_code == 200
        assert conclude.json()["status"] == "concluido"

    def test_custody_chain(self):
        laudo = client.post(
            "/liceu/forense/laudos",
            json={"pericia_type": "pericia_engenharia", "requester": "Juízo", "subject": "Obra Y"},
        ).json()
        lid = laudo["laudo_id"]
        client.post(
            f"/liceu/forense/laudos/{lid}/custody/transfer",
            json={"from": "Perito Inicial", "to": "Perito Substituto", "reason": "Impedimento"},
        )
        chain = client.get(f"/liceu/forense/laudos/{lid}/custody").json()
        assert len(chain["custody_chain"]) >= 1

    def test_timeline_reconstruction(self):
        laudo = client.post(
            "/liceu/forense/laudos",
            json={"pericia_type": "reconstrucao_evento", "requester": "ANCHOR", "subject": "Acidente Obra Z"},
        ).json()
        lid = laudo["laudo_id"]
        resp = client.get(f"/liceu/forense/laudos/{lid}/timeline")
        assert resp.status_code == 200
        assert "timeline" in resp.json()


# ── Legal NLP ─────────────────────────────────────────────────────────────────

class TestLegalNLP:
    def test_analyze_contract_detects_risks(self):
        text = (
            "Cláusula 1: responsabilidade do contratante é ilimitada. "
            "Cláusula 2: O prazo de entrega será conforme disponibilidade. "
            "Cláusula 3: sem garantia técnica sobre os serviços."
        )
        resp = client.post("/liceu/nlp/analyze-contract", json={"contract_text": text})
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_count"] >= 2
        assert data["overall_risk"] in ("critical", "high", "medium")

    def test_generate_document_notificacao(self):
        resp = client.post(
            "/liceu/nlp/generate-document",
            json={
                "template_id": "notificacao_extrajudicial",
                "variables": {
                    "destinatario": "Fornecedor XYZ",
                    "assunto": "inadimplemento contratual",
                    "prazo": "10",
                    "providencias": "pagamento do saldo devedor",
                    "remetente": "LICEU Incorporações Ltda.",
                },
            },
        )
        assert resp.status_code == 200
        assert "NOTIFICAÇÃO EXTRAJUDICIAL" in resp.json()["document"]

    def test_generate_document_missing_var_returns_400(self):
        resp = client.post(
            "/liceu/nlp/generate-document",
            json={"template_id": "notificacao_extrajudicial", "variables": {}},
        )
        assert resp.status_code == 400

    def test_list_templates(self):
        resp = client.get("/liceu/nlp/templates")
        assert resp.status_code == 200
        assert len(resp.json()["templates"]) >= 3

    def test_extract_clauses(self):
        text = "Objeto do contrato: fornecimento de materiais. Valor do contrato: R$ 50.000. Prazo de entrega: 30 dias."
        resp = client.post("/liceu/nlp/extract-clauses", json={"contract_text": text})
        assert resp.status_code == 200
        assert resp.json()["clause_count"] >= 1


# ── Evidence Vault ────────────────────────────────────────────────────────────

class TestEvidenceVault:
    def test_deposit_and_verify(self):
        resp = client.post(
            "/liceu/cofre/deposit",
            json={
                "title": "Laudo Infiltração Apt 204",
                "content": "Laudo técnico: vício construtivo confirmado na unidade 204.",
                "depositor": "Eng. Silva",
                "tags": ["laudo", "infiltracao"],
                "linked_entity": "LAU-001",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["icp_signed"] is True
        assert "blockchain_anchor" in data
        eid = data["evidence_id"]

        verify = client.post(
            f"/liceu/cofre/{eid}/verify",
            json={"original_content": "Laudo técnico: vício construtivo confirmado na unidade 204."},
        )
        assert verify.status_code == 200
        assert verify.json()["integrity_ok"] is True

    def test_verify_tampered_content(self):
        dep = client.post(
            "/liceu/cofre/deposit",
            json={"title": "Doc Teste", "content": "Conteúdo original", "depositor": "Sistema"},
        ).json()
        verify = client.post(
            f"/liceu/cofre/{dep['evidence_id']}/verify",
            json={"original_content": "Conteúdo alterado"},
        )
        assert verify.json()["integrity_ok"] is False

    def test_custody_transfer(self):
        dep = client.post(
            "/liceu/cofre/deposit",
            json={"title": "Evidência Processo", "content": "Dados do processo", "depositor": "Perito A"},
        ).json()
        eid = dep["evidence_id"]
        resp = client.post(
            f"/liceu/cofre/{eid}/custody/transfer",
            json={"from": "Perito A", "to": "Juízo da 3ª Vara", "reason": "Entrega oficial"},
        )
        assert resp.status_code == 200


# ── Event Registry LICEU 6.0 ─────────────────────────────────────────────────

class TestEventRegistry:
    def test_liceu_subjects_registered(self):
        from app.integration.legal_event_registry import subject_for_event
        cases = [
            ("arbitration.case.opened", "liceu.events.arbitration.case.opened"),
            ("litigation.process.opened", "liceu.events.litigation.process.opened"),
            ("forensic.laudo.concluded", "liceu.events.forensic.laudo.concluded"),
            ("tax.risk.flagged", "liceu.events.tax.risk.flagged"),
            ("vault.evidence.deposited", "liceu.events.vault.evidence.deposited"),
            ("compliance.check.failed", "liceu.events.compliance.check.failed"),
            ("governance.deliberation.approved", "liceu.events.governance.deliberation.approved"),
        ]
        for event, expected_subject in cases:
            assert subject_for_event(event) == expected_subject, f"Falhou para {event}"
