"""
LICEU 6.0 — Domain: Litigation Engine
Gestão de processos judiciais, prazos, peças, perícias, pareceres, evidências
e analytics jurídicos. Integração com tribunais (PJe, e-SAJ, Projudi).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


TRIBUNAL_APIS: dict[str, dict] = {
    "PJe": {
        "name": "Processo Judicial Eletrônico",
        "url_base": "https://pje.jus.br/",
        "tribunais": ["TJ", "TRF", "TRT", "STJ", "STF"],
        "status": "integration_ready",
    },
    "e-SAJ": {
        "name": "Sistema de Automação da Justiça (TJSP / TJSC)",
        "url_base": "https://esaj.tjsp.jus.br/",
        "tribunais": ["TJSP", "TJSC"],
        "status": "integration_ready",
    },
    "Projudi": {
        "name": "Projudi (TJPR / TJBA / TJAM)",
        "url_base": "https://projudi.tjpr.jus.br/",
        "tribunais": ["TJPR", "TJBA", "TJAM"],
        "status": "integration_ready",
    },
}

PROCESS_PHASES: list[str] = [
    "petição_inicial",
    "citação",
    "contestação",
    "réplica",
    "instrução",
    "alegações_finais",
    "sentença",
    "recurso",
    "trânsito_em_julgado",
    "execução",
    "encerrado",
]

PROCESS_TYPES: list[str] = [
    "ação_cobrança", "ação_indenização", "rescisão_contratual",
    "execução_contrato", "ação_trabalhista", "mandado_segurança",
    "ação_ambiental", "ação_societária", "perícia_judicial", "arbitragem",
]


class LitigationDomain:
    def __init__(self) -> None:
        self._processes: dict[str, dict] = {}
        self._deadlines: list[dict] = {}
        self._evidence: dict[str, list[dict]] = {}
        self._pieces: dict[str, list[dict]] = {}

    # ── Processo ──────────────────────────────────────────────────────────────

    def open_process(
        self,
        process_type: str,
        plaintiff: str,
        defendant: str,
        description: str,
        tribunal: str,
        tribunal_system: str = "PJe",
        amount_in_dispute: float = 0.0,
        process_number: str | None = None,
    ) -> dict:
        pid = f"PROC-{uuid4().hex[:8].upper()}"
        proc = {
            "process_id": pid,
            "process_number": process_number,
            "process_type": process_type,
            "plaintiff": plaintiff,
            "defendant": defendant,
            "description": description,
            "tribunal": tribunal,
            "tribunal_system": tribunal_system,
            "amount_in_dispute": amount_in_dispute,
            "phase": PROCESS_PHASES[0],
            "timeline": [{"phase": PROCESS_PHASES[0], "at": utc_now()}],
            "status": "active",
            "opened_at": utc_now(),
        }
        self._processes[pid] = proc
        self._evidence[pid] = []
        self._pieces[pid] = []
        return proc

    def advance_phase(self, process_id: str) -> dict:
        proc = self._get(process_id)
        idx = PROCESS_PHASES.index(proc["phase"])
        if idx >= len(PROCESS_PHASES) - 1:
            raise ValueError("Processo já encerrado")
        proc["phase"] = PROCESS_PHASES[idx + 1]
        proc["timeline"].append({"phase": proc["phase"], "at": utc_now()})
        if proc["phase"] == "encerrado":
            proc["status"] = "closed"
        return proc

    def get_process(self, process_id: str) -> dict:
        return self._get(process_id)

    def list_processes(self, status: str | None = None) -> list[dict]:
        procs = list(self._processes.values())
        if status:
            procs = [p for p in procs if p["status"] == status]
        return procs

    # ── Prazos ────────────────────────────────────────────────────────────────

    def add_deadline(
        self,
        process_id: str,
        description: str,
        due_date: str,
        type_: str = "processual",
        assignee: str | None = None,
    ) -> dict:
        self._get(process_id)
        dl = {
            "deadline_id": f"DL-{uuid4().hex[:6].upper()}",
            "process_id": process_id,
            "description": description,
            "due_date": due_date,
            "type": type_,
            "assignee": assignee,
            "status": "pending",
            "created_at": utc_now(),
        }
        self._deadlines.setdefault(process_id, []).append(dl)
        return dl

    def list_deadlines(self, process_id: str) -> list[dict]:
        return self._deadlines.get(process_id, [])

    def overdue_deadlines(self) -> list[dict]:
        now = datetime.now(UTC).date().isoformat()
        result = []
        for dls in self._deadlines.values():
            for dl in dls:
                if dl["due_date"] < now and dl["status"] == "pending":
                    result.append(dl)
        return result

    # ── Peças Processuais ─────────────────────────────────────────────────────

    def add_piece(
        self,
        process_id: str,
        piece_type: str,
        content_summary: str,
        author: str,
    ) -> dict:
        self._get(process_id)
        piece = {
            "piece_id": f"PC-{uuid4().hex[:6].upper()}",
            "process_id": process_id,
            "piece_type": piece_type,
            "content_summary": content_summary,
            "author": author,
            "created_at": utc_now(),
        }
        self._pieces[process_id].append(piece)
        return piece

    def list_pieces(self, process_id: str) -> list[dict]:
        return self._pieces.get(process_id, [])

    # ── Evidências ────────────────────────────────────────────────────────────

    def add_evidence(
        self,
        process_id: str,
        description: str,
        evidence_type: str,
        source: str,
        hash_sha256: str | None = None,
    ) -> dict:
        self._get(process_id)
        ev = {
            "evidence_id": f"EV-{uuid4().hex[:6].upper()}",
            "process_id": process_id,
            "description": description,
            "evidence_type": evidence_type,
            "source": source,
            "hash_sha256": hash_sha256,
            "chain_of_custody": [{"holder": source, "at": utc_now()}],
            "added_at": utc_now(),
        }
        self._evidence[process_id].append(ev)
        return ev

    def list_evidence(self, process_id: str) -> list[dict]:
        return self._evidence.get(process_id, [])

    # ── Analytics ─────────────────────────────────────────────────────────────

    def litigation_analytics(self) -> dict:
        procs = list(self._processes.values())
        by_type: dict[str, int] = {}
        by_tribunal: dict[str, int] = {}
        total_exposure = 0.0
        for p in procs:
            by_type[p["process_type"]] = by_type.get(p["process_type"], 0) + 1
            by_tribunal[p["tribunal"]] = by_tribunal.get(p["tribunal"], 0) + 1
            total_exposure += p.get("amount_in_dispute", 0.0)
        active = sum(1 for p in procs if p["status"] == "active")
        return {
            "total_processes": len(procs),
            "active": active,
            "closed": len(procs) - active,
            "total_financial_exposure": total_exposure,
            "by_type": by_type,
            "by_tribunal": by_tribunal,
            "overdue_deadlines": len(self.overdue_deadlines()),
            "generated_at": utc_now(),
        }

    def list_tribunal_integrations(self) -> list[dict]:
        return list(TRIBUNAL_APIS.values())

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get(self, process_id: str) -> dict:
        p = self._processes.get(process_id)
        if not p:
            raise KeyError(f"Processo {process_id} não encontrado")
        return p
