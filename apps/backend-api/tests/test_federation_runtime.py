from fastapi.testclient import TestClient

from app.federation.graph.legal_graph import LegalKnowledgeGraph
from app.federation.memory.runtime_memory import LegalMemory
from app.federation.observability.tracing import UnifiedObservability
from app.main import app


def setup_function() -> None:
    LegalKnowledgeGraph.reset()
    LegalMemory.reset()
    UnifiedObservability.reset()


def test_federation_summary_and_treaty_registration() -> None:
    client = TestClient(app)

    response = client.get("/federation/legal/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["compliance"]["lgpd"] is True
    assert data["war_room"]["federated_legal_runtime"] is True
    assert "diagnostics" in data
    assert data["diagnostics"]["configured"]["memory"] in {"auto", "memory", "redis"}

    response = client.post(
        "/federation/legal/treaties",
        json={
            "treaty_name": "Lunar Resource Accord",
            "jurisdiction": "lunar-orbit",
            "legal_scope": "orbital-mining",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Lunar Resource Accord"

    response = client.get("/federation/legal/graph")
    assert response.status_code == 200
    assert response.json()["nodes"] == 1


def test_federation_backend_diagnostics_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/federation/legal/diagnostics/backends")
    assert response.status_code == 200
    data = response.json()

    assert data["configured"]["memory"] in {"auto", "memory", "redis"}
    assert data["configured"]["graph"] in {"auto", "memory", "neo4j"}
    assert data["configured"]["observability"] in {"auto", "memory", "otel"}

    assert data["effective"]["memory"] in {"memory", "redis"}
    assert data["effective"]["graph"] in {"internal", "neo4j"}
    assert data["effective"]["observability"] in {"memory", "otel"}

    assert "connection" in data
    assert "nats_url" in data["connection"]


def test_federation_memory_and_john_hooks() -> None:
    client = TestClient(app)

    response = client.post(
        "/federation/legal/memory/cases/case-001",
        json={"payload": {"status": "active", "scope": "space-law"}},
    )
    assert response.status_code == 200
    assert response.json()["case_id"] == "case-001"

    response = client.get("/federation/legal/memory/cases/case-001")
    assert response.status_code == 200
    assert response.json()["scope"] == "space-law"

    response = client.get("/federation/legal/john/hooks")
    assert response.status_code == 200
    assert response.json()["persona"] == "JOHN BRASILEIRO"

    response = client.post(
        "/federation/legal/john/hooks/annotate",
        json={"payload": {"incident": "orbital-dispute"}},
    )
    assert response.status_code == 200
    assert response.json()["annotation"] == "federation_hook_applied"