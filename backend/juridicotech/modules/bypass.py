from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Header

from juridicotech.core.audit import log_action
from juridicotech.core.db import get_connection
from juridicotech.core.rbac import require_permission
from juridicotech.modules.state import non_circ_db


router = APIRouter()
UTC = timezone.utc


def _hash_relationship(lead_id: str, broker_id: str, property_id: str) -> str:
    payload = {
        "lead_id": lead_id,
        "broker_id": broker_id,
        "property_id": property_id,
    }
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _as_uuid_or_none(value: str | None):
    if not value:
        return None
    try:
        return UUID(str(value))
    except Exception:
        return None


def _db_insert_non_circ(record: dict) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO non_circumvention
                (id, relationship_hash, lead_id, broker_id, property_id, protected_until, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (relationship_hash)
                DO UPDATE SET
                    broker_id = excluded.broker_id,
                    property_id = excluded.property_id,
                    protected_until = excluded.protected_until
                """,
                (
                    UUID(record["id"]),
                    record["relationship_hash"],
                    _as_uuid_or_none(record.get("lead_id")),
                    _as_uuid_or_none(record.get("broker_id")),
                    _as_uuid_or_none(record.get("property_id")),
                    record["protected_until"],
                    record["created_at"],
                ),
            )
        connection.commit()


@router.post("/protect")
def protect(payload: dict, x_user_role: str = Header(default="SYSTEM_AUTOMATION")) -> dict:
    require_permission(x_user_role, "events")

    relationship_hash = _hash_relationship(
        payload["lead_id"],
        payload["broker_id"],
        payload["property_id"],
    )
    protected_until = datetime.now(UTC) + timedelta(days=int(payload.get("protection_days", 180)))

    record = {
        "id": str(uuid4()),
        "relationship_hash": relationship_hash,
        "lead_id": payload["lead_id"],
        "broker_id": payload["broker_id"],
        "property_id": payload["property_id"],
        "commission_owner_id": payload.get("commission_owner_id", payload["broker_id"]),
        "protected_until": protected_until.isoformat(),
        "created_at": datetime.now(UTC).isoformat(),
    }
    non_circ_db[relationship_hash] = record
    try:
        _db_insert_non_circ(record)
    except Exception:
        pass
    log_action("non_circ.protected", payload.get("actor_id"), record)
    return record


@router.post("/check")
def check(payload: dict, x_user_role: str = Header(default="SYSTEM_AUTOMATION")) -> dict:
    require_permission(x_user_role, "events")

    relationship_hash = _hash_relationship(
        payload["lead_id"],
        payload["broker_id"],
        payload["property_id"],
    )
    record = non_circ_db.get(relationship_hash)
    if not record:
        return {
            "detected": False,
            "reason": "unprotected_relationship",
            "relationship_hash": relationship_hash,
        }

    protected_until = datetime.fromisoformat(record["protected_until"])
    now = datetime.now(UTC)
    bypass_detected = (
        now < protected_until
        and payload.get("candidate_broker_id")
        and payload.get("candidate_broker_id") != record["broker_id"]
    )

    result = {
        "detected": bool(bypass_detected),
        "relationship_hash": relationship_hash,
        "protected_until": record["protected_until"],
        "commission_owner_id": record["commission_owner_id"],
    }
    if bypass_detected:
        result["blocked"] = True
        log_action("non_circ.bypass_detected", payload.get("actor_id"), result)
    else:
        result["blocked"] = False

    return result
