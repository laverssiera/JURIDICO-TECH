from runtime.legal.governance.earth_legal_governance_runtime import EarthLegalGovernanceRuntime


def test_earth_governance_runtime_returns_compliant_when_all_domains_are_clear():
    runtime = EarthLegalGovernanceRuntime()

    result = runtime.validate(
        {
            "domains": {
                "environmental": True,
                "construction": True,
                "land": True,
                "water": True,
                "energy": True,
                "labor": True,
                "procurement": True,
                "data": True,
                "cross-border": True,
            }
        }
    )

    assert result["overall_status"] == "COMPLIANT"
    assert result["domain_results"]["environmental"] == "COMPLIANT"
    assert result["domain_results"]["cross-border"] == "COMPLIANT"


def test_earth_governance_runtime_returns_conditional_for_non_critical_gaps():
    runtime = EarthLegalGovernanceRuntime()

    result = runtime.validate(
        {
            "domains": {
                "environmental": True,
                "construction": False,
                "land": True,
                "water": True,
                "energy": True,
                "labor": True,
                "procurement": True,
                "data": True,
                "cross-border": True,
            }
        }
    )

    assert result["overall_status"] == "CONDITIONAL"
    assert result["domain_results"]["construction"] == "CONDITIONAL"


def test_earth_governance_runtime_returns_blocked_for_critical_domain_failure():
    runtime = EarthLegalGovernanceRuntime()

    result = runtime.validate(
        {
            "domains": {
                "environmental": True,
                "construction": True,
                "land": True,
                "water": True,
                "energy": True,
                "labor": False,
                "procurement": True,
                "data": True,
                "cross-border": True,
            }
        }
    )

    assert result["overall_status"] == "BLOCKED"
    assert result["domain_results"]["labor"] == "BLOCKED"
