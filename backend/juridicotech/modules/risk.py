from __future__ import annotations

from datetime import datetime, timezone
import json
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Header

from juridicotech.core.audit import log_action
from juridicotech.core.db import get_connection
from juridicotech.core.rbac import require_permission


router = APIRouter()
UTC = timezone.utc


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _as_uuid_or_none(value: str | None):
    if not value:
        return None
    try:
        return UUID(str(value))
    except Exception:
        return None


def _db_insert_risk(payload: dict, response: dict) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO legal_risk (id, deal_id, risk_level, score, flags, created_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    uuid4(),
                    _as_uuid_or_none(payload.get("deal_id")),
                    response["risk_level"],
                    response["score"],
                    json.dumps(response["flags"], ensure_ascii=True),
                    response["created_at"],
                ),
            )
        connection.commit()


@router.post("/analyze")
def analyze(payload: dict, x_user_role: str = Header(default="JURIDICO_ANALYST")) -> dict:
    require_permission(x_user_role, "analyze")

    score = 0.0
    flags: list[str] = []

    if not payload.get("has_documents", True):
        score += 0.35
        flags.append("missing_document")
    if float(payload.get("amount", 0) or 0) >= 1_000_000:
        score += 0.25
        flags.append("high_value")
    if int(payload.get("user_age_days", 365) or 365) <= 30:
        score += 0.2
        flags.append("new_user")
    if len(payload.get("actors", [])) <= 1:
        score += 0.15
        flags.append("single_actor")

    score = round(min(0.99, max(0.01, score)), 2)
    if score >= 0.75:
        level = "high"
    elif score >= 0.45:
        level = "medium"
    else:
        level = "low"

    response = {
        "risk_level": level,
        "score": score,
        "flags": flags,
        "created_at": _utc_now(),
    }

    try:
        _db_insert_risk(payload, response)
    except Exception:
        pass

    log_action("risk.analyzed", payload.get("actor_id"), response)
    return response
