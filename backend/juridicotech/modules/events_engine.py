from __future__ import annotations

import asyncio
import json

from app.integration.legal_event_registry import subject_for_event
from juridicotech.integrations.core_dna import legal_decision
from juridicotech.integrations.nats import nats_bus


async def handle_deal_created(msg) -> None:
    raw = msg.data.decode("utf-8")
    deal = json.loads(raw)

    contract = {
        "id": deal.get("id"),
        "type": "intermediation",
        "status": "draft",
        "deal_id": deal.get("id"),
    }
    await nats_bus.publish(subject_for_event("legal.contract.created"), json.dumps(contract, ensure_ascii=True))

    decision = legal_decision(
        {
            "deal_id": deal.get("id"),
            "value": deal.get("value", 0),
        }
    )

    risk_update = {
        "deal_id": deal.get("id"),
        "risk_level": decision["risk_level"],
        "score": decision["score"],
    }
    await nats_bus.publish(subject_for_event("legal.risk.update"), json.dumps(risk_update, ensure_ascii=True))

    if decision["risk_level"] == "high":
        flagged = {
            "message": f"Deal {deal.get('id')} bloqueado",
            "deal_id": deal.get("id"),
        }
        await nats_bus.publish(subject_for_event("legal.risk.flagged"), json.dumps(flagged, ensure_ascii=True))


async def start() -> None:
    await nats_bus.connect()
    await nats_bus.subscribe("deal.created", handle_deal_created)
    await nats_bus.subscribe(subject_for_event("deal_created"), handle_deal_created)


if __name__ == "__main__":
    asyncio.run(start())
