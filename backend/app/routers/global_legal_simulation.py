from fastapi import APIRouter, HTTPException

from app.integration.event_bus import event_bus
from app.legal_core.global_legal_simulation import GlobalLegalSimulationDomain

router = APIRouter()
_sim = GlobalLegalSimulationDomain()


@router.post("/supplier-failure")
def simulate_supplier_failure(payload: dict) -> dict:
    try:
        result = _sim.simulate_supplier_failure(
            supplier_id=payload["supplier_id"],
            affected_works=int(payload["affected_works"]),
            affected_contracts=int(payload["affected_contracts"]),
            financial_exposure=float(payload["financial_exposure"]),
            contingency_ready=bool(payload.get("contingency_ready", False)),
        )
        event_bus.publish("simulation.global.executed", result)
        if result.get("risk_level") in ("HIGH", "CRITICAL"):
            event_bus.publish("simulation.global.risk.high", result)
        return result
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/regulatory-change")
def simulate_regulatory_change(payload: dict) -> dict:
    try:
        result = _sim.simulate_regulatory_change(
            regulation_name=payload["regulation_name"],
            impacted_units=payload.get("impacted_units", []),
            adaptation_days=int(payload["adaptation_days"]),
            penalty_estimate=float(payload["penalty_estimate"]),
        )
        event_bus.publish("simulation.global.executed", result)
        if result.get("risk_level") in ("HIGH", "CRITICAL"):
            event_bus.publish("simulation.global.risk.high", result)
        return result
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/")
def list_scenarios(scenario_type: str | None = None) -> dict:
    return {"scenarios": _sim.list_scenarios(scenario_type)}


@router.get("/{scenario_id}")
def get_scenario(scenario_id: str) -> dict:
    try:
        return _sim.get_scenario(scenario_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
