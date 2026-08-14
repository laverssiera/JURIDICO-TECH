from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter()
_registry: dict[str, dict[str, Any]] = {}


class LandRegistryRecordRequest(BaseModel):
    parcel_id: str = Field(..., min_length=3)
    owner_name: str = Field(..., min_length=3)
    jurisdiction: str = Field(default="BR", min_length=2)
    zoning_classification: str = Field(default="residential", min_length=3)
    environmental_restrictions: list[str] = Field(default_factory=list)
    compliance_flags: dict[str, bool] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LandRegistryTransferRequest(BaseModel):
    new_owner_name: str = Field(..., min_length=3)
    actor_id: str = Field(..., min_length=3)
    reason: str = Field(default="ownership_transfer", min_length=3)


@router.post("/land/registry/register")
def register_land_record(request: LandRegistryRecordRequest) -> dict[str, Any]:
    record_id = f"land-{uuid4().hex[:12]}"
    now = datetime.now(UTC).isoformat()

    compliance_score = 100
    if request.environmental_restrictions:
        compliance_score -= 10
    if any(not value for value in request.compliance_flags.values()):
        compliance_score -= 15

    _registry[record_id] = {
        "record_id": record_id,
        "parcel_id": request.parcel_id,
        "owner_name": request.owner_name,
        "jurisdiction": request.jurisdiction,
        "zoning_classification": request.zoning_classification,
        "environmental_restrictions": request.environmental_restrictions,
        "compliance_flags": request.compliance_flags,
        "metadata": request.metadata,
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "compliance_score": max(compliance_score, 0),
        "history": [
            {
                "event": "record_created",
                "at": now,
                "details": {"owner_name": request.owner_name},
            }
        ],
    }

    return {
        "record_id": record_id,
        "parcel_id": request.parcel_id,
        "status": "registered",
        "compliance_score": _registry[record_id]["compliance_score"],
        "registered_at": now,
    }


@router.post("/land/registry/{record_id}/transfer")
def transfer_land_record(record_id: str, request: LandRegistryTransferRequest) -> dict[str, Any]:
    record = _registry.get(record_id)
    if not record:
        return {
            "record_id": record_id,
            "transferred": False,
            "reason": "record_not_found",
        }

    previous_owner = record["owner_name"]
    now = datetime.now(UTC).isoformat()

    record["owner_name"] = request.new_owner_name
    record["updated_at"] = now
    record["history"].append(
        {
            "event": "ownership_transferred",
            "at": now,
            "details": {
                "from": previous_owner,
                "to": request.new_owner_name,
                "actor_id": request.actor_id,
                "reason": request.reason,
            },
        }
    )

    return {
        "record_id": record_id,
        "transferred": True,
        "previous_owner": previous_owner,
        "new_owner": request.new_owner_name,
        "updated_at": now,
    }


@router.get("/land/registry/runtime-status")
def land_registry_runtime_status() -> dict[str, Any]:
    active_records = sum(1 for item in _registry.values() if item["status"] == "active")
    avg_score = (
        round(sum(item["compliance_score"] for item in _registry.values()) / len(_registry), 2)
        if _registry
        else 0.0
    )

    return {
        "runtime": "land_registry_runtime",
        "status": "healthy",
        "records_total": len(_registry),
        "records_active": active_records,
        "average_compliance_score": avg_score,
        "jurisdictions": sorted({item["jurisdiction"] for item in _registry.values()}),
    }


@router.get("/land/registry/{record_id}")
def get_land_record(record_id: str) -> dict[str, Any]:
    record = _registry.get(record_id)
    if not record:
        return {
            "record_id": record_id,
            "found": False,
            "reason": "record_not_found",
        }

    return {"found": True, "record": record}
