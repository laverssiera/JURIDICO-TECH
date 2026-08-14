from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.integration.legal_event_registry import subject_for_event


UTC = timezone.utc


class LegalAdapter:
    def __init__(self, publisher) -> None:
        self.publisher = publisher

    async def emit_event(self, event_type: str, entity_id: str, metadata: dict | None = None) -> None:
        from core_dna.compiled import legal_pb2

        event = legal_pb2.LegalEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            entity_id=entity_id,
            entity_type=(metadata or {}).get("entity_type", "deal"),
            user_id=(metadata or {}).get("user_id", "system"),
            module=(metadata or {}).get("module", "ARCHIMEDES_CORE"),
            metadata={**(metadata or {}), "event_version": "v1"},
            timestamp=int(datetime.now(UTC).timestamp()),
        )

        await self.publisher.publish(subject_for_event(event_type), event.SerializeToString())
