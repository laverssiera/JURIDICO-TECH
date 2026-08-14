from __future__ import annotations

from app.integration.event_bus import event_bus
from app.schemas import LegalEventRequest
from app.integration.sdk import spe_factory
from app.services.legal_core import legal_core_engine


class ContractSignedSubscriber:
    event_name = "contract.signed"

    def handle(self, payload: dict) -> dict:
        return spe_factory.start_closing_workflow(
            contract_id=payload["contract_id"],
            monolito_id=payload["monolito_id"],
            spe_name=payload["spe_name"],
            partners=payload["partners"],
            purpose=payload["purpose"],
        )


class LegalEventSubscriber:
    def __init__(self, event_name: str) -> None:
        self.event_name = event_name

    def handle(self, payload: dict) -> dict:
        return legal_core_engine.consume_event(
            LegalEventRequest(
                type=self.event_name,
                payload=payload,
            )
        )


contract_signed_subscriber = ContractSignedSubscriber()
legal_event_subscribers = [
    LegalEventSubscriber("lead_created"),
    LegalEventSubscriber("deal_created"),
    LegalEventSubscriber("match_generated"),
    LegalEventSubscriber("deal_won"),
]
_subscribers_registered = False


def register_integration_subscribers() -> None:
    global _subscribers_registered

    if _subscribers_registered:
        return

    event_bus.subscribe(
        ContractSignedSubscriber.event_name,
        contract_signed_subscriber.handle,
    )
    for subscriber in legal_event_subscribers:
        event_bus.subscribe(subscriber.event_name, subscriber.handle)
    _subscribers_registered = True
