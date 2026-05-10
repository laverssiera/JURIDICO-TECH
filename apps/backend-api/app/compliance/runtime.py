"""Compliance Runtime — in-process registry that tracks per-entity compliance state."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.compliance.engine import run_compliance_engine


@dataclass
class RuntimeEntry:
    entity_id: str
    scope: str
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_checked_at: datetime | None = None
    last_score: float | None = None
    last_findings: list[dict[str, Any]] = field(default_factory=list)
    check_count: int = 0
    active: bool = True


class ComplianceRuntime:
    """Singleton-style in-memory registry for live compliance monitoring."""

    _registry: dict[str, RuntimeEntry] = {}

    @classmethod
    def register(cls, entity_id: str, scope: str) -> RuntimeEntry:
        entry = cls._registry.get(entity_id)
        if entry is None:
            entry = RuntimeEntry(entity_id=entity_id, scope=scope)
            cls._registry[entity_id] = entry
        else:
            entry.active = True
            entry.scope = scope
        return entry

    @classmethod
    def status(cls, entity_id: str) -> RuntimeEntry | None:
        return cls._registry.get(entity_id)

    @classmethod
    def pulse(cls, entity_id: str) -> RuntimeEntry | None:
        entry = cls._registry.get(entity_id)
        if entry is None or not entry.active:
            return None
        score, findings = run_compliance_engine(entity_id, entry.scope)
        entry.last_score = score
        entry.last_checked_at = datetime.now(UTC)
        entry.check_count += 1
        entry.last_findings = [
            {
                "rule": f.rule,
                "alert_type": f.alert_type,
                "severity": f.severity,
                "passed": f.passed,
                "message": f.message,
            }
            for f in findings
        ]
        return entry

    @classmethod
    def deregister(cls, entity_id: str) -> bool:
        entry = cls._registry.get(entity_id)
        if entry is None:
            return False
        entry.active = False
        return True

    @classmethod
    def list_all(cls) -> list[RuntimeEntry]:
        return list(cls._registry.values())
