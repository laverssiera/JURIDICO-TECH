from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from fastapi import APIRouter

from app.domain_schemas import (
    ComplianceApproveData,
    ComplianceApproveRequest,
    ComplianceApproveResponse,
    ComplianceBlockData,
    ComplianceBlockRequest,
    ComplianceBlockResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ComplianceHistoryResponse,
    ComplianceReviewRecord,
)
from app.integration.event_bus import event_bus

router = APIRouter()
_reviews: list[dict] = []


@router.post("/compliance/check", response_model=ComplianceCheckResponse)
def compliance_check(payload: ComplianceCheckRequest) -> ComplianceCheckResponse:
    result = {
        "id": str(uuid4()),
        "research_type": payload.research_type,
        "risk_level": payload.risk_level,
        "jurisdiction_scope": payload.jurisdiction_scope,
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }
    _reviews.append(result)
    return ComplianceCheckResponse(status="checked", data=ComplianceReviewRecord.model_validate(result))


@router.post("/compliance/approve", response_model=ComplianceApproveResponse)
def compliance_approve(payload: ComplianceApproveRequest) -> ComplianceApproveResponse:
    event = {
        "review_id": payload.review_id,
        "approved_by": payload.approved_by,
        "approved_at": datetime.now(UTC).isoformat(),
    }
    event_bus.publish("research.compliance.approved", event)
    return ComplianceApproveResponse(status="approved", data=ComplianceApproveData.model_validate(event))


@router.post("/compliance/block", response_model=ComplianceBlockResponse)
def compliance_block(payload: ComplianceBlockRequest) -> ComplianceBlockResponse:
    event = {
        "review_id": payload.review_id,
        "blocked_by": payload.blocked_by,
        "reason": payload.reason,
        "blocked_at": datetime.now(UTC).isoformat(),
    }
    event_bus.publish("research.compliance.blocked", event)
    return ComplianceBlockResponse(status="blocked", data=ComplianceBlockData.model_validate(event))


@router.get("/compliance/history", response_model=ComplianceHistoryResponse)
def compliance_history() -> ComplianceHistoryResponse:
    return ComplianceHistoryResponse(items=[ComplianceReviewRecord.model_validate(item) for item in _reviews])
