from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, status

from juridicotech.core.audit import log_action
from juridicotech.core.db import get_connection
from juridicotech.core.rbac import require_permission
from juridicotech.modules.state import contract_signatures_db, contract_versions_db, contracts_db


router = APIRouter()
UTC = timezone.utc

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"pending", "canceled"},
    "pending": {"signed", "canceled"},
    "signed": {"active", "canceled"},
    "active": {"completed", "canceled"},
    "completed": set(),
    "canceled": set(),
}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _hash_payload(payload: dict, previous_hash: str | None = None) -> str:
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    material = f"{serialized}|{previous_hash or ''}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _as_uuid_or_none(value: str | None):
    if not value:
        return None
    try:
        return UUID(str(value))
    except Exception:
        return None


def _db_insert_contract(contract: dict) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO contracts (id, type, status, created_by, deal_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    UUID(contract["id"]),
                    contract["type"],
                    contract["status"],
                    _as_uuid_or_none(contract.get("created_by")),
                    _as_uuid_or_none(contract.get("deal_id")),
                    contract["created_at"],
                ),
            )
        connection.commit()


def _db_insert_version(version: dict) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO contract_versions (id, contract_id, version, content, hash, created_at)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                """,
                (
                    UUID(version["id"]),
                    UUID(version["contract_id"]),
                    version["version"],
                    json.dumps(version["content"], ensure_ascii=True),
                    version["hash"],
                    version["created_at"],
                ),
            )
        connection.commit()


def _db_update_contract_status(contract_id: str, target_status: str) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE contracts SET status = %s WHERE id = %s",
                (target_status, UUID(contract_id)),
            )
        connection.commit()


def _db_insert_signature(signature: dict) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO contract_signatures (id, contract_id, user_id, ip_address, signed_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    UUID(signature["id"]),
                    UUID(signature["contract_id"]),
                    _as_uuid_or_none(signature.get("user_id")),
                    signature.get("ip_address"),
                    signature["signed_at"],
                ),
            )
        connection.commit()


@router.post("/")
def create_contract(payload: dict, x_user_role: str = Header(default="SYSTEM_AUTOMATION")) -> dict:
    require_permission(x_user_role, "create_contract")

    contract_id = str(uuid4())
    now = _utc_now()
    contract = {
        "id": contract_id,
        "type": payload.get("type", "generic"),
        "status": "draft",
        "created_by": payload.get("created_by"),
        "deal_id": payload.get("deal_id"),
        "created_at": now,
        "updated_at": now,
    }
    contracts_db[contract_id] = contract

    version_payload = {
        "type": contract["type"],
        "deal_id": contract["deal_id"],
        "parties": payload.get("parties", []),
        "clauses": payload.get("clauses", []),
    }
    version_hash = _hash_payload(version_payload)
    contract_versions_db[contract_id] = [
        {
            "id": str(uuid4()),
            "contract_id": contract_id,
            "version": 1,
            "content": version_payload,
            "hash": version_hash,
            "created_at": now,
        }
    ]

    try:
        _db_insert_contract(contract)
        _db_insert_version(contract_versions_db[contract_id][0])
    except Exception:
        pass

    log_action("contract.created", payload.get("created_by"), {"contract_id": contract_id})
    return {"contract_id": contract_id, "status": contract["status"]}


@router.get("/{contract_id}")
def get_contract(contract_id: str, x_user_role: str = Header(default="JURIDICO_ANALYST")) -> dict:
    require_permission(x_user_role, "read")
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contract not found")

    return {
        "contract": contract,
        "versions": contract_versions_db.get(contract_id, []),
        "signatures": contract_signatures_db.get(contract_id, []),
    }


@router.post("/{contract_id}/version")
def create_contract_version(
    contract_id: str,
    payload: dict,
    x_user_role: str = Header(default="JURIDICO_ANALYST"),
) -> dict:
    require_permission(x_user_role, "create_contract")
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contract not found")

    versions = contract_versions_db.setdefault(contract_id, [])
    previous_hash = versions[-1]["hash"] if versions else None
    version_number = len(versions) + 1
    now = _utc_now()
    version = {
        "id": str(uuid4()),
        "contract_id": contract_id,
        "version": version_number,
        "content": payload,
        "hash": _hash_payload(payload, previous_hash),
        "created_at": now,
    }
    versions.append(version)
    contract["updated_at"] = now

    try:
        _db_insert_version(version)
    except Exception:
        pass

    log_action("contract.versioned", payload.get("author_id"), {"contract_id": contract_id, "version": version_number})
    return {"contract_id": contract_id, "version": version_number, "hash": version["hash"]}


@router.post("/{contract_id}/status")
def change_contract_status(
    contract_id: str,
    payload: dict,
    x_user_role: str = Header(default="JURIDICO_MASTER"),
) -> dict:
    require_permission(x_user_role, "sign_contract")
    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contract not found")

    target_status = payload.get("status")
    if target_status not in ALLOWED_TRANSITIONS.get(contract["status"], set()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="invalid status transition")

    contract["status"] = target_status
    contract["updated_at"] = _utc_now()
    try:
        _db_update_contract_status(contract_id, target_status)
    except Exception:
        pass
    log_action("contract.status.changed", payload.get("actor_id"), {"contract_id": contract_id, "status": target_status})
    return {"contract_id": contract_id, "status": target_status}


@router.post("/{contract_id}/sign")
def sign_contract(
    contract_id: str,
    payload: dict,
    x_user_role: str = Header(default="JURIDICO_ANALYST"),
) -> dict:
    require_permission(x_user_role, "sign_contract")

    contract = contracts_db.get(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if contract["status"] == "draft":
        contract["status"] = "pending"
    if contract["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="contract must be pending before sign")

    contract["status"] = "signed"
    contract["updated_at"] = _utc_now()

    signature = {
        "id": str(uuid4()),
        "contract_id": contract_id,
        "user_id": payload.get("user_id"),
        "ip_address": payload.get("ip_address"),
        "signed_at": _utc_now(),
    }
    contract_signatures_db.setdefault(contract_id, []).append(signature)

    try:
        _db_update_contract_status(contract_id, "signed")
        _db_insert_signature(signature)
    except Exception:
        pass

    log_action("contract.signed", payload.get("user_id"), {"contract_id": contract_id})
    return {"status": "signed", "contract_id": contract_id}
