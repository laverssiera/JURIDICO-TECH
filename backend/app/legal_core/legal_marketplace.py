"""
LICEU 6.x — Legal Marketplace
Marketplace externo para perícias, arbitragem, compliance, laudos e auditoria.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


SERVICES = [
    "pericia", "arbitragem", "compliance", "laudo", "due_diligence", "auditoria", "engenharia_legal"
]


class LegalMarketplaceDomain:
    def __init__(self) -> None:
        self._requests: dict[str, dict] = {}

    def create_request(self, client_name: str, service_type: str, description: str, budget: float | None = None) -> dict:
        req_id = f"MKT-{uuid4().hex[:8].upper()}"
        req = {
            "request_id": req_id,
            "client_name": client_name,
            "service_type": service_type,
            "description": description,
            "budget": budget,
            "status": "qualified_by_john",
            "pipeline": [
                "john_qualify",
                "legal_scope",
                "anchor_execution",
                "hub_billing",
                "cea_profitability",
            ],
            "created_at": utc_now(),
        }
        self._requests[req_id] = req
        return req

    def update_status(self, request_id: str, status: str) -> dict:
        req = self._get(request_id)
        req["status"] = status
        req["updated_at"] = utc_now()
        return req

    def list_requests(self, service_type: str | None = None) -> list[dict]:
        values = list(self._requests.values())
        if service_type:
            values = [v for v in values if v["service_type"] == service_type]
        return values

    def _get(self, request_id: str) -> dict:
        req = self._requests.get(request_id)
        if not req:
            raise KeyError("Solicitação não encontrada")
        return req
