from fastapi import APIRouter, status
from app.schemas import SPERequest, ContractAuditRequest
from app.services.legal_engine import legal_engine

router = APIRouter()

@router.post("/create-spe", status_code=status.HTTP_201_CREATED)
def create_spe(request: SPERequest) -> dict:
    return legal_engine.create_spe(request)

@router.post("/contract/analyze")
def audit_contract(request: ContractAuditRequest) -> dict:
    return legal_engine.audit_contract(request)


@router.post("/audit/contract")
def audit_contract_legacy(request: ContractAuditRequest) -> dict:
    return legal_engine.audit_contract(request)


@router.get("/norms/alerts")
def get_norm_alerts_legacy() -> dict:
    return legal_engine.get_norm_alerts()

# Endpoints de Serviços Jurídicos
# POST /legal/create-scp
# POST /legal/incorporation
# POST /legal/contract/create
# POST /legal/esg/assessment
# POST /legal/consulting/request