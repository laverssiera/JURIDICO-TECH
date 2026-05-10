from fastapi.testclient import TestClient

from app.integration.legal_event_registry import subject_for_event
from app.main import app

client = TestClient(app)


def test_scientific_authorship_register_and_history():
    created = client.post(
        "/science/authorship/register",
        json={
            "experiment_id": "EXP-001",
            "author_id": "AUTH-001",
            "contribution_type": "discovery",
            "contribution_score": 92.5,
        },
    )
    assert created.status_code == 200
    assert created.json()["status"] == "registered"

    history = client.get("/science/authorship/history", params={"experiment_id": "EXP-001"})
    assert history.status_code == 200
    assert len(history.json()["history"]) >= 1


def test_patent_discovery_flow():
    created = client.post(
        "/patents/register",
        json={"title": "Composite-X", "category": "material", "novelty_score": 88.0},
    )
    assert created.status_code == 200
    patent_id = created.json()["data"]["id"]

    novelty = client.post(
        "/patents/analyze-novelty",
        json={"novelty_score": 88.0, "prior_art_candidates": ["PAT-OLD-1"]},
    )
    assert novelty.status_code == 200
    assert novelty.json()["is_novel"] is True

    approved = client.post("/patents/validate-prior-art", json={"patent_id": patent_id})
    assert approved.status_code == 200
    assert approved.json()["data"]["status"] == "approved"

    licensed = client.post(
        "/patents/license",
        json={"patent_id": patent_id, "licensee": "LAB-A", "royalty_rate": 2.5},
    )
    assert licensed.status_code == 200
    assert licensed.json()["status"] == "licensed"


def test_interplanetary_research_compliance_flow():
    checked = client.post(
        "/research/compliance/check",
        json={"research_type": "space", "risk_level": "high", "jurisdiction_scope": "orbit"},
    )
    assert checked.status_code == 200
    review_id = checked.json()["data"]["id"]

    approved = client.post(
        "/research/compliance/approve",
        json={"review_id": review_id, "approved_by": "counsel-01"},
    )
    assert approved.status_code == 200

    history = client.get("/research/compliance/history")
    assert history.status_code == 200
    assert len(history.json()["items"]) >= 1


def test_orbital_space_law_flow():
    treaty = client.post(
        "/space/treaty/analyze",
        json={"treaty_id": "TR-1", "jurisdiction": "orbit", "compliant": True},
    )
    assert treaty.status_code == 200
    assert treaty.json()["compliant"] is True

    review = client.post(
        "/space/mission/legal-review",
        json={"mission_id": "MIS-77", "approved": True},
    )
    assert review.status_code == 200
    assert review.json()["approved"] is True


def test_deep_ocean_law_flow():
    habitat = client.post(
        "/oceanic/habitat/legal-check",
        json={"habitat_id": "HBT-9", "depth_zone": "bathypelagic", "status": "compliant"},
    )
    assert habitat.status_code == 200
    assert habitat.json()["status"] == "compliant"

    risk = client.post(
        "/oceanic/environmental-risk",
        json={"project_id": "OC-12", "risk_level": "medium", "mitigation": ["buffer_zone"]},
    )
    assert risk.status_code == 200
    assert risk.json()["risk_level"] == "medium"


def test_ai_ethics_and_quantum_fusion_flow():
    risk = client.post(
        "/ai/governance/risk",
        json={"model_id": "AGI-01", "risk_level": "high", "risk_vector": ["autonomy"]},
    )
    assert risk.status_code == 200
    assert risk.json()["risk_level"] == "high"

    ethics = client.post(
        "/ai/governance/ethics-check",
        json={"model_id": "AGI-01", "compliant": False},
    )
    assert ethics.status_code == 200
    assert ethics.json()["compliant"] is False

    quantum = client.post(
        "/quantum/compliance/check",
        json={"runtime_id": "Q-12", "compliant": False},
    )
    assert quantum.status_code == 200
    assert quantum.json()["compliant"] is False

    fusion = client.post(
        "/fusion/reactor/audit",
        json={"reactor_id": "FUS-9", "audit_status": "completed"},
    )
    assert fusion.status_code == 200
    assert fusion.json()["audit_status"] == "completed"


def test_civilizational_governance_flow():
    impact = client.post(
        "/civilization/impact/analyze",
        json={
            "project_id": "CIV-1",
            "housing_impact": 15,
            "infrastructure_impact": 10,
            "social_benefit_score": 88,
        },
    )
    assert impact.status_code == 200
    assert impact.json()["project_id"] == "CIV-1"

    score = client.post("/civilization/social-benefit/score", json={"project_id": "CIV-1", "score": 91})
    assert score.status_code == 200
    assert score.json()["score"] == 91


def test_cosmic_law_subject_registry():
    cases = [
        ("science.authorship.registered", "liceu.events.science.authorship.registered"),
        ("patent.created", "liceu.events.patent.created"),
        ("research.compliance.approved", "liceu.events.research.compliance.approved"),
        ("space.mission.legal.approved", "liceu.events.space.mission.legal.approved"),
        ("oceanic.habitat.compliant", "liceu.events.oceanic.habitat.compliant"),
        ("ai.governance.alert", "liceu.events.ai.governance.alert"),
        ("quantum.runtime.risk.detected", "liceu.events.quantum.runtime.risk.detected"),
        ("civilization.impact.assessed", "liceu.events.civilization.impact.assessed"),
    ]
    for event_name, subject in cases:
        assert subject_for_event(event_name) == subject
