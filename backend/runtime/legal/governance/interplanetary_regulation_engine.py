from __future__ import annotations

from datetime import datetime, UTC


class InterplanetaryRegulationEngine:
    def __init__(self) -> None:
        self._jurisdictions = {
            "earth": "active",
            "orbital": "active",
            "lunar": "active",
            "mars": "active",
            "deep_space": "active",
        }

    def enforce(self, payload: dict) -> dict:
        jurisdiction = payload.get("jurisdiction", "earth")
        regulation_family = payload.get("regulation_family", "general")
        status = self._jurisdictions.get(jurisdiction, "unknown")
        ready = status == "active"

        return {
            "jurisdiction": jurisdiction,
            "regulation_family": regulation_family,
            "enforcement": "enforced" if ready else "degraded",
            "interplanetary_ready": ready,
            "evaluated_at": datetime.now(UTC).isoformat(),
        }
