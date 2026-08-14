from __future__ import annotations

from pydantic import BaseModel, Field


class ComplianceReviewRecord(BaseModel):
    id: str
    research_type: str
    risk_level: str
    jurisdiction_scope: str
    status: str
    created_at: str


class ComplianceCheckRequest(BaseModel):
    research_type: str = Field(default="general", min_length=2)
    risk_level: str = Field(default="medium", min_length=2)
    jurisdiction_scope: str = Field(default="earth", min_length=2)


class ComplianceCheckResponse(BaseModel):
    status: str
    data: ComplianceReviewRecord


class ComplianceApproveRequest(BaseModel):
    review_id: str | None = None
    approved_by: str | None = None


class ComplianceApproveData(BaseModel):
    review_id: str | None = None
    approved_by: str | None = None
    approved_at: str


class ComplianceApproveResponse(BaseModel):
    status: str
    data: ComplianceApproveData


class ComplianceBlockRequest(BaseModel):
    review_id: str | None = None
    blocked_by: str | None = None
    reason: str = ""


class ComplianceBlockData(BaseModel):
    review_id: str | None = None
    blocked_by: str | None = None
    reason: str
    blocked_at: str


class ComplianceBlockResponse(BaseModel):
    status: str
    data: ComplianceBlockData


class ComplianceHistoryResponse(BaseModel):
    items: list[ComplianceReviewRecord]