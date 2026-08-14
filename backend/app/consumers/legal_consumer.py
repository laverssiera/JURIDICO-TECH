from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.integration.legal_event_registry import INPUT_EVENTS
from app.publishers.legal_publisher import LegalPublisher
from app.schemas import MatchProposalRequest
from app.services.legal_core import legal_core_engine


UTC = timezone.utc


class LegalConsumer:
    def __init__(self) -> None:
        self.nc = None
        self.js = None
        self.publisher = None

    async def start(self, nats_url: str = "nats://localhost:4222") -> None:
        import nats

        self.nc = await nats.connect(nats_url)
        self.js = self.nc.jetstream()
        self.publisher = LegalPublisher(self.js)

        await self.js.subscribe(
            "liceu.events.>",
            durable="juridico_consumer",
            cb=self.handle_event,
        )

    async def stop(self) -> None:
        if self.nc:
            await self.nc.drain()
            self.nc = None
            self.js = None
            self.publisher = None

    async def handle_event(self, msg) -> None:
        from core_dna.compiled import legal_pb2

        event = legal_pb2.LegalEvent()
        event.ParseFromString(msg.data)
        await self.route_event(event)

    async def route_event(self, event) -> None:
        if event.event_type not in INPUT_EVENTS:
            return

        if event.event_type == "deal_created":
            await self.handle_deal_created(event)
        elif event.event_type == "match_generated":
            await self.handle_match(event)
        elif event.event_type == "deal_won":
            await self.handle_deal_won(event)

    async def handle_deal_created(self, event) -> None:
        snapshot = legal_core_engine.get_snapshot(event.entity_id)
        has_nda = snapshot.get("nda_signed", False)

        if not has_nda:
            await self.publisher.publish_block(event, "Missing NDA")
            return

        await self.generate_contract(event)

    async def handle_match(self, event) -> None:
        metadata = dict(event.metadata)
        if not all(key in metadata for key in ["lead_id", "deal_id", "property_id", "broker_id"]):
            await self.publisher.publish_block(event, "Missing metadata for match validation")
            return

        result = legal_core_engine.process_match_or_proposal(
            MatchProposalRequest(
                event_name="match_generated",
                lead_id=metadata["lead_id"],
                deal_id=metadata["deal_id"],
                property_id=metadata["property_id"],
                broker_id=metadata["broker_id"],
                owner_id=metadata.get("owner_id"),
                involved_users=metadata.get("involved_users", "").split(",") if metadata.get("involved_users") else [],
                requested_by=metadata.get("requested_by", event.user_id or "system"),
            )
        )
        if result.get("blocked"):
            await self.publisher.publish_block(event, "Blocked on legal match check")
        else:
            await self.publisher.publish_approved(event, "match_processed")

    async def handle_deal_won(self, event) -> None:
        await self.publisher.publish_approved(event, "deal_won_validated")

    async def generate_contract(self, event) -> None:
        from core_dna.compiled import legal_pb2

        new_event = legal_pb2.LegalEvent(
            event_id=str(uuid4()),
            event_type="contract.generated",
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            user_id=event.user_id,
            module=event.module,
            metadata={"event_version": "v1"},
            timestamp=int(datetime.now(UTC).timestamp()),
        )
        await self.publisher.publish_event(new_event)
