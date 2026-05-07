"""
LICEU 6.0 — Router: Legal NLP + AI Engine
Análise de contratos, extração de cláusulas, geração de documentos,
resumo de processos e comparação de jurisprudência.
"""
from fastapi import APIRouter, HTTPException

from app.legal_core.legal_nlp import LegalNLPDomain

router = APIRouter()
_nlp = LegalNLPDomain()


@router.post("/analyze-contract")
def analyze_contract(payload: dict) -> dict:
    """
    Detecta riscos em texto de contrato.
    Payload: { contract_text: str }
    """
    text = payload.get("contract_text", "")
    if not text:
        raise HTTPException(status_code=422, detail="contract_text é obrigatório")
    return _nlp.analyze_contract_text(text)


@router.post("/extract-clauses")
def extract_clauses(payload: dict) -> dict:
    """
    Extrai cláusulas-chave de texto contratual.
    Payload: { contract_text: str }
    """
    text = payload.get("contract_text", "")
    if not text:
        raise HTTPException(status_code=422, detail="contract_text é obrigatório")
    return _nlp.extract_key_clauses(text)


@router.get("/templates")
def list_templates() -> dict:
    return {"templates": _nlp.list_templates()}


@router.post("/generate-document")
def generate_document(payload: dict) -> dict:
    """
    Gera documento jurídico a partir de template.
    Payload: { template_id: str, variables: dict }
    """
    template_id = payload.get("template_id")
    variables = payload.get("variables", {})
    if not template_id:
        raise HTTPException(status_code=422, detail="template_id é obrigatório")
    result = _nlp.generate_document(template_id, variables)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/summarize-process")
def summarize_process(payload: dict) -> dict:
    return _nlp.summarize_process(payload)


@router.post("/compare-jurisprudence")
def compare_jurisprudence(payload: dict) -> dict:
    """
    Compara caso com precedentes.
    Payload: { issue_description: str, precedents: list[dict] }
    """
    issue = payload.get("issue_description", "")
    precedents = payload.get("precedents", [])
    if not issue:
        raise HTTPException(status_code=422, detail="issue_description é obrigatório")
    return _nlp.compare_jurisprudence(issue, precedents)
