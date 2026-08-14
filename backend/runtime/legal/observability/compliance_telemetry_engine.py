from __future__ import annotations


class ComplianceTelemetryEngine:
    def __init__(self) -> None:
        self._events = 0
        self._successful = 0

    def record(self, compliant: bool) -> None:
        self._events += 1
        if compliant:
            self._successful += 1

    def metrics(self) -> dict:
        ratio = (self._successful / self._events) if self._events else 1.0
        return {
            "events": self._events,
            "successful": self._successful,
            "compliance_propagation": round(ratio, 4),
        }
