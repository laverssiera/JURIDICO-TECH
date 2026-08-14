from __future__ import annotations

import json

from fastapi import APIRouter, Header

from app.integration.event_bus import event_bus
from juridicotech.core.audit import log_action
from juridicotech.core.rbac import require_permission
from juridicotech.integrations.core_dna import legal_decision
from juridicotech.integrations.nats import nats_bus
from juridicotech.modules.contracts import create_contract
from juridicotech.modules.risk import analyze


router = APIRouter()


@router.post("/deal-created")
async def handle_deal_created(payload: dict, x_user_role: str = Header(default="SYSTEM_AUTOMATION")) -> dict:
    require_permission(x_user_role, "events")

    contract_result = create_contract(
        {
            "type": payload.get("contract_type", "intermediation"),
            "created_by": payload.get("user_id"),
            "deal_id": payload.get("deal_id"),
            "parties": payload.get("parties", []),
            "clauses": payload.get("clauses", ["non_circ", "commission_protection"]),
        },
        x_user_role="SYSTEM_AUTOMATION",
    )

    risk_result = analyze(
        {
            "actors": payload.get("actors", []),
            "amount": payload.get("amount", 0),
            "has_documents": payload.get("has_documents", True),
            "user_age_days": payload.get("user_age_days", 365),
            "actor_id": payload.get("user_id"),
        },
        x_user_role="SYSTEM_AUTOMATION",
    )

    decision = legal_decision(
        {
            "deal_id": payload.get("deal_id"),
            "value": payload.get("amount", 0),
            "risk": risk_result,
            "contract_id": contract_result["contract_id"],
        }
    )

    blocked = risk_result["risk_level"] == "high" or decision.get("decision") in {"block", "deny"}
    event = {
        "deal_id": payload.get("deal_id"),
        "contract_id": contract_result["contract_id"],
        "risk": risk_result,
        "decision": decision,
        "blocked": blocked,
    }

    event_bus.publish(
        "legal.contract.created",
        {
            "id": contract_result["contract_id"],
            "type": payload.get("contract_type", "intermediation"),
            "status": "draft",
            "deal_id": payload.get("deal_id"),
        },
    )
    event_bus.publish(
        "legal.risk.update",
        {
            "deal_id": payload.get("deal_id"),
            "risk_level": decision.get("risk_level", risk_result["risk_level"]),
            "score": decision.get("score", risk_result["score"]),
        },
    )
    if blocked:
        event_bus.publish(
            "legal.risk.flagged",
            {
                "message": f"Deal {payload.get('deal_id')} bloqueado",
                "deal_id": payload.get("deal_id"),
                "reason": "high_risk",
            },
        )

    log_action("event.deal_created.processed", payload.get("user_id"), event)
    return event


@router.post("/publish")
async def publish_event(payload: dict, x_user_role: str = Header(default="SYSTEM_AUTOMATION")) -> dict:
    require_permission(x_user_role, "events")
    subject = payload["subject"]
    data = json.dumps(payload.get("data", {}), ensure_ascii=True)
    await nats_bus.publish(subject, data)
    log_action("event.published", payload.get("actor_id"), {"subject": subject})
    return {"published": True, "subject": subject}
