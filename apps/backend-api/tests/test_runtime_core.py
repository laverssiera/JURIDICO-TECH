from fastapi.testclient import TestClient

from app.main import app


def test_runtime_status_contains_core_layers() -> None:
    client = TestClient(app)

    response = client.get("/runtime/status")

    assert response.status_code == 200
    data = response.json()
    assert data["runtime"] == "federated"
    assert data["federation_authority"] == "active"
    assert data["knowledge_graph"] == "enabled"
    assert data["ecosystem_memory"] == "enabled"
    assert data["causal_runtime"] == "active"
    assert data["patent_intelligence"] == "active"
    assert data["autonomous_arbitration"] == "active"
    assert data["collective_legal_runtime"] == "online"


def test_runtime_graph_case_registers_case() -> None:
    client = TestClient(app)

    response = client.post("/runtime/graph-case")

    assert response.status_code == 200
    data = response.json()
    assert data["saved"] is True or data["saved"] is False
    assert data["backend"] in {"neo4j", "memory"}


def test_runtime_identity_dynamic_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/runtime/identity",
        json={
            "subject": "agent-lex-01",
            "roles": ["federated_agi", "legal_runtime"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["claims"]["subject"] == "agent-lex-01"
    assert data["claims"]["roles"] == ["federated_agi", "legal_runtime"]
    assert "token" in data
