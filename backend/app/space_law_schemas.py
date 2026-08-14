from __future__ import annotations

from pydantic import BaseModel, Field


class SpaceRuntimeBaseRequest(BaseModel):
    mission_id: str | None = None
    involves_dual_use_tech: bool = False
    includes_us_munitions_list_item: bool = False
    includes_us_origin_hardware: bool = False
    has_reexport: bool = False
    destination_country: str = Field(default="undisclosed", min_length=2)
    end_user_verified: bool = True


class OuterSpaceTreatyRuntimeRequest(SpaceRuntimeBaseRequest):
    pass


class ItarRuntimeRequest(SpaceRuntimeBaseRequest):
    pass


class ExportControlRuntimeRequest(SpaceRuntimeBaseRequest):
    pass


class SpaceComplianceSuiteRequest(SpaceRuntimeBaseRequest):
    mission_id: str = Field(..., min_length=3)


class OuterSpaceTreatyRuntimeResult(BaseModel):
    mission_id: str | None = None
    runtime: str
    peaceful_use: bool
    non_appropriation: bool
    status: str
    evaluated_at: str


class ItarRuntimeResult(BaseModel):
    mission_id: str | None = None
    runtime: str
    usml_item_detected: bool
    reexport_detected: bool
    license_required: bool
    destination_country: str
    status: str
    evaluated_at: str


class ExportControlRuntimeResult(BaseModel):
    mission_id: str | None = None
    runtime: str
    eccn_review_required: bool
    reexport_detected: bool
    end_user_verified: bool
    status: str
    evaluated_at: str


class SpaceComplianceSuiteControls(BaseModel):
    outer_space_treaty: OuterSpaceTreatyRuntimeResult
    itar: ItarRuntimeResult
    export_control: ExportControlRuntimeResult


class SpaceComplianceSuiteResponse(BaseModel):
    mission_id: str | None = None
    runtime: str
    requires_review: bool
    controls: SpaceComplianceSuiteControls
    evaluated_at: str


class SpaceComplianceSuiteSchemaResponse(BaseModel):
    endpoint: str
    method: str
    description: str
    request_schema: dict[str, str]
    example_request: dict
    example_response: SpaceComplianceSuiteResponse


class TreatyAnalyzeRequest(BaseModel):
    treaty_id: str | None = None
    jurisdiction: str = Field(default="orbit", min_length=2)
    compliant: bool = True


class TreatyAnalyzeResponse(BaseModel):
    treaty_id: str | None = None
    jurisdiction: str
    compliant: bool
    analyzed_at: str


class HabitatComplianceRequest(BaseModel):
    habitat_id: str | None = None
    zone: str = Field(default="lunar", min_length=2)
    status: str = Field(default="compliant", min_length=2)


class HabitatComplianceResponse(BaseModel):
    habitat_id: str | None = None
    zone: str
    status: str


class MiningRiskRequest(BaseModel):
    mission_id: str | None = None
    risk_level: str = Field(default="medium", min_length=2)
    recommendation: str = Field(default="additional_legal_review", min_length=2)


class MiningRiskResponse(BaseModel):
    mission_id: str | None = None
    risk_level: str
    recommendation: str


class MissionLegalReviewRequest(BaseModel):
    mission_id: str | None = None
    approved: bool = True


class MissionLegalReviewResponse(BaseModel):
    mission_id: str | None = None
    approved: bool
    reviewed_at: str