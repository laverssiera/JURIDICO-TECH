from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.domain_schemas import (
    AnalyzeNoveltyRequest,
    AnalyzeNoveltyResponse,
    CreateLicenseRequest,
    CreateLicenseResponse,
    PatentRecord,
    RegisterPatentRequest,
    RegisterPatentResponse,
    ValidatePriorArtRequest,
    ValidatePriorArtResponse,
)
from app.integration.event_bus import event_bus

router = APIRouter()
_patents: dict[str, dict] = {}


@router.post("/register", response_model=RegisterPatentResponse)
def register_patent(payload: RegisterPatentRequest) -> RegisterPatentResponse:
    title = payload.title
    if not title:
        raise HTTPException(status_code=422, detail="Campo obrigatório: title")

    patent = {
        "id": str(uuid4()),
        "title": title,
        "category": payload.category,
        "status": "draft",
        "novelty_score": float(payload.novelty_score),
        "created_at": datetime.now(UTC).isoformat(),
    }
    _patents[patent["id"]] = patent
    event_bus.publish("patent.created", patent)
    return RegisterPatentResponse(status="registered", data=PatentRecord.model_validate(patent))


@router.post("/analyze-novelty", response_model=AnalyzeNoveltyResponse)
def analyze_novelty(payload: AnalyzeNoveltyRequest) -> AnalyzeNoveltyResponse:
    score = float(payload.novelty_score)
    return AnalyzeNoveltyResponse(
        status="analyzed",
        is_novel=score >= 70,
        novelty_score=score,
        prior_art_candidates=payload.prior_art_candidates,
    )


@router.post("/validate-prior-art", response_model=ValidatePriorArtResponse)
def validate_prior_art(payload: ValidatePriorArtRequest) -> ValidatePriorArtResponse:
    patent_id = payload.patent_id
    if not patent_id or patent_id not in _patents:
        raise HTTPException(status_code=404, detail="Patente não encontrada")

    _patents[patent_id]["prior_art_checked"] = True
    _patents[patent_id]["status"] = "approved"
    event_bus.publish("patent.approved", _patents[patent_id])
    return ValidatePriorArtResponse(
        status="prior_art_validated",
        data=PatentRecord.model_validate(_patents[patent_id]),
    )


@router.post("/license", response_model=CreateLicenseResponse)
def create_license(payload: CreateLicenseRequest) -> CreateLicenseResponse:
    patent_id = payload.patent_id
    if not patent_id or patent_id not in _patents:
        raise HTTPException(status_code=404, detail="Patente não encontrada")

    license_data = {
        "patent_id": patent_id,
        "licensee": payload.licensee,
        "royalty_rate": float(payload.royalty_rate),
        "licensed_at": datetime.now(UTC).isoformat(),
    }
    _patents[patent_id]["status"] = "licensed"
    event_bus.publish("patent.licensed", {**_patents[patent_id], **license_data})
    return CreateLicenseResponse.model_validate({"status": "licensed", "data": license_data})


@router.get("/{patent_id}", response_model=PatentRecord)
def get_patent(patent_id: str) -> PatentRecord:
    if patent_id not in _patents:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    return PatentRecord.model_validate(_patents[patent_id])
