from fastapi import APIRouter

from app.schemas import (
    AuditEventRequest,
    BypassDetectionRequest,
    ComplianceCheckRequest,
    ContractCreateRequest,
    ContractLifecycleActionRequest,
    ContractSignRequest,
    ContractVersionRequest,
    DisputeRequest,
    LegalDecisionRequest,
    LegalEventRequest,
    LegalGateRequest,
    LegalLockRequest,
    LegalValidateRequest,
    MatchProposalRequest,
    PaymentAuthorizationRequest,
)
from app.services.legal_core import legal_core_engine


router = APIRouter()
contract_router = APIRouter()


@router.post("/contracts")
def create_contract(request: ContractCreateRequest) -> dict:
    return legal_core_engine.create_contract(request)


@router.post("/contracts/{contract_id}/generate")
def generate_contract(contract_id: str, request: ContractLifecycleActionRequest) -> dict:
    return legal_core_engine.generate_contract(contract_id, request)


@router.post("/contracts/{contract_id}/send")
def send_contract(contract_id: str, request: ContractLifecycleActionRequest) -> dict:
    return legal_core_engine.send_contract(contract_id, request)


@router.post("/contracts/{contract_id}/sign")
def sign_contract(contract_id: str, request: ContractSignRequest) -> dict:
    return legal_core_engine.sign_contract(contract_id, request)


@router.post("/contracts/{contract_id}/lock")
def lock_contract(contract_id: str, request: ContractLifecycleActionRequest) -> dict:
    return legal_core_engine.lock_contract(contract_id, request)


@router.post("/contracts/{contract_id}/execute")
def execute_contract(contract_id: str, request: ContractLifecycleActionRequest) -> dict:
    return legal_core_engine.execute_contract(contract_id, request)


@router.post("/contracts/{contract_id}/breach")
def breach_contract(contract_id: str, request: ContractLifecycleActionRequest) -> dict:
    return legal_core_engine.breach_contract(contract_id, request)


@router.get("/contracts/{contract_id}/status")
def get_contract_status(contract_id: str) -> dict:
    return legal_core_engine.get_contract_status(contract_id)


@router.post("/contracts/{contract_id}/version")
def version_contract(contract_id: str, request: ContractVersionRequest) -> dict:
    return legal_core_engine.version_contract(contract_id, request)


@router.post("/contracts/{contract_id}/rollback/{target_version}")
def rollback_contract(contract_id: str, target_version: int, actor_id: str) -> dict:
    return legal_core_engine.rollback_contract(contract_id, target_version, actor_id)


@router.post("/validate")
def validate_gate(request: LegalValidateRequest) -> dict:
    return legal_core_engine.validate_gate(request)


@router.post("/gate/validate")
def validate_action(request: LegalGateRequest) -> dict:
    return legal_core_engine.validate_action(request)


@router.post("/lock")
def create_lock(request: LegalLockRequest) -> dict:
    return legal_core_engine.create_lock(request)


@router.get("/lock/{entity_id}")
def get_locks(entity_id: str) -> dict:
    return legal_core_engine.get_locks(entity_id)


@router.post("/compliance/check")
def check_compliance(request: ComplianceCheckRequest) -> dict:
    return legal_core_engine.check_compliance(request)


@router.post("/match")
def process_match(request: MatchProposalRequest) -> dict:
    return legal_core_engine.process_match_or_proposal(request)


@router.post("/proposal")
def process_proposal(request: MatchProposalRequest) -> dict:
    return legal_core_engine.process_match_or_proposal(request)


@router.get("/graph/{entity_id}")
def get_graph(entity_id: str) -> dict:
    return legal_core_engine.get_relationships(entity_id)


@router.get("/snapshot/{entity_id}")
def get_snapshot(entity_id: str) -> dict:
    return legal_core_engine.get_snapshot(entity_id)


@router.post("/dispute/resolve")
def resolve_dispute(request: DisputeRequest) -> dict:
    return legal_core_engine.resolve_dispute(request)


@router.post("/decision")
def resolve_legal_decision(request: LegalDecisionRequest) -> dict:
    return legal_core_engine.resolve_legal_decision(request)


@router.post("/payment/authorize")
def authorize_payment(request: PaymentAuthorizationRequest) -> dict:
    return legal_core_engine.authorize_payment(request)


@router.post("/events/consume")
def consume_event(request: LegalEventRequest) -> dict:
    return legal_core_engine.consume_event(request)


@router.post("/bypass/detect")
def detect_bypass(request: BypassDetectionRequest) -> dict:
    return legal_core_engine.detect_bypass(request)


@router.post("/audit/event")
def append_audit_event(request: AuditEventRequest) -> dict:
    return legal_core_engine.append_audit(request)


@router.get("/audit/trail")
def list_audit() -> dict:
    return legal_core_engine.list_audit()


@router.get("/audit")
def list_audit_hub() -> dict:
    return legal_core_engine.list_audit()


@router.get("/fraud/flags")
def list_fraud_flags() -> dict:
    return legal_core_engine.list_fraud_flags()


@contract_router.post("/contract/generate")
def sdk_generate_contract(request: ContractCreateRequest) -> dict:
    contract = legal_core_engine.create_contract(request)
    generated = legal_core_engine.generate_contract(
        contract["contract_id"],
        ContractLifecycleActionRequest(
            actor_id=request.created_by,
            role="LEGAL_ADMIN",
            ip=None,
        ),
    )
    return {
        "contract_id": contract["contract_id"],
        "state": generated["state"],
        "hash": contract["current_hash"],
    }


@contract_router.post("/contract/sign")
def sdk_sign_contract(contract_id: str, request: ContractSignRequest) -> dict:
    return legal_core_engine.sign_contract(contract_id, request)


@contract_router.get("/contract/status")
def sdk_status(contract_id: str) -> dict:
    return legal_core_engine.get_contract_status(contract_id)
