from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.services.legal_store import legal_core_store


client = TestClient(app)


def test_legal_contract_generate_endpoint_supports_required_templates():
    response = client.post(
        "/legal/contract/generate",
        json={
            "contract_type": "MSA",
            "parties": ["ACME", "ORBITAL OPS"],
            "objective": "Master legal governance terms",
            "jurisdiction": "BR",
            "context": {"sector": "infrastructure"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generated"] is True
    assert payload["contract_type"] == "MSA"
    assert "contract_id" in payload


def test_legal_compliance_check_governance_payload():
    response = client.post(
        "/legal/compliance/check",
        json={
            "jurisdiction": "BR",
            "contract_type": "PPP",
            "obligations": ["anti_corruption"],
            "controls": {
                "audit_trail": True,
                "data_protection": True,
                "dispute_clause": True,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "compliance" in payload
    assert "regulatory" in payload
    assert payload["compliance"]["status"] in {"approved", "attention"}


def test_legal_assurance_unifies_contract_compliance_liability_and_insurance():
    response = client.post(
        "/legal/assurance",
        json={
            "contract_type": "MSA",
            "parties": ["ACME", "SUPPLIER"],
            "objective": "Operacao de servicos",
            "jurisdiction": "BR",
            "obligations": ["audit_trail"],
            "controls": {"audit_trail": True, "data_protection": True, "dispute_clause": True},
            "liability": {"status": "high"},
            "insurance": {"covered": False},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["contract"]["generated"] is True
    assert payload["compliance"]["compliance"]["status"] == "approved"
    assert payload["decision"] == "pending"
    assert "required_actions" in payload


def test_legal_compliance_check_legacy_payload_compatibility():
    response = client.post(
        "/legal/compliance/check",
        json={
            "user_id": "u-1",
            "role": "LEGAL_ADMIN",
            "action": "create_deal",
            "module": "sales",
            "entity_id": "en-1",
            "property_documents_ok": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "allowed" in payload
    assert "checks" in payload


def test_legal_risk_analyze_endpoint():
    response = client.post(
        "/legal/risk/analyze",
        json={
            "jurisdiction": "EU",
            "contract_type": "BOT",
            "obligations": ["audit_trail"],
            "controls": {
                "audit_trail": True,
                "data_protection": False,
            },
            "claims": [
                {"category": "delay", "severity": "high", "amount": 150000.0},
                {"category": "quality", "severity": "medium", "amount": 25000.0},
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "risk" in payload
    assert payload["risk"]["risk_level"] in {"low", "medium", "high"}
    assert payload["claims"]["total_claims"] == 2


def test_legal_implications_endpoint_returns_requested_contract():
    response = client.post(
        "/legal/implications",
        json={
            "affected_contracts": ["CTR-1"],
            "obligations": ["notice", "mitigation"],
            "regulatory_risk": "high",
            "liability": True,
            "force_majeure": True,
            "insurance": False,
            "compliance": False,
            "licensing": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"legal_status", "risk_level", "required_actions"}
    assert payload["legal_status"] == "blocked"
    assert payload["risk_level"] == "critical"
    assert payload["required_actions"]


def test_legal_risk_analyze_critical_controls_missing_results_in_high_risk():
    response = client.post(
        "/legal/risk/analyze",
        json={
            "jurisdiction": "GLOBAL",
            "contract_type": "MSA",
            "obligations": [
                "data_protection",
                "sanctions_screening",
                "audit_trail",
                "incident_response",
                "dispute_clause",
            ],
            "controls": {
                "data_protection": False,
                "sanctions_screening": False,
                "audit_trail": False,
                "incident_response": False,
                "dispute_clause": False,
            },
            "claims": [
                {"category": "cross_border_sanctions", "severity": "high", "amount": 1000000.0},
                {"category": "privacy_breach", "severity": "high", "amount": 500000.0},
                {"category": "contract_nullity", "severity": "high", "amount": 250000.0},
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["compliance"]["status"] == "attention"
    assert len(payload["compliance"]["missing_controls"]) == 5
    assert payload["risk"]["risk_level"] == "high"
    assert payload["risk"]["risk_score"] == 100


def test_legal_worldwide_compliance_simulation_critical_scenario():
    response = client.post(
        "/legal/compliance/worldwide-simulation",
        json={"scenario": "critical"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["simulation"] == "worldwide_compliance"
    assert payload["scenario"] == "critical"
    assert payload["compliance"]["status"] == "attention"
    assert payload["risk"]["risk_level"] == "high"
    assert payload["risk"]["risk_score"] == 100
    assert payload["claims"]["high_severity_claims"] == 3


def test_legal_worldwide_compliance_simulation_baseline_scenario():
    response = client.post(
        "/legal/compliance/worldwide-simulation",
        json={"scenario": "baseline"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["simulation"] == "worldwide_compliance"
    assert payload["scenario"] == "baseline"
    assert payload["compliance"]["status"] == "approved"
    assert payload["risk"]["risk_level"] == "low"
    assert payload["risk"]["risk_score"] == 40
    assert payload["claims"]["high_severity_claims"] == 1


def test_legal_worldwide_compliance_simulation_invalid_scenario_returns_422():
    response = client.post(
        "/legal/compliance/worldwide-simulation",
        json={"scenario": "unknown"},
    )

    assert response.status_code == 422


def test_legal_state_endpoint_contains_objective_capabilities_contracts():
    response = client.get("/legal/state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["objective"] == "Governanca juridica"
    assert "contract_generation_runtime.py" in payload["capabilities"]
    assert payload["contracts"] == ["MSA", "SoW", "NDA", "EPC", "PPP", "BOT", "Concessao"]


def test_legal_wave_43_endpoint_contains_expected_tracks():
    response = client.get("/legal/waves/43")

    assert response.status_code == 200
    payload = response.json()
    assert payload["wave"] == 43
    assert payload["program"] == "JURIDICOTECH"
    assert payload["status"] == "active"
    assert "legal_state" in payload["tracks"]
    assert "contracts" in payload["tracks"]
    assert "regulation" in payload["tracks"]
    assert "ip" in payload["tracks"]
    assert "compliance" in payload["tracks"]


def test_legal_wave_59_evaluates_all_legal_exposure_tracks():
    manifest = client.get("/legal/waves/59")
    assert manifest.status_code == 200
    assert set(manifest.json()["tracks"]) == {
        "contracts",
        "international_obligations",
        "regulatory_exposure",
        "liability",
        "insurance",
        "ip",
        "data_rights",
        "cross_border_compliance",
    }

    response = client.post(
        "/legal/waves/59/evaluate",
        json={track: True for track in manifest.json()["tracks"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "approved"
    assert payload["score"] == 100.0
    assert payload["gaps"] == []


def test_legal_wave_70_returns_legal_decision_id_for_global_legal_validation():
    manifest = client.get("/legal/waves/70")
    assert manifest.status_code == 200
    tracks = manifest.json()["tracks"]
    assert set(tracks) == {
        "contracts",
        "compliance",
        "liability",
        "insurance",
        "regulatory_exposure",
        "ip",
        "data_rights",
        "cross_border_obligations",
    }

    response = client.post(
        "/legal/waves/70/validate",
        json={track: True for track in tracks},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["legal_decision_id"].startswith("LDEC-")
    assert payload["status"] == "approved"
    assert payload["score"] == 100.0
    assert payload["gaps"] == []


def test_legal_wave_84_consumes_cea_lineage_and_is_idempotent():
    w83 = {
        "source_event_id": f"evt-cea-{uuid4().hex}",
        "trace_id": "trace-cea-001",
        "decision_id": "decision-cea-001",
        "governance_decision_id": "gov-cea-001",
        "execution_id": "exec-cea-001",
        "infrastructure_change_ids": ["infra-cea-001"],
        "supplier_analysis_id": "supplier-cea-001",
        "procurement_plan_id": "procurement-cea-001",
        "economic_impact_id": "economic-cea-001",
        "financial_exposure_id": "exposure-cea-001",
    }
    audit_events = legal_core_store.load("audit_trail", [])
    audit_events.append(
        {
            "event_id": w83["source_event_id"],
            "wave": 83,
            "payload": {
                **w83,
                "wave_lineage": [79, 80, 81, 82, 83],
                "validations": {
                    "replay": True,
                    "idempotency": True,
                    "rollback": True,
                    "recovery": True,
                    "audit": True,
                },
            },
        }
    )
    legal_core_store.save("audit_trail", audit_events)

    first = client.post(
        "/legal/waves/84/evaluate",
        json={
            **w83,
            "legal_checks": {
                "contract_valid": True,
                "compliance_valid": True,
                "regulatory_valid": True,
                "liability_valid": True,
                "insurance_valid": True,
            },
        },
    )
    second = client.post(
        "/legal/waves/84/evaluate",
        json={
            **w83,
            "legal_checks": {
                "contract_valid": True,
                "compliance_valid": True,
                "regulatory_valid": True,
                "liability_valid": True,
                "insurance_valid": True,
            },
        },
    )

    assert first.status_code == second.status_code == 200
    payload = first.json()
    assert payload == second.json()
    assert payload["legal_assessment_id"]
    assert payload["financial_exposure_id"] == w83["financial_exposure_id"]
    assert all(payload[field] is True for field in (
        "contract_valid", "lineage_valid", "compliance_valid", "regulatory_valid",
        "liability_valid", "insurance_valid", "replay_valid", "idempotency_valid",
        "rollback_valid", "recovery_valid", "audit_valid",
    ))
    assert payload["status"] == "PASS"
    assert any(
        event.get("wave") == 84
        and event.get("source_event_id") == w83["source_event_id"]
        and event.get("trace_id") == w83["trace_id"]
        and event.get("legal_assessment_id") == payload["legal_assessment_id"]
        for event in legal_core_store.load("audit_trail", [])
    )


def test_legal_wave_84_rejects_disconnected_lineage():
    payload = {
        "source_event_id": "evt-cea-002",
        "trace_id": "trace-cea-002",
        "decision_id": "decision-cea-002",
        "governance_decision_id": "gov-cea-002",
        "execution_id": "exec-cea-002",
        "infrastructure_change_ids": ["infra-cea-002"],
        "supplier_analysis_id": "supplier-cea-002",
        "procurement_plan_id": "procurement-cea-002",
        "economic_impact_id": "economic-cea-002",
        "financial_exposure_id": "exposure-cea-002",
    }
    audit_events = legal_core_store.load("audit_trail", [])
    audit_events.append(
        {
            "event_id": payload["source_event_id"],
            "wave": 83,
            "payload": {**payload, "wave_lineage": [79, 83]},
        }
    )
    legal_core_store.save("audit_trail", audit_events)

    response = client.post("/legal/waves/84/evaluate", json=payload)

    assert response.status_code == 409
    assert "W79-W83" in response.json()["detail"]
