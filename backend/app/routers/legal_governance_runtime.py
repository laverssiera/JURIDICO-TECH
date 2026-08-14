from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas import ComplianceCheckRequest
from app.services.legal_core import legal_core_engine
from runtime.legal.governance.mission_legal_runtime import MissionLegalRuntime


router = APIRouter()
_runtime = MissionLegalRuntime()


class ContractGenerateRequest(BaseModel):
    contract_type: str = Field(..., min_length=3)
    parties: list[str] = Field(default_factory=list)
    objective: str = Field(..., min_length=3)
    jurisdiction: str = Field(default="BR", min_length=2)
    context: dict[str, Any] = Field(default_factory=dict)


class GovernanceComplianceRequest(BaseModel):
    jurisdiction: str = Field(default="BR", min_length=2)
    contract_type: str = Field(..., min_length=3)
    obligations: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    controls: dict[str, bool] = Field(default_factory=dict)


class ClaimItem(BaseModel):
    category: str = Field(default="general", min_length=2)
    severity: str = Field(default="low", min_length=3)
    amount: float = 0.0


class RiskAnalyzeRequest(BaseModel):
    jurisdiction: str = Field(default="BR", min_length=2)
    contract_type: str = Field(..., min_length=3)
    obligations: list[str] = Field(default_factory=list)
    controls: dict[str, bool] = Field(default_factory=dict)
    claims: list[ClaimItem] = Field(default_factory=list)


class LegalImplicationsRequest(BaseModel):
    affected_contracts: list[dict[str, Any]] | list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)
    regulatory_risk: bool | str | dict[str, Any] = False
    liability: bool | str | dict[str, Any] = False
    force_majeure: bool | str | dict[str, Any] = False
    insurance: bool | str | dict[str, Any] = False
    compliance: bool | str | dict[str, Any] = False
    licensing: bool | str | dict[str, Any] = False


class LegalAssuranceRequest(BaseModel):
    contract_type: str = Field(..., min_length=3)
    parties: list[str] = Field(default_factory=list)
    objective: str = Field(..., min_length=3)
    jurisdiction: str = Field(default="BR", min_length=2)
    context: dict[str, Any] = Field(default_factory=dict)
    obligations: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    controls: dict[str, bool] = Field(default_factory=dict)
    liability: bool | str | dict[str, Any] = False
    insurance: bool | str | dict[str, Any] = False


class WorldwideComplianceSimulationRequest(BaseModel):
    scenario: str = Field(default="baseline", pattern="^(baseline|critical)$")


class ContinentalLegalStateRequest(BaseModel):
    countries: list[str] = Field(..., min_length=1)
    contracts: list[dict[str, Any]] = Field(default_factory=list)
    assets: list[dict[str, Any]] = Field(default_factory=list)
    data: list[dict[str, Any]] = Field(default_factory=list)
    investments: list[dict[str, Any]] = Field(default_factory=list)
    suppliers: list[dict[str, Any]] = Field(default_factory=list)
    infrastructure: list[dict[str, Any]] = Field(default_factory=list)
    controls: dict[str, bool] = Field(default_factory=dict)
    sectors: list[str] = Field(default_factory=list)
    operation_id: str | None = None


@router.post("/legal/contract/generate")
def legal_contract_generate(request: ContractGenerateRequest) -> dict[str, Any]:
    return _runtime.generate_contract(
        contract_type=request.contract_type,
        parties=request.parties,
        objective=request.objective,
        jurisdiction=request.jurisdiction,
        context=request.context,
    )


@router.post("/legal/compliance/check")
def legal_compliance_check(request: dict[str, Any]) -> dict[str, Any]:
    # Keep backward compatibility with existing Legal Core payload contract.
    legacy_keys = {"user_id", "role", "action", "module", "entity_id"}
    if legacy_keys.issubset(set(request.keys())):
        return legal_core_engine.check_compliance(ComplianceCheckRequest.model_validate(request))

    payload = GovernanceComplianceRequest.model_validate(request)
    return _runtime.check_compliance(
        jurisdiction=payload.jurisdiction,
        contract_type=payload.contract_type,
        obligations=payload.obligations,
        controls=payload.controls,
        frameworks=payload.frameworks,
    )


@router.post("/legal/compliance/worldwide-simulation")
def legal_compliance_worldwide_simulation(
    request: WorldwideComplianceSimulationRequest,
) -> dict[str, Any]:
    if request.scenario == "critical":
        payload = {
            "jurisdiction": "GLOBAL",
            "contract_type": "MSA",
            "obligations": [
                "data_protection",
                "sanctions_screening",
                "audit_trail",
                "incident_response",
                "dispute_clause",
            ],
            "controls": {
                "data_protection": False,
                "sanctions_screening": False,
                "audit_trail": False,
                "incident_response": False,
                "dispute_clause": False,
            },
            "claims": [
                {"category": "cross_border_sanctions", "severity": "high", "amount": 1000000.0},
                {"category": "privacy_breach", "severity": "high", "amount": 500000.0},
                {"category": "contract_nullity", "severity": "high", "amount": 250000.0},
            ],
        }
    else:
        payload = {
            "jurisdiction": "GLOBAL",
            "contract_type": "MSA",
            "obligations": [
                "data_protection",
                "sanctions_screening",
                "audit_trail",
                "incident_response",
            ],
            "controls": {
                "data_protection": True,
                "sanctions_screening": True,
                "audit_trail": False,
                "incident_response": True,
            },
            "claims": [
                {"category": "privacy_breach", "severity": "high", "amount": 0.0},
                {"category": "sla_dispute", "severity": "medium", "amount": 0.0},
            ],
        }

    risk_bundle = _runtime.analyze_risk(
        jurisdiction=payload["jurisdiction"],
        contract_type=payload["contract_type"],
        obligations=payload["obligations"],
        controls=payload["controls"],
        claims=payload["claims"],
    )

    return {
        "simulation": "worldwide_compliance",
        "scenario": request.scenario,
        "compliance": risk_bundle["compliance"],
        "regulatory": risk_bundle["regulatory"],
        "risk": risk_bundle["risk"],
        "claims": risk_bundle["claims"],
    }


@router.post("/legal/risk/analyze")
def legal_risk_analyze(request: RiskAnalyzeRequest) -> dict[str, Any]:
    return _runtime.analyze_risk(
        jurisdiction=request.jurisdiction,
        contract_type=request.contract_type,
        obligations=request.obligations,
        controls=request.controls,
        claims=[item.model_dump() for item in request.claims],
    )


@router.post("/legal/implications")
def legal_implications(request: LegalImplicationsRequest) -> dict[str, Any]:
    return _runtime.assess_implications(request.model_dump())


@router.post("/legal/assurance")
def legal_assurance(request: LegalAssuranceRequest) -> dict[str, Any]:
    return _runtime.assess_assurance(request.model_dump())


@router.get("/legal/state")
def legal_state() -> dict[str, Any]:
    return _runtime.state()


@router.get("/legal/waves/43")
def legal_wave_43() -> dict[str, Any]:
    return _runtime.wave_43()


@router.post("/legal/continental/state")
def continental_legal_state(request: ContinentalLegalStateRequest) -> dict[str, Any]:
    return _runtime.continental_state(**request.model_dump())
