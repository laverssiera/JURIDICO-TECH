"""
LICEU 6.x — Regulatory Radar Global
Monitora fontes normativas e gera impacto + ação recomendada por sistemas do ecossistema.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


SOURCES = [
    "STF", "STJ", "TRT", "TCU", "CREA", "CAU", "Receita Federal",
    "ABNT", "NR", "Legislação Ambiental", "Jurisprudência", "Tributário",
]

IMPACT_AREAS = ["OPERA", "RH", "ANCHOR", "HUBBACKOFFICE", "CEA", "ACADEMIA"]


class RegulatoryRadarGlobalDomain:
    def __init__(self) -> None:
        self._signals: list[dict] = []

    def ingest_signal(
        self,
        source: str,
        title: str,
        summary: str,
        tags: list[str],
        severity: str = "medium",
    ) -> dict:
        signal = {
            "signal_id": f"RAD-{uuid4().hex[:8].upper()}",
            "source": source,
            "title": title,
            "summary": summary,
            "tags": tags,
            "severity": severity,
            "created_at": utc_now(),
        }
        signal["impact"] = self.assess_impact(signal)
        self._signals.append(signal)
        return signal

    def assess_impact(self, signal: dict) -> dict:
        impacted = []
        title = (signal.get("title", "") + " " + signal.get("summary", "")).lower()
        if "nr" in title or "sst" in title:
            impacted.extend(["OPERA", "RH", "ANCHOR"])
        if "fiscal" in title or "tribut" in title or "receita" in title:
            impacted.extend(["HUBBACKOFFICE", "CEA"])
        if "ambiental" in title or "esg" in title:
            impacted.extend(["OPERA", "ANCHOR", "CEA"])
        if "treinamento" in title or "capacitação" in title:
            impacted.append("ACADEMIA")
        if not impacted:
            impacted = ["OPERA", "HUBBACKOFFICE"]

        impacted = sorted(set(impacted))
        return {
            "impacted_systems": impacted,
            "recommended_actions": self._recommended_actions(signal, impacted),
            "deadline_days": 15 if signal.get("severity") in ("high", "critical") else 30,
            "assessed_at": utc_now(),
        }

    def list_signals(self, source: str | None = None, severity: str | None = None) -> list[dict]:
        result = self._signals
        if source:
            result = [s for s in result if s["source"] == source]
        if severity:
            result = [s for s in result if s["severity"] == severity]
        return result

    def disseminate(self, signal_id: str) -> dict:
        signal = next((s for s in self._signals if s["signal_id"] == signal_id), None)
        if not signal:
            raise KeyError("Sinal regulatório não encontrado")
        return {
            "signal_id": signal_id,
            "status": "disseminated",
            "targets": signal["impact"]["impacted_systems"],
            "message": f"John Jurídico disseminou: {signal['title']}",
            "at": utc_now(),
        }

    def _recommended_actions(self, signal: dict, impacted: list[str]) -> list[str]:
        actions = ["Publicar comunicado regulatório interno"]
        txt = (signal.get("title", "") + " " + signal.get("summary", "")).lower()
        if "nr" in txt or "sst" in txt:
            actions.append("Agendar treinamento obrigatório em 15 dias")
            actions.append("Atualizar checklist de segurança operacional")
        if "fiscal" in txt or "tribut" in txt:
            actions.append("Executar revisão de compliance fiscal")
        if "ambiental" in txt:
            actions.append("Revisar licenciamento e evidências ambientais")
        if "jurisprud" in txt:
            actions.append("Atualizar playbook de contencioso/arbitragem")
        return actions
