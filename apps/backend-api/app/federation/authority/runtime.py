from __future__ import annotations

import json
import socket
from datetime import UTC, datetime
from typing import Any

from app.federation.config import settings


class FederationAuthority:
    """Registers the monolith in the federation and keeps a local snapshot."""

    def __init__(self) -> None:
        self._client: Any | None = None
        self._last_registration: dict[str, Any] | None = None

    async def connect(self) -> bool:
        try:
            from nats.aio.client import Client as NATS
        except Exception:
            self._client = None
            return False

        client = NATS()
        try:
            await client.connect(settings.NATS_URL)
        except Exception:
            self._client = None
            return False

        self._client = client
        return True

    async def register(self) -> dict[str, Any]:
        payload = {
            "monolith": settings.MONOLITH_NAME,
            "host": socket.gethostname(),
            "domains": [
                "legal-runtime",
                "compliance",
                "arbitration",
                "governance",
                "contracts",
                "forensics",
                "evidence-vault",
                "space-law",
                "patents",
                "interplanetary-ip",
                "planetary-regulation",
                "war-room",
                "observability",
                "memory",
            ],
            "registered_at": datetime.now(UTC).isoformat(),
        }
        self._last_registration = payload

        if self._client is not None:
            await self._client.publish(
                "federation.runtime.register",
                json.dumps(payload).encode(),
            )

        return payload

    def snapshot(self) -> dict[str, Any]:
        return {
            "connected": self._client is not None,
            "last_registration": self._last_registration,
        }
