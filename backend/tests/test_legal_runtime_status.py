from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_legal_runtime_status_endpoint_shape():
    resp = client.get("/legal/runtime-status")
    assert resp.status_code == 200
    data = resp.json()

    assert "legal_governance_state" in data
    assert "interplanetary_compliance_readiness" in data
    assert "sovereign_contract_integrity" in data
    assert "civilization_legal_federation" in data
    assert "runtime_legal_health" in data
    assert data["runtime_objective"] == "Perpetual Sovereign Interplanetary Legal Intelligence Runtime"


def test_legal_compliance_metrics_endpoint_shape():
    # Primeiro gera sinais para povoar telemetry e lineage.
    client.get("/legal/runtime-status")

    resp = client.get("/legal/compliance-metrics")
    assert resp.status_code == 200
    data = resp.json()

    assert "compliance_propagation_metrics" in data
    assert "contract_integrity_score" in data
    assert "legal_federation_consistency" in data
    assert "trust_governance_metrics" in data
    assert "sovereign_legal_continuity" in data
