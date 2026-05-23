from __future__ import annotations

from datetime import datetime, UTC


class SovereignLegalIdentity:
    def __init__(self) -> None:
        self._registry: dict[str, dict] = {}

    def issue(self, entity_id: str, jurisdiction: str) -> dict:
        identity = {
            "entity_id": entity_id,
            "jurisdiction": jurisdiction,
            "issued_at": datetime.now(UTC).isoformat(),
            "identity_state": "trusted",
        }
        self._registry[entity_id] = identity
        return identity

    def count(self) -> int:
        return len(self._registry)
