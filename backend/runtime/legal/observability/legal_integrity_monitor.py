from __future__ import annotations


class LegalIntegrityMonitor:
    def __init__(self) -> None:
        self._flags: list[dict] = []

    def ingest_flag(self, name: str, severity: str) -> None:
        self._flags.append({"name": name, "severity": severity})

    def status(self) -> dict:
        critical = sum(1 for flag in self._flags if flag.get("severity") == "critical")
        return {
            "critical_flags": critical,
            "integrity_state": "stable" if critical == 0 else "at_risk",
            "total_flags": len(self._flags),
        }
