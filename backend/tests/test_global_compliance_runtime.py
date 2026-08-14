from runtime.legal.governance.global_compliance_runtime import GlobalComplianceRuntime


def test_global_compliance_runtime_approves_when_required_framework_controls_are_present():
    runtime = GlobalComplianceRuntime()

    result = runtime.validate_contract(
        {
            "jurisdiction": "global",
            "contract_type": "msa",
            "frameworks": ["LGPD", "GDPR", "Space Law", "Maritime Law", "International Treaties"],
            "controls": {
                "data_protection": True,
                "consent_management": True,
                "cross_border_transfer": True,
                "dpo_designation": True,
                "orbital_operations_authorization": True,
                "space_assets_registry": True,
                "collision_avoidance": True,
                "maritime_cargo_documentation": True,
                "marine_environment_compliance": True,
                "incident_reporting": True,
                "treaty_obligations": True,
                "sovereignty_clauses": True,
                "dispute_resolution": True,
            },
        }
    )

    assert result["global_compliance_validation"] is True
    assert result["status"] == "approved"
    assert result["score"] == 100.0
    assert result["missing_controls"] == []


def test_global_compliance_runtime_metrics_track_failed_assessments():
    runtime = GlobalComplianceRuntime()

    runtime.validate_contract(
        {
            "jurisdiction": "global",
            "contract_type": "msa",
            "frameworks": ["LGPD", "GDPR"],
            "controls": {
                "data_protection": True,
                "consent_management": False,
                "cross_border_transfer": True,
                "dpo_designation": False,
            },
        }
    )

    metrics = runtime.metrics()
    assert metrics["total_validations"] == 1
    assert metrics["approved_validations"] == 0
    assert metrics["global_compliance_ratio"] == 0.0
