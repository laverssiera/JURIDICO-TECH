"""
LICEU 6.0 — Router: Tax Intelligence
Regime tributário, estimativa de carga, risco fiscal, incentivos.
"""
from fastapi import APIRouter, HTTPException

from app.legal_core.tax import TaxIntelligenceDomain

router = APIRouter()
_tax = TaxIntelligenceDomain()


@router.post("/regime/suggest")
def suggest_regime(payload: dict) -> dict:
    """
    John Tributário sugere regime mais vantajoso.
    Payload: { annual_revenue, entity_type, has_patrimonio_afetacao?, high_deductible_costs? }
    """
    try:
        return _tax.suggest_regime(
            annual_revenue=float(payload["annual_revenue"]),
            entity_type=payload["entity_type"],
            has_patrimonio_afetacao=payload.get("has_patrimonio_afetacao", False),
            high_deductible_costs=payload.get("high_deductible_costs", False),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/burden/estimate")
def estimate_burden(payload: dict) -> dict:
    """
    Estima carga tributária para um regime.
    Payload: { regime, annual_revenue, annual_profit?, annual_cost? }
    """
    try:
        return _tax.estimate_tax_burden(
            regime=payload["regime"],
            annual_revenue=float(payload["annual_revenue"]),
            annual_profit=payload.get("annual_profit"),
            annual_cost=payload.get("annual_cost"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/risk")
def tax_risk(payload: dict) -> dict:
    """Checagem de riscos tributários para a entidade."""
    return _tax.tax_risk_check(payload)


@router.get("/incentivos")
def list_incentivos() -> dict:
    return {"incentivos": _tax.list_incentivos()}


@router.get("/impostos-construcao")
def list_construction_taxes() -> dict:
    return {"taxes": _tax.list_construction_taxes()}
