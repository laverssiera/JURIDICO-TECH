from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.integration.event_bus import event_bus

router = APIRouter()
_authorship_history: dict[str, list[dict]] = {}


@router.post("/register")
def register_authorship(payload: dict) -> dict:
    experiment_id = payload.get("experiment_id")
    author_id = payload.get("author_id")
    if not experiment_id or not author_id:
        raise HTTPException(status_code=422, detail="Campos obrigatórios: experiment_id, author_id")

    event = {
        "id": str(uuid4()),
        "experiment_id": experiment_id,
        "author_id": author_id,
        "contribution_type": payload.get("contribution_type", "discovery"),
        "contribution_score": float(payload.get("contribution_score", 0)),
        "created_at": datetime.now(UTC).isoformat(),
    }
    _authorship_history.setdefault(experiment_id, []).append(event)
    event_bus.publish("science.authorship.registered", event)
    return {"status": "registered", "data": event}


@router.post("/validate")
def validate_authorship(payload: dict) -> dict:
    event = {
        "experiment_id": payload.get("experiment_id"),
        "validator_id": payload.get("validator_id"),
        "is_valid": bool(payload.get("is_valid", True)),
        "notes": payload.get("notes", ""),
        "validated_at": datetime.now(UTC).isoformat(),
    }
    subject = "science.discovery.validated" if event["is_valid"] else "science.discovery.disputed"
    event_bus.publish(subject, event)
    return {"status": "validated", "data": event}


@router.get("/history")
def authorship_history(experiment_id: str) -> dict:
    return {"experiment_id": experiment_id, "history": _authorship_history.get(experiment_id, [])}


@router.post("/dispute")
def dispute_authorship(payload: dict) -> dict:
    dispute = {
        "id": str(uuid4()),
        "experiment_id": payload.get("experiment_id"),
        "claimant_id": payload.get("claimant_id"),
        "reason": payload.get("reason", ""),
        "created_at": datetime.now(UTC).isoformat(),
    }
    event_bus.publish("science.discovery.disputed", dispute)
    return {"status": "dispute_opened", "data": dispute}
