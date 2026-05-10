from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.integration.event_bus import event_bus

router = APIRouter()
_patents: dict[str, dict] = {}


@router.post("/register")
def register_patent(payload: dict) -> dict:
    title = payload.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="Campo obrigatório: title")

    patent = {
        "id": str(uuid4()),
        "title": title,
        "category": payload.get("category", "general"),
        "status": "draft",
        "novelty_score": float(payload.get("novelty_score", 0)),
        "created_at": datetime.now(UTC).isoformat(),
    }
    _patents[patent["id"]] = patent
    event_bus.publish("patent.created", patent)
    return {"status": "registered", "data": patent}


@router.post("/analyze-novelty")
def analyze_novelty(payload: dict) -> dict:
    score = float(payload.get("novelty_score", 75.0))
    return {
        "status": "analyzed",
        "is_novel": score >= 70,
        "novelty_score": score,
        "prior_art_candidates": payload.get("prior_art_candidates", []),
    }


@router.post("/validate-prior-art")
def validate_prior_art(payload: dict) -> dict:
    patent_id = payload.get("patent_id")
    if not patent_id or patent_id not in _patents:
        raise HTTPException(status_code=404, detail="Patente não encontrada")

    _patents[patent_id]["prior_art_checked"] = True
    _patents[patent_id]["status"] = "approved"
    event_bus.publish("patent.approved", _patents[patent_id])
    return {"status": "prior_art_validated", "data": _patents[patent_id]}


@router.post("/license")
def create_license(payload: dict) -> dict:
    patent_id = payload.get("patent_id")
    if not patent_id or patent_id not in _patents:
        raise HTTPException(status_code=404, detail="Patente não encontrada")

    license_data = {
        "patent_id": patent_id,
        "licensee": payload.get("licensee"),
        "royalty_rate": float(payload.get("royalty_rate", 0)),
        "licensed_at": datetime.now(UTC).isoformat(),
    }
    _patents[patent_id]["status"] = "licensed"
    event_bus.publish("patent.licensed", {**_patents[patent_id], **license_data})
    return {"status": "licensed", "data": license_data}


@router.get("/{patent_id}")
def get_patent(patent_id: str) -> dict:
    if patent_id not in _patents:
        raise HTTPException(status_code=404, detail="Patente não encontrada")
    return _patents[patent_id]
