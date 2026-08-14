from runtime.legal.governance.international_compliance_runtime import InternationalComplianceRuntime


def test_international_compliance_runtime_approves_when_controls_are_complete():
    runtime = InternationalComplianceRuntime()

    result = runtime.assess(
        {
            "jurisdiction": "interplanetary",
            "frameworks": ["UNCITRAL", "OST", "GDPR"],
            "controls": {
                "audit_trail": True,
                "cross_border_data_transfer": True,
                "export_control_screening": True,
            },
        }
    )

    assert result["international_compliance_validation"] is True
    assert result["status"] == "approved"
    assert result["score"] == 100.0


def test_international_compliance_runtime_metrics_track_failed_assessment():
    runtime = InternationalComplianceRuntime()

    runtime.assess(
        {
            "jurisdiction": "interplanetary",
            "frameworks": ["UNCITRAL"],
            "controls": {
                "audit_trail": False,
                "cross_border_data_transfer": True,
            },
        }
    )

    metrics = runtime.metrics()
    assert metrics["total_assessments"] == 1
    assert metrics["approved_assessments"] == 0
    assert metrics["international_compliance_ratio"] == 0.0
