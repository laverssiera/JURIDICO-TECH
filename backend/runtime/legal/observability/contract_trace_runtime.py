from __future__ import annotations

from datetime import datetime, UTC


class ContractTraceRuntime:
    def __init__(self) -> None:
        self._trace: dict[str, list[dict]] = {}

    def append(self, contract_id: str, action: str, metadata: dict | None = None) -> None:
        event = {
            "action": action,
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._trace.setdefault(contract_id, []).append(event)

    def lineage(self, contract_id: str) -> list[dict]:
        return self._trace.get(contract_id, [])

    def summary(self) -> dict:
        contracts = len(self._trace)
        total_events = sum(len(items) for items in self._trace.values())
        return {
            "tracked_contracts": contracts,
            "lineage_events": total_events,
        }
