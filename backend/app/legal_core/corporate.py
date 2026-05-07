"""
LICEU 6.0 — Domain: Corporate Engine
Abertura de empresas, SPEs, holdings, atas, contratos sociais, cap table e governança societária.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

UTC = timezone.utc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


ENTITY_TYPES = ["ltda", "sa", "spe_ltda", "spe_sa", "scp", "holding", "eireli", "mei"]

OPEN_COMPANY_CHECKLIST: list[dict] = [
    {"step": 1, "action": "Definição do tipo societário e objeto social", "key": "tipo_definido"},
    {"step": 2, "action": "Elaboração do contrato social / estatuto", "key": "contrato_elaborado"},
    {"step": 3, "action": "Pesquisa de viabilidade de nome na Junta Comercial", "key": "viabilidade_nome"},
    {"step": 4, "action": "Registro na Junta Comercial (REGIN/integrador REDESIM)", "key": "junta_registrado"},
    {"step": 5, "action": "Inscrição no CNPJ (RFB)", "key": "cnpj_obtido"},
    {"step": 6, "action": "Inscrição Estadual (IE) — se necessário", "key": "ie_obtida"},
    {"step": 7, "action": "Inscrição Municipal (ISS)", "key": "im_obtida"},
    {"step": 8, "action": "Alvará de funcionamento", "key": "alvara_funcionamento"},
    {"step": 9, "action": "Abertura de conta bancária PJ", "key": "conta_bancaria"},
    {"step": 10, "action": "Adesão ao regime tributário", "key": "regime_tributario"},
]

SPE_CHECKLIST: list[dict] = [
    {"step": 1, "action": "Definição do objeto (empreendimento específico)", "key": "objeto_definido"},
    {"step": 2, "action": "Definição dos sócios e participações (cap table)", "key": "cap_table"},
    {"step": 3, "action": "Elaboração do contrato social / estatuto da SPE", "key": "contrato_spe"},
    {"step": 4, "action": "Registro na Junta Comercial", "key": "junta_registrado"},
    {"step": 5, "action": "CNPJ próprio para a SPE", "key": "cnpj_spe"},
    {"step": 6, "action": "Patrimônio de afetação (se incorporação)", "key": "afetacao"},
    {"step": 7, "action": "Adesão ao RET (se incorporação residencial)", "key": "ret_adesao"},
    {"step": 8, "action": "Abertura de conta vinculada ao patrimônio de afetação", "key": "conta_afetacao"},
    {"step": 9, "action": "Registro de atos societários no RCPJ", "key": "rcpj"},
]


class CorporateDomain:
    def __init__(self) -> None:
        self._entities: dict[str, dict] = {}
        self._atas: list[dict] = []
        self._cap_tables: dict[str, list[dict]] = {}

    # ── Abertura de Empresa ───────────────────────────────────────────────────

    def open_company_checklist(self, entity_type: str) -> list[dict]:
        if "spe" in entity_type:
            return SPE_CHECKLIST
        return OPEN_COMPANY_CHECKLIST

    def register_entity(
        self,
        name: str,
        entity_type: str,
        object_description: str,
        partners: list[dict],
        cnpj: str | None = None,
    ) -> dict:
        entity_id = f"ENT-{uuid4().hex[:8].upper()}"
        entity = {
            "entity_id": entity_id,
            "name": name,
            "entity_type": entity_type,
            "object": object_description,
            "partners": partners,
            "cnpj": cnpj,
            "status": "active",
            "registered_at": utc_now(),
            "bylaws_updated_at": utc_now(),
            "compliance_officer": None,
            "data_protection_officer": None,
            "internal_audit": False,
        }
        self._entities[entity_id] = entity
        # Inicializa cap table com base nos sócios
        self._cap_tables[entity_id] = [
            {
                "partner": p["name"],
                "participation_pct": p.get("participation_pct", 0.0),
                "entry_date": utc_now(),
            }
            for p in partners
        ]
        return entity

    def get_entity(self, entity_id: str) -> dict:
        e = self._entities.get(entity_id)
        if not e:
            raise KeyError(f"Entidade {entity_id} não encontrada")
        return e

    def list_entities(self, entity_type: str | None = None) -> list[dict]:
        if entity_type:
            return [e for e in self._entities.values() if e["entity_type"] == entity_type]
        return list(self._entities.values())

    # ── Cap Table ─────────────────────────────────────────────────────────────

    def get_cap_table(self, entity_id: str) -> dict:
        ct = self._cap_tables.get(entity_id, [])
        total = sum(p["participation_pct"] for p in ct)
        return {
            "entity_id": entity_id,
            "shareholders": ct,
            "total_pct": round(total, 4),
            "is_complete": abs(total - 100.0) < 0.01,
        }

    def update_cap_table(
        self,
        entity_id: str,
        partner: str,
        participation_pct: float,
        operation: str = "add",  # "add" | "transfer" | "remove"
    ) -> dict:
        ct = self._cap_tables.setdefault(entity_id, [])
        existing = next((p for p in ct if p["partner"] == partner), None)
        if operation == "remove":
            self._cap_tables[entity_id] = [p for p in ct if p["partner"] != partner]
        elif operation == "transfer" and existing:
            existing["participation_pct"] = participation_pct
            existing["last_transfer"] = utc_now()
        else:
            if existing:
                existing["participation_pct"] += participation_pct
            else:
                ct.append({"partner": partner, "participation_pct": participation_pct, "entry_date": utc_now()})
        return self.get_cap_table(entity_id)

    # ── Atas e Deliberações Societárias ───────────────────────────────────────

    def record_ata(
        self,
        entity_id: str,
        tipo: str,
        pauta: list[str],
        resolucoes: list[str],
        presentes: list[str],
    ) -> dict:
        ata = {
            "ata_id": f"ATA-{uuid4().hex[:8].upper()}",
            "entity_id": entity_id,
            "tipo": tipo,  # "assembleia_geral" | "reuniao_socios" | "conselho_adm"
            "pauta": pauta,
            "resolucoes": resolucoes,
            "presentes": presentes,
            "registrada_at": utc_now(),
            "status": "rascunho",
        }
        self._atas.append(ata)
        return ata

    def list_atas(self, entity_id: str) -> list[dict]:
        return [a for a in self._atas if a["entity_id"] == entity_id]

    # ── Fluxo CEA → SPE → Tokenização ─────────────────────────────────────────

    def spe_tokenization_flow(self, spe_id: str, token_supply: int, price_per_token: float) -> dict:
        entity = self._entities.get(spe_id)
        if not entity:
            raise KeyError(f"SPE {spe_id} não encontrada")
        ct = self.get_cap_table(spe_id)
        return {
            "spe_id": spe_id,
            "spe_name": entity["name"],
            "token_supply": token_supply,
            "price_per_token": price_per_token,
            "market_cap": token_supply * price_per_token,
            "shareholders": ct["shareholders"],
            "tokenization_status": "pending_legal_opinion",
            "required_steps": [
                "Parecer jurídico sobre tokenização",
                "Registro CVM (se necessário — instrução CVM 88)",
                "Auditoria de smart contract",
                "KYC/AML dos investidores",
                "Due diligence patrimonial",
            ],
            "initiated_at": utc_now(),
        }
