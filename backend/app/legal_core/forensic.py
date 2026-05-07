"""
LICEU 6.0 — Domain: Forensic Lab
Ligado ao ANCHOR. Perícias, engenharia legal, laudos técnicos, cadeia de custódia,
drones, sensores, visão computacional, reconstrução de eventos e timeline técnica.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


PERICIA_TYPES: list[str] = [
    "pericia_engenharia",
    "pericia_contabil",
    "pericia_ambiental",
    "pericia_trabalhista",
    "vistoria_predial",
    "laudo_infiltracao",
    "laudo_estrutural",
    "laudo_incendio",
    "laudo_acidente_trabalho",
    "laudo_vicio_construtivo",
    "pericia_drone",
    "pericia_sensor_iot",
    "reconstrucao_evento",
]

EVIDENCE_TYPES: list[str] = [
    "fotografia", "video", "drone_footage", "sensor_data",
    "planta_projeto", "art_rrt", "relatorio_tecnico",
    "laudo_laboratorial", "documento_contratual", "registro_eletronico",
    "icp_assinatura", "blockchain_hash",
]


class ForensicLabDomain:
    def __init__(self) -> None:
        self._laudos: dict[str, dict] = {}
        self._custody_chains: dict[str, list[dict]] = {}

    # ── Perícia / Laudo ───────────────────────────────────────────────────────

    def open_pericia(
        self,
        pericia_type: str,
        requester: str,
        subject: str,
        location: str | None = None,
        linked_process_id: str | None = None,
        perito_name: str | None = None,
    ) -> dict:
        lid = f"LAU-{uuid4().hex[:8].upper()}"
        laudo = {
            "laudo_id": lid,
            "pericia_type": pericia_type,
            "requester": requester,
            "subject": subject,
            "location": location,
            "linked_process_id": linked_process_id,
            "perito": perito_name,
            "status": "aguardando_pericia",
            "findings": [],
            "evidence_items": [],
            "timeline": [{"event": "abertura", "at": utc_now()}],
            "opened_at": utc_now(),
            "concluded_at": None,
        }
        self._laudos[lid] = laudo
        self._custody_chains[lid] = []
        return laudo

    def add_finding(self, laudo_id: str, finding: str, severity: str = "informational") -> dict:
        """Adiciona constatação ao laudo (low / medium / high / critical)."""
        laudo = self._get_laudo(laudo_id)
        laudo["findings"].append({
            "finding_id": f"FND-{uuid4().hex[:4].upper()}",
            "finding": finding,
            "severity": severity,
            "recorded_at": utc_now(),
        })
        return laudo

    def add_evidence_item(
        self,
        laudo_id: str,
        description: str,
        evidence_type: str,
        source_system: str,
        hash_sha256: str | None = None,
        icp_signed: bool = False,
        blockchain_anchor: str | None = None,
    ) -> dict:
        laudo = self._get_laudo(laudo_id)
        item = {
            "item_id": f"EVI-{uuid4().hex[:6].upper()}",
            "description": description,
            "evidence_type": evidence_type,
            "source_system": source_system,
            "hash_sha256": hash_sha256,
            "icp_signed": icp_signed,
            "blockchain_anchor": blockchain_anchor,
            "added_at": utc_now(),
        }
        laudo["evidence_items"].append(item)
        # Registra entrada na custódia
        self._custody_chains[laudo_id].append({
            "action": "evidence_added",
            "item_id": item["item_id"],
            "at": utc_now(),
        })
        return item

    def conclude_laudo(self, laudo_id: str, conclusion: str, perito: str | None = None) -> dict:
        laudo = self._get_laudo(laudo_id)
        laudo["status"] = "concluido"
        laudo["conclusion"] = conclusion
        laudo["concluded_at"] = utc_now()
        laudo["timeline"].append({"event": "conclusão", "perito": perito, "at": utc_now()})
        if perito:
            laudo["perito"] = perito
        return laudo

    # ── Cadeia de Custódia ────────────────────────────────────────────────────

    def transfer_custody(self, laudo_id: str, from_: str, to: str, reason: str) -> dict:
        self._get_laudo(laudo_id)
        entry = {
            "action": "custody_transfer",
            "from": from_,
            "to": to,
            "reason": reason,
            "at": utc_now(),
        }
        self._custody_chains[laudo_id].append(entry)
        return entry

    def get_custody_chain(self, laudo_id: str) -> list[dict]:
        self._get_laudo(laudo_id)
        return self._custody_chains[laudo_id]

    # ── Timeline Técnica ──────────────────────────────────────────────────────

    def add_timeline_event(self, laudo_id: str, event: str, metadata: dict | None = None) -> dict:
        laudo = self._get_laudo(laudo_id)
        entry = {"event": event, "metadata": metadata or {}, "at": utc_now()}
        laudo["timeline"].append(entry)
        return entry

    def reconstruct_event_timeline(self, laudo_id: str) -> dict:
        laudo = self._get_laudo(laudo_id)
        return {
            "laudo_id": laudo_id,
            "subject": laudo["subject"],
            "timeline": sorted(laudo["timeline"], key=lambda x: x["at"]),
            "findings_count": len(laudo["findings"]),
            "evidence_count": len(laudo["evidence_items"]),
            "custody_entries": len(self._custody_chains[laudo_id]),
            "reconstructed_at": utc_now(),
        }

    # ── Consultas ─────────────────────────────────────────────────────────────

    def get_laudo(self, laudo_id: str) -> dict:
        return self._get_laudo(laudo_id)

    def list_laudos(self, status: str | None = None) -> list[dict]:
        laudos = list(self._laudos.values())
        if status:
            return [l for l in laudos if l["status"] == status]
        return laudos

    def list_pericia_types(self) -> list[str]:
        return PERICIA_TYPES

    def list_evidence_types(self) -> list[str]:
        return EVIDENCE_TYPES

    # ── helper ────────────────────────────────────────────────────────────────

    def _get_laudo(self, laudo_id: str) -> dict:
        l = self._laudos.get(laudo_id)
        if not l:
            raise KeyError(f"Laudo {laudo_id} não encontrado")
        return l
