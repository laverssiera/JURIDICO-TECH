from __future__ import annotations

from datetime import datetime, UTC

from fastapi import APIRouter

from app.domain_schemas import (
    ExportControlRuntimeRequest,
    ExportControlRuntimeResult,
    HabitatComplianceRequest,
    HabitatComplianceResponse,
    ItarRuntimeRequest,
    ItarRuntimeResult,
    MiningRiskRequest,
    MiningRiskResponse,
    MissionLegalReviewRequest,
    MissionLegalReviewResponse,
    OuterSpaceTreatyRuntimeRequest,
    OuterSpaceTreatyRuntimeResult,
    SpaceComplianceSuiteRequest,
    SpaceComplianceSuiteResponse,
    SpaceComplianceSuiteSchemaResponse,
    TreatyAnalyzeRequest,
    TreatyAnalyzeResponse,
)
from app.integration.event_bus import event_bus

router = APIRouter()


@router.post("/treaty/analyze", response_model=TreatyAnalyzeResponse)
def analyze_treaty(payload: TreatyAnalyzeRequest) -> TreatyAnalyzeResponse:
    result = {
        "treaty_id": payload.treaty_id,
        "jurisdiction": payload.jurisdiction,
        "compliant": payload.compliant,
        "analyzed_at": datetime.now(UTC).isoformat(),
    }
    if not result["compliant"]:
        event_bus.publish("space.treaty.violation", result)
    else:
        event_bus.publish("planetary.treaty.registered", result)
    return TreatyAnalyzeResponse.model_validate(result)


@router.post("/habitat/compliance", response_model=HabitatComplianceResponse)
def habitat_compliance(payload: HabitatComplianceRequest) -> HabitatComplianceResponse:
    return HabitatComplianceResponse(
        habitat_id=payload.habitat_id,
        zone=payload.zone,
        status=payload.status,
    )


@router.post("/mining/risk", response_model=MiningRiskResponse)
def mining_risk(payload: MiningRiskRequest) -> MiningRiskResponse:
    return MiningRiskResponse(
        mission_id=payload.mission_id,
        risk_level=payload.risk_level,
        recommendation=payload.recommendation,
    )


@router.post("/mission/legal-review", response_model=MissionLegalReviewResponse)
def mission_legal_review(payload: MissionLegalReviewRequest) -> MissionLegalReviewResponse:
    review = {
        "mission_id": payload.mission_id,
        "approved": payload.approved,
        "reviewed_at": datetime.now(UTC).isoformat(),
    }
    if review["approved"]:
        event_bus.publish("space.mission.legal.approved", review)
    return MissionLegalReviewResponse.model_validate(review)


@router.post("/outer-space-treaty/runtime", response_model=OuterSpaceTreatyRuntimeResult)
def outer_space_treaty_runtime(payload: OuterSpaceTreatyRuntimeRequest) -> OuterSpaceTreatyRuntimeResult:
    dual_use = payload.involves_dual_use_tech
    result = {
        "mission_id": payload.mission_id,
        "runtime": "outer-space-treaty",
        "peaceful_use": not dual_use,
        "non_appropriation": True,
        "status": "review-required" if dual_use else "compliant",
        "evaluated_at": datetime.now(UTC).isoformat(),
    }
    if result["status"] != "compliant":
        event_bus.publish("space.outer_treaty.review_required", result)
    return OuterSpaceTreatyRuntimeResult.model_validate(result)


@router.post("/itar/runtime", response_model=ItarRuntimeResult)
def itar_runtime(payload: ItarRuntimeRequest) -> ItarRuntimeResult:
    usml_item = payload.includes_us_munitions_list_item
    reexport = payload.has_reexport
    license_required = usml_item or reexport
    result = {
        "mission_id": payload.mission_id,
        "runtime": "itar",
        "usml_item_detected": usml_item,
        "reexport_detected": reexport,
        "license_required": license_required,
        "destination_country": payload.destination_country,
        "status": "license-required" if license_required else "compliant",
        "evaluated_at": datetime.now(UTC).isoformat(),
    }
    if license_required:
        event_bus.publish("space.itar.license_required", result)
    return ItarRuntimeResult.model_validate(result)


@router.post("/export-control/runtime", response_model=ExportControlRuntimeResult)
def export_control_runtime(payload: ExportControlRuntimeRequest) -> ExportControlRuntimeResult:
    reexport = payload.has_reexport
    us_origin_hardware = payload.includes_us_origin_hardware
    end_user_verified = payload.end_user_verified
    escalation_required = (us_origin_hardware and reexport) or not end_user_verified
    result = {
        "mission_id": payload.mission_id,
        "runtime": "export-control",
        "eccn_review_required": us_origin_hardware,
        "reexport_detected": reexport,
        "end_user_verified": end_user_verified,
        "status": "escalation-required" if escalation_required else "compliant",
        "evaluated_at": datetime.now(UTC).isoformat(),
    }
    if escalation_required:
        event_bus.publish("space.export_control.escalated", result)
    return ExportControlRuntimeResult.model_validate(result)


@router.post("/runtime/compliance-suite", response_model=SpaceComplianceSuiteResponse)
def compliance_suite_runtime(payload: SpaceComplianceSuiteRequest) -> SpaceComplianceSuiteResponse:
    outer_treaty = outer_space_treaty_runtime(OuterSpaceTreatyRuntimeRequest.model_validate(payload.model_dump()))
    itar = itar_runtime(ItarRuntimeRequest.model_validate(payload.model_dump()))
    export_control = export_control_runtime(ExportControlRuntimeRequest.model_validate(payload.model_dump()))

    requires_review = (
        outer_treaty.status != "compliant"
        or itar.status != "compliant"
        or export_control.status != "compliant"
    )

    suite = {
        "mission_id": payload.mission_id,
        "runtime": "space-compliance-suite",
        "requires_review": requires_review,
        "controls": {
            "outer_space_treaty": outer_treaty.model_dump(),
            "itar": itar.model_dump(),
            "export_control": export_control.model_dump(),
        },
        "evaluated_at": datetime.now(UTC).isoformat(),
    }

    if requires_review:
        event_bus.publish("space.runtime.compliance.review_required", suite)

    return SpaceComplianceSuiteResponse.model_validate(suite)


@router.get("/runtime/compliance-suite/schema", response_model=SpaceComplianceSuiteSchemaResponse)
def compliance_suite_runtime_schema() -> SpaceComplianceSuiteSchemaResponse:
    example_payload = {
        "mission_id": "MIS-900",
        "involves_dual_use_tech": False,
        "includes_us_munitions_list_item": False,
        "includes_us_origin_hardware": False,
        "has_reexport": False,
        "destination_country": "BR",
        "end_user_verified": True,
    }

    return SpaceComplianceSuiteSchemaResponse(
        endpoint="/space/runtime/compliance-suite",
        method="POST",
        description="Consolidated runtime for Outer Space Treaty, ITAR, and Export Control checks.",
        request_schema={
            "mission_id": "string",
            "involves_dual_use_tech": "boolean",
            "includes_us_munitions_list_item": "boolean",
            "includes_us_origin_hardware": "boolean",
            "has_reexport": "boolean",
            "destination_country": "string",
            "end_user_verified": "boolean",
        },
        example_request=example_payload,
        example_response=compliance_suite_runtime(SpaceComplianceSuiteRequest.model_validate(example_payload)),
    )
