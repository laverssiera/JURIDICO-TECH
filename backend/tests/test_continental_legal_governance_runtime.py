from runtime.legal.governance.continental_legal_governance_runtime import (
    ContinentalLegalGovernanceRuntime,
)


def test_continental_state_tracks_route_and_operational_domains():
    state = ContinentalLegalGovernanceRuntime().build_state(
        countries=["BR", "PT", "ES"],
        contracts=[{"contract_id": "contract-1", "contract_type": "msa"}],
        assets=[{"asset_id": "patent-1", "type": "patent", "protected_in": ["BR", "PT"]}],
        data=[{"data_set_id": "customers", "classification": "personal"}],
        investments=[{"investment_id": "fund-1", "country": "PT"}],
        suppliers=[{"supplier_id": "supplier-1", "country": "ES"}],
        infrastructure=[{"asset_id": "datacenter-1", "country": "PT"}],
        controls={"cross_border_transfer": True},
        operation_id="operation-1",
    )

    assert state["legal_state_id"] == "operation-1"
    assert [item["country"] for item in state["route"]] == ["BR", "PT", "ES"]
    assert state["contracts"]["cross_border_contracts"] == 1
    assert state["intellectual_property"]["protection_gaps"]
    assert state["data"][0]["classification"] == "personal"
    assert state["investments"] and state["suppliers"] and state["infrastructure"]