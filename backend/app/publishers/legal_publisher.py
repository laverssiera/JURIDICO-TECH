from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.integration.legal_event_registry import subject_for_event


UTC = timezone.utc


class LegalPublisher:
    def __init__(self, jetstream_client) -> None:
        self.js = jetstream_client

    async def publish_event(self, event) -> None:
        subject = subject_for_event(event.event_type)
        await self.js.publish(subject, event.SerializeToString())

    async def publish_block(self, source_event, reason: str):
        from core_dna.compiled import legal_pb2

        event = legal_pb2.LegalEvent(
            event_id=str(uuid4()),
            event_type="legal.blocked",
            entity_type=source_event.entity_type,
            entity_id=source_event.entity_id,
            user_id=source_event.user_id,
            module=source_event.module,
            metadata={"reason": reason, "event_version": "v1"},
            timestamp=int(datetime.now(UTC).timestamp()),
        )
        await self.publish_event(event)

    async def publish_approved(self, source_event, note: str = "approved"):
        from core_dna.compiled import legal_pb2

        event = legal_pb2.LegalEvent(
            event_id=str(uuid4()),
            event_type="legal.approved",
            entity_type=source_event.entity_type,
            entity_id=source_event.entity_id,
            user_id=source_event.user_id,
            module=source_event.module,
            metadata={"note": note, "event_version": "v1"},
            timestamp=int(datetime.now(UTC).timestamp()),
        )
        await self.publish_event(event)
