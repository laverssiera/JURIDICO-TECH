from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)



def test_create_spe_workflow():
    response = client.post(
        "/legal/create-spe",
        json={
            "name": "Residencial Aurora",
            "partners": ["ARCHIMEDES", "CEA INVESTIMENTOS"],
            "purpose": "Incorporação imobiliária",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "draft_created"
    assert payload["spe"]["name"] == "Residencial Aurora"
    assert "protocol" in payload



def test_contract_audit_returns_risks_and_guidance():
    response = client.post(
        "/legal/audit/contract",
        json={
            "title": "Contrato de Compra e Venda",
            "content": "A multa é integral para o comprador e não há cláusula de proteção de dados.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] in {"low", "medium", "high"}
    assert isinstance(payload["findings"], list)
    assert len(payload["findings"]) >= 1



def test_norm_alerts_list_is_available():
    response = client.get("/legal/norms/alerts")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert isinstance(payload["alerts"], list)



def test_compliance_check_returns_checklist():
    response = client.post("/legal/compliance/check/backoffice")

    assert response.status_code == 200
    payload = response.json()
    assert payload["monolito_id"] == "backoffice"
    assert payload["status"] in {"approved", "attention"}
    assert len(payload["checklist"]) >= 3


def test_contract_signed_event_starts_automatic_legal_closing():
    response = client.post(
        "/integration/events/contract.signed",
        json={
            "contract_id": "CTR-2026-001",
            "monolito_id": "backoffice",
            "spe_name": "Residencial Horizonte",
            "partners": ["ARQUITETA HOLDING", "CEA INVESTIMENTOS"],
            "purpose": "Incorporacao imobiliaria",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["event"] == "contract.signed"
    assert payload["status"] == "closing_started"
    assert payload["spe_draft"]["status"] == "draft_created"
    assert payload["compliance"]["status"] in {"approved", "attention"}
