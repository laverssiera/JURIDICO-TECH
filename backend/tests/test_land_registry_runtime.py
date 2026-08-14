from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.routers import land_registry_runtime


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_land_registry() -> None:
    land_registry_runtime._registry.clear()


def test_register_land_record_and_fetch() -> None:
    register_response = client.post(
        "/land/registry/register",
        json={
            "parcel_id": "PARCEL-001",
            "owner_name": "Sovereign Holdings",
            "jurisdiction": "BR",
            "zoning_classification": "industrial",
            "environmental_restrictions": ["wetland-buffer"],
            "compliance_flags": {
                "title_clear": True,
                "tax_clearance": True,
            },
            "metadata": {"municipality": "Sao Paulo"},
        },
    )

    assert register_response.status_code == 200
    registered = register_response.json()
    assert registered["status"] == "registered"
    assert registered["parcel_id"] == "PARCEL-001"
    assert registered["compliance_score"] == 90

    record_id = registered["record_id"]
    get_response = client.get(f"/land/registry/{record_id}")

    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["found"] is True
    assert payload["record"]["owner_name"] == "Sovereign Holdings"
    assert payload["record"]["jurisdiction"] == "BR"


def test_transfer_land_record_updates_owner_and_history() -> None:
    created = client.post(
        "/land/registry/register",
        json={
            "parcel_id": "PARCEL-002",
            "owner_name": "Initial Owner",
            "jurisdiction": "BR",
            "zoning_classification": "residential",
            "environmental_restrictions": [],
            "compliance_flags": {"title_clear": True},
        },
    ).json()

    transfer_response = client.post(
        f"/land/registry/{created['record_id']}/transfer",
        json={
            "new_owner_name": "Next Owner",
            "actor_id": "legal-admin-01",
            "reason": "asset_reorganization",
        },
    )

    assert transfer_response.status_code == 200
    transfer_payload = transfer_response.json()
    assert transfer_payload["transferred"] is True
    assert transfer_payload["previous_owner"] == "Initial Owner"
    assert transfer_payload["new_owner"] == "Next Owner"

    record_response = client.get(f"/land/registry/{created['record_id']}")
    record_payload = record_response.json()
    assert record_payload["record"]["owner_name"] == "Next Owner"
    assert len(record_payload["record"]["history"]) == 2
    assert record_payload["record"]["history"][-1]["event"] == "ownership_transferred"


def test_not_found_paths_are_stable() -> None:
    get_response = client.get("/land/registry/land-does-not-exist")
    transfer_response = client.post(
        "/land/registry/land-does-not-exist/transfer",
        json={
            "new_owner_name": "Another Owner",
            "actor_id": "legal-admin-01",
            "reason": "correction",
        },
    )

    assert get_response.status_code == 200
    assert get_response.json() == {
        "record_id": "land-does-not-exist",
        "found": False,
        "reason": "record_not_found",
    }

    assert transfer_response.status_code == 200
    assert transfer_response.json() == {
        "record_id": "land-does-not-exist",
        "transferred": False,
        "reason": "record_not_found",
    }


def test_runtime_status_aggregates_registry_metrics() -> None:
    client.post(
        "/land/registry/register",
        json={
            "parcel_id": "PARCEL-003",
            "owner_name": "Owner A",
            "jurisdiction": "BR",
            "zoning_classification": "commercial",
            "environmental_restrictions": [],
            "compliance_flags": {
                "title_clear": True,
                "tax_clearance": True,
            },
        },
    )
    client.post(
        "/land/registry/register",
        json={
            "parcel_id": "PARCEL-004",
            "owner_name": "Owner B",
            "jurisdiction": "PT",
            "zoning_classification": "industrial",
            "environmental_restrictions": ["coastal-limit"],
            "compliance_flags": {
                "title_clear": True,
                "tax_clearance": False,
            },
        },
    )

    response = client.get("/land/registry/runtime-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime"] == "land_registry_runtime"
    assert payload["status"] == "healthy"
    assert payload["records_total"] == 2
    assert payload["records_active"] == 2
    assert payload["average_compliance_score"] == 87.5
    assert payload["jurisdictions"] == ["BR", "PT"]
