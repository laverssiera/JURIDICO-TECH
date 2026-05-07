"""
JOHN JURÍDICO — General Counsel Cognitivo — LICEU 6.0
Interpreta riscos, analisa contratos, valida operações, bloqueia fluxos perigosos,
sugere cláusulas, educa equipes, prevê litígios e opera arbitragem.
"""
from fastapi import APIRouter, HTTPException

from app.services.contract_engine import analyze_contract
from app.integration.mae_bridge import send_to_mae
from app.schemas import JohnRiskRequest
from app.services.legal_core import legal_core_engine
from app.services.preventive_module import preventive_module
from app.services.contract_learning import contract_learning
from app.services.arbitration_service import arbitration_service
from app.legal_core.legal_ai import LegalAIDomain
from app.legal_core.contracts import ContractDomain
from app.legal_core.jurisprudence import JurisprudenceDomain

router = APIRouter()

_ai = LegalAIDomain()
_contracts = ContractDomain()
_jurisprudence = JurisprudenceDomain()


# ── Decisão e Risco ───────────────────────────────────────────────────────────

def john_legal_decision(payload: dict) -> dict:
    result = analyze_contract(payload)
    if result.get("risk") == "alto":
        return send_to_mae("/integration/mae/legal-risk", result)
    return result


@router.post("/decision")
def legal_decision(payload: dict) -> dict:
    return john_legal_decision(payload)


@router.post("/risk")
def legal_risk(payload: JohnRiskRequest) -> dict:
    return legal_core_engine.assess_legal_risk(payload)


# ── Módulo Preventivo — Score Jurídico Vivo ───────────────────────────────────

@router.post("/score")
def score_entity(
    entity_id: str,
    entity_type: str,
    active_risks: list[str],
    context: dict | None = None,
) -> dict:
    """Score jurídico vivo para qualquer entidade do ecossistema."""
    return preventive_module.score_entity(entity_id, entity_type, active_risks, context)


@router.get("/score/factors")
def list_risk_factors(scope: str | None = None) -> dict:
    """Lista todos os fatores de risco jurídico disponíveis."""
    return {"factors": preventive_module.available_risk_factors(scope)}


@router.get("/score/history")
def score_history() -> dict:
    return {"history": preventive_module.score_history()}


# ── Cláusulas e Contratos ─────────────────────────────────────────────────────

@router.get("/clauses/suggest")
def suggest_clauses(tags: str) -> dict:
    """Sugere cláusulas relevantes para contexto fornecido (tags separadas por vírgula)."""
    tag_list = [t.strip() for t in tags.split(",")]
    return {"clauses": _contracts.suggest_clauses(tag_list)}


@router.post("/clauses/draft")
def draft_contract(payload: dict) -> dict:
    """Gera rascunho de contrato com cláusulas blindadas."""
    try:
        return _contracts.draft_contract(
            title=payload["title"],
            parties=payload["parties"],
            object_description=payload["object"],
            value=payload.get("value", 0.0),
            tags=payload.get("tags", []),
            clause_ids=payload.get("clause_ids"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


# ── Educação Jurídica ─────────────────────────────────────────────────────────

@router.get("/educate/{topic}")
def educate(topic: str) -> dict:
    """John explica um tópico jurídico ao ecossistema."""
    return _ai.educate(topic)


@router.post("/interpret-risk")
def interpret_risk(risk_score: int, entity_type: str, issues: list[str]) -> dict:
    """John interpreta um score de risco e recomenda ações."""
    return _ai.interpret_risk(risk_score, entity_type, issues)


@router.post("/action-plan")
def action_plan(issues: list[str]) -> dict:
    """John gera plano de ação corretiva para uma lista de não-conformidades."""
    return {"action_plan": _ai.suggest_action_plan(issues)}


# ── Aprendizado Contratual ────────────────────────────────────────────────────

@router.post("/learning/event")
def record_learning_event(payload: dict) -> dict:
    """Registra evento de aprendizado (litígio, falha, auditoria, feedback)."""
    try:
        return contract_learning.record_event(
            source=payload["source"],
            issue_type=payload["issue_type"],
            context_tags=payload.get("context_tags", []),
            details=payload.get("details", ""),
            contract_id=payload.get("contract_id"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/learning/reinforcements")
def list_reinforcements(status: str | None = None) -> dict:
    return {"reinforcements": contract_learning.list_reinforcements(status)}


@router.post("/learning/reinforcements/{reinforcement_id}/approve")
def approve_reinforcement(reinforcement_id: str) -> dict:
    try:
        return contract_learning.approve_reinforcement(reinforcement_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/learning/stats")
def learning_stats() -> dict:
    return contract_learning.learning_stats()


# ── Arbitragem ───────────────────────────────────────────────────────────────

@router.post("/arbitration/open")
def open_arbitration_case(payload: dict) -> dict:
    try:
        return arbitration_service.open_case(
            claimant=payload["claimant"],
            respondent=payload["respondent"],
            contract_id=payload["contract_id"],
            dispute_description=payload["dispute_description"],
            amount_in_dispute=payload.get("amount_in_dispute", 0.0),
            chamber_id=payload.get("chamber_id", "CAMARB"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/arbitration/{case_id}/advance")
def advance_arbitration_phase(case_id: str) -> dict:
    try:
        return arbitration_service.advance_phase(case_id)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/arbitration/{case_id}/award")
def issue_arbitration_award(case_id: str, payload: dict) -> dict:
    try:
        return arbitration_service.issue_award(
            case_id,
            decision=payload["decision"],
            awarded_amount=payload.get("awarded_amount"),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/arbitration/{case_id}")
def get_arbitration_case(case_id: str) -> dict:
    try:
        return arbitration_service.get_case(case_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/arbitration")
def list_arbitration_cases() -> dict:
    return {"cases": arbitration_service.list_cases()}


@router.get("/arbitration/chambers/list")
def list_chambers() -> dict:
    return {"chambers": arbitration_service.list_chambers()}


# ── Jurisprudência e Normas ───────────────────────────────────────────────────

@router.get("/norms")
def search_norms(tags: str) -> dict:
    tag_list = [t.strip() for t in tags.split(",")]
    return {"norms": _jurisprudence.search_norms(tag_list)}


@router.post("/jurisprudence/add")
def add_precedent(payload: dict) -> dict:
    try:
        return _jurisprudence.add_precedent(
            title=payload["title"],
            court=payload["court"],
            decision=payload["decision"],
            tags=payload.get("tags", []),
            case_number=payload.get("case_number"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/jurisprudence/search")
def search_precedents(tags: str) -> dict:
    tag_list = [t.strip() for t in tags.split(",")]
    return {"precedents": _jurisprudence.search_precedents(tag_list)}
