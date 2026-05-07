"""
LICEU 6.x — Legal War Room
Central de crise para acidentes graves, ESG, fraude, embargo e desastres.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.persistence.store import PersistenceStore

UTC = timezone.utc
_DOMAIN = "legal_war_room"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class LegalWarRoomDomain:
    def __init__(self, store: "PersistenceStore | None" = None) -> None:
        self._store = store
        self._incidents: dict[str, dict] = {}
        if store:
            for record in store.list(_DOMAIN):
                self._incidents[record["incident_id"]] = record

    def open_incident(self, title: str, severity: str, category: str, summary: str) -> dict:
        incident_id = f"WR-{uuid4().hex[:8].upper()}"
        incident = {
            "incident_id": incident_id,
            "title": title,
            "severity": severity,
            "category": category,
            "summary": summary,
            "status": "open",
            "timeline": [{"event": "incident_opened", "at": utc_now()}],
            "evidence": [],
            "teams": ["juridico", "compliance", "comunicacao"],
            "opened_at": utc_now(),
        }
        self._incidents[incident_id] = incident
        if self._store:
            self._store.set(_DOMAIN, incident_id, incident)
        return incident

    def add_evidence(self, incident_id: str, description: str, source: str) -> dict:
        incident = self._get(incident_id)
        item = {"description": description, "source": source, "at": utc_now()}
        incident["evidence"].append(item)
        incident["timeline"].append({"event": "evidence_added", "at": utc_now()})
        return item

    def add_timeline_event(self, incident_id: str, event: str, details: dict | None = None) -> dict:
        incident = self._get(incident_id)
        entry = {"event": event, "details": details or {}, "at": utc_now()}
        incident["timeline"].append(entry)
        return entry

    def official_response(self, incident_id: str) -> dict:
        incident = self._get(incident_id)
        return {
            "incident_id": incident_id,
            "narrative": (
                f"Incidente '{incident['title']}' sob gestão da Legal War Room. "
                "Evidências centralizadas, times acionados e resposta jurídica coordenada."
            ),
            "legal_position": "Apuração em curso com preservação de cadeia de custódia",
            "next_steps": [
                "Consolidar relatório técnico-jurídico",
                "Atualizar stakeholders críticos",
                "Definir plano de mitigação e prevenção",
            ],
            "generated_at": utc_now(),
        }

    def close_incident(self, incident_id: str, closure_note: str) -> dict:
        incident = self._get(incident_id)
        incident["status"] = "closed"
        incident["closure_note"] = closure_note
        incident["timeline"].append({"event": "incident_closed", "at": utc_now()})
        incident["closed_at"] = utc_now()
        if self._store:
            self._store.set(_DOMAIN, incident_id, incident)
        return incident

    def list_incidents(self, status: str | None = None) -> list[dict]:
        incidents = list(self._incidents.values())
        if status:
            incidents = [i for i in incidents if i["status"] == status]
        return incidents

    def _get(self, incident_id: str) -> dict:
        i = self._incidents.get(incident_id)
        if not i:
            raise KeyError("Incidente não encontrado")
        return i
