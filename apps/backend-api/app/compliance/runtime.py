"""Compliance Runtime — in-process registry that tracks per-entity compliance state."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from app.compliance.engine import run_compliance_engine


ISOLDE_MARS_PROFILE: dict[str, Any] = {
    "case_code": "CASE 3",
    "case_name": "ISOLDE-MARS",
    "mission_class": "mars_base",
    "jurisdiction": "martian-base",
    "objective_tracks": [
        "space-law",
        "ip",
        "research",
        "licensing",
    ],
    "objectives": [
        "Pesquisa de núcleos exóticos",
        "Descoberta de materiais",
        "Blindagem radiológica",
        "Materiais para construção civil URIDICOTECH",
    ],
    "regulatory_stack": {
        "space_law": "outer-space-treaty",
        "ip": "interplanetary-ip",
        "research": "scientific-compliance",
        "licensing": "export-control",
    },
}


@dataclass
class RuntimeEntry:
    entity_id: str
    scope: str
    case_code: str | None = None
    case_name: str | None = None
    mission_profile: dict[str, Any] = field(default_factory=dict)
    objective_tracks: list[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_checked_at: datetime | None = None
    last_score: float | None = None
    last_findings: list[dict[str, Any]] = field(default_factory=list)
    check_count: int = 0
    active: bool = True


class ComplianceRuntime:
    """Singleton-style in-memory registry for live compliance monitoring."""

    _registry: dict[str, RuntimeEntry] = {}

    @staticmethod
    def _build_mission_profile(
        case_code: str | None = None,
        case_name: str | None = None,
        mission_profile: dict[str, Any] | None = None,
        objective_tracks: list[str] | None = None,
    ) -> tuple[str | None, str | None, dict[str, Any], list[str]]:
        profile: dict[str, Any] = {}
        tracks: list[str] = []

        if case_code == ISOLDE_MARS_PROFILE["case_code"] or case_name == ISOLDE_MARS_PROFILE["case_name"]:
            profile.update(ISOLDE_MARS_PROFILE)
            tracks.extend(ISOLDE_MARS_PROFILE["objective_tracks"])

        if mission_profile:
            profile.update(mission_profile)

        if objective_tracks:
            tracks = list(dict.fromkeys([*tracks, *objective_tracks]))

        resolved_case_code = case_code or profile.get("case_code")
        resolved_case_name = case_name or profile.get("case_name")

        return resolved_case_code, resolved_case_name, profile, tracks

    @classmethod
    def register(
        cls,
        entity_id: str,
        scope: str,
        *,
        case_code: str | None = None,
        case_name: str | None = None,
        mission_profile: dict[str, Any] | None = None,
        objective_tracks: list[str] | None = None,
    ) -> RuntimeEntry:
        resolved_case_code, resolved_case_name, resolved_profile, resolved_tracks = cls._build_mission_profile(
            case_code=case_code,
            case_name=case_name,
            mission_profile=mission_profile,
            objective_tracks=objective_tracks,
        )
        entry = cls._registry.get(entity_id)
        if entry is None:
            entry = RuntimeEntry(
                entity_id=entity_id,
                scope=scope,
                case_code=resolved_case_code,
                case_name=resolved_case_name,
                mission_profile=resolved_profile,
                objective_tracks=resolved_tracks,
            )
            cls._registry[entity_id] = entry
        else:
            entry.active = True
            entry.scope = scope
            entry.case_code = resolved_case_code or entry.case_code
            entry.case_name = resolved_case_name or entry.case_name
            if resolved_profile:
                entry.mission_profile = resolved_profile
            if resolved_tracks:
                entry.objective_tracks = resolved_tracks
        return entry

    @classmethod
    def register_isolde_mars(cls, entity_id: str, scope: str = "interplanetary") -> RuntimeEntry:
        return cls.register(
            entity_id,
            scope,
            case_code=ISOLDE_MARS_PROFILE["case_code"],
            case_name=ISOLDE_MARS_PROFILE["case_name"],
            mission_profile=ISOLDE_MARS_PROFILE,
            objective_tracks=ISOLDE_MARS_PROFILE["objective_tracks"],
        )

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
    def update_scope(cls, entity_id: str, scope: str) -> RuntimeEntry | None:
        entry = cls._registry.get(entity_id)
        if entry is None or not entry.active:
            return None
        entry.scope = scope
        return entry

    @classmethod
    def deregister(cls, entity_id: str) -> bool:
        entry = cls._registry.get(entity_id)
        if entry is None:
            return False
        entry.active = False
        return True

    @classmethod
    def list_all(
        cls,
        active: bool | None = None,
        order_by: Literal["registered_at", "last_checked_at"] = "registered_at",
        direction: Literal["asc", "desc"] = "desc",
    ) -> list[RuntimeEntry]:
        entries = list(cls._registry.values())
        if active is not None:
            entries = [entry for entry in entries if entry.active is active]

        reverse = direction == "desc"

        # Secondary deterministic ordering: entity_id asc (stable),
        # then primary timestamp ordering.
        entries.sort(key=lambda entry: entry.entity_id)
        if order_by == "last_checked_at":
            entries.sort(key=lambda entry: entry.last_checked_at or entry.registered_at, reverse=reverse)
        else:
            entries.sort(key=lambda entry: entry.registered_at, reverse=reverse)

        return entries
