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


def test_space_outer_treaty_itar_and_export_control_runtime_flow():
    treaty_runtime = client.post(
        "/space/outer-space-treaty/runtime",
        json={"mission_id": "MIS-201", "involves_dual_use_tech": False},
    )
    assert treaty_runtime.status_code == 200
    assert treaty_runtime.json()["runtime"] == "outer-space-treaty"
    assert treaty_runtime.json()["status"] == "compliant"

    itar_runtime = client.post(
        "/space/itar/runtime",
        json={
            "mission_id": "MIS-202",
            "includes_us_munitions_list_item": True,
            "has_reexport": False,
            "destination_country": "BR",
        },
    )
    assert itar_runtime.status_code == 200
    assert itar_runtime.json()["runtime"] == "itar"
    assert itar_runtime.json()["license_required"] is True

    export_control = client.post(
        "/space/export-control/runtime",
        json={
            "mission_id": "MIS-203",
            "includes_us_origin_hardware": True,
            "has_reexport": True,
            "end_user_verified": True,
        },
    )
    assert export_control.status_code == 200
    assert export_control.json()["runtime"] == "export-control"
    assert export_control.json()["status"] == "escalation-required"


def test_space_compliance_suite_runtime_flow():
    compliant_case = client.post(
        "/space/runtime/compliance-suite",
        json={
            "mission_id": "MIS-301",
            "involves_dual_use_tech": False,
            "includes_us_munitions_list_item": False,
            "includes_us_origin_hardware": False,
            "has_reexport": False,
            "end_user_verified": True,
        },
    )
    assert compliant_case.status_code == 200
    assert compliant_case.json()["runtime"] == "space-compliance-suite"
    assert compliant_case.json()["requires_review"] is False

    review_case = client.post(
        "/space/runtime/compliance-suite",
        json={
            "mission_id": "MIS-302",
            "involves_dual_use_tech": True,
            "includes_us_munitions_list_item": True,
            "includes_us_origin_hardware": True,
            "has_reexport": True,
            "end_user_verified": True,
        },
    )
    assert review_case.status_code == 200
    assert review_case.json()["requires_review"] is True
    assert review_case.json()["controls"]["outer_space_treaty"]["status"] == "review-required"
    assert review_case.json()["controls"]["itar"]["status"] == "license-required"
    assert review_case.json()["controls"]["export_control"]["status"] == "escalation-required"


def test_space_compliance_suite_schema_endpoint():
    schema = client.get("/space/runtime/compliance-suite/schema")
    assert schema.status_code == 200
    body = schema.json()

    assert body["endpoint"] == "/space/runtime/compliance-suite"
    assert body["method"] == "POST"
    assert body["request_schema"]["mission_id"] == "string"
    assert body["request_schema"]["end_user_verified"] == "boolean"
    assert body["example_request"]["mission_id"] == "MIS-900"
    assert body["example_response"]["runtime"] == "space-compliance-suite"


def test_space_compliance_suite_openapi_schema_present():
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    spec = openapi.json()

    suite_path = spec["paths"]["/space/runtime/compliance-suite"]["post"]
    schema_ref = suite_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    response_ref = suite_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]

    assert schema_ref.endswith("SpaceComplianceSuiteRequest")
    assert response_ref.endswith("SpaceComplianceSuiteResponse")


def test_space_individual_runtime_openapi_schema_present():
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    spec = openapi.json()

    treaty_path = spec["paths"]["/space/outer-space-treaty/runtime"]["post"]
    treaty_req = treaty_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    treaty_res = treaty_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert treaty_req.endswith("OuterSpaceTreatyRuntimeRequest")
    assert treaty_res.endswith("OuterSpaceTreatyRuntimeResult")

    itar_path = spec["paths"]["/space/itar/runtime"]["post"]
    itar_req = itar_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    itar_res = itar_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert itar_req.endswith("ItarRuntimeRequest")
    assert itar_res.endswith("ItarRuntimeResult")

    export_path = spec["paths"]["/space/export-control/runtime"]["post"]
    export_req = export_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    export_res = export_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert export_req.endswith("ExportControlRuntimeRequest")
    assert export_res.endswith("ExportControlRuntimeResult")


def test_space_legacy_endpoints_openapi_schema_present():
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    spec = openapi.json()

    treaty_path = spec["paths"]["/space/treaty/analyze"]["post"]
    treaty_req = treaty_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    treaty_res = treaty_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert treaty_req.endswith("TreatyAnalyzeRequest")
    assert treaty_res.endswith("TreatyAnalyzeResponse")

    habitat_path = spec["paths"]["/space/habitat/compliance"]["post"]
    habitat_req = habitat_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    habitat_res = habitat_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert habitat_req.endswith("HabitatComplianceRequest")
    assert habitat_res.endswith("HabitatComplianceResponse")

    mining_path = spec["paths"]["/space/mining/risk"]["post"]
    mining_req = mining_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    mining_res = mining_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert mining_req.endswith("MiningRiskRequest")
    assert mining_res.endswith("MiningRiskResponse")

    review_path = spec["paths"]["/space/mission/legal-review"]["post"]
    review_req = review_path["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    review_res = review_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert review_req.endswith("MissionLegalReviewRequest")
    assert review_res.endswith("MissionLegalReviewResponse")


def test_patent_and_research_openapi_schema_present():
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    spec = openapi.json()

    patent_register = spec["paths"]["/patents/register"]["post"]
    patent_register_req = patent_register["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    patent_register_res = patent_register["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert patent_register_req.endswith("RegisterPatentRequest")
    assert patent_register_res.endswith("RegisterPatentResponse")

    patent_license = spec["paths"]["/patents/license"]["post"]
    patent_license_req = patent_license["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    patent_license_res = patent_license["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert patent_license_req.endswith("CreateLicenseRequest")
    assert patent_license_res.endswith("CreateLicenseResponse")

    compliance_check = spec["paths"]["/research/compliance/check"]["post"]
    compliance_check_req = compliance_check["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    compliance_check_res = compliance_check["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert compliance_check_req.endswith("ComplianceCheckRequest")
    assert compliance_check_res.endswith("ComplianceCheckResponse")

    compliance_history = spec["paths"]["/research/compliance/history"]["get"]
    compliance_history_res = compliance_history["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert compliance_history_res.endswith("ComplianceHistoryResponse")


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
        ("space.outer_treaty.review_required", "liceu.events.space.outer_treaty.review_required"),
        ("space.itar.license_required", "liceu.events.space.itar.license_required"),
        ("space.export_control.escalated", "liceu.events.space.export_control.escalated"),
        ("space.runtime.compliance.review_required", "liceu.events.space.runtime.compliance.review_required"),
        ("oceanic.habitat.compliant", "liceu.events.oceanic.habitat.compliant"),
        ("ai.governance.alert", "liceu.events.ai.governance.alert"),
        ("quantum.runtime.risk.detected", "liceu.events.quantum.runtime.risk.detected"),
        ("civilization.impact.assessed", "liceu.events.civilization.impact.assessed"),
    ]
    for event_name, subject in cases:
        assert subject_for_event(event_name) == subject
