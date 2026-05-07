from __future__ import annotations

from fastapi import APIRouter

from app.schemas import (
    AuditAppendRequest,
    BypassCheckRequest,
    BypassProtectRequest,
    ContractCreateV2Request,
    ContractCustodyVerifyRequest,
    ContractDigitalSignRequest,
    ContractSignV2Request,
    ContractSignatureVerifyRequest,
    ContractStatusActionRequest,
    ContractTemplateCreateRequest,
    ContractVersionCreateRequest,
    ExternalRiskIngestRequest,
    JohnDecisionRequest,
    KanbanStageUpdateRequest,
    LegalEntityUpsertRequest,
    LegalLearningCreateRequest,
    LegalRoleGrantRequest,
    LegalTaskAutoDecisionRequest,
    LegalTaskCreateRequest,
    LegalUserUpsertRequest,
    OverrideRequest,
    RiskAnalysisRequest,
    SLAUpsertRequest,
)
from app.services.legal_ecosystem import legal_ecosystem_service


router = APIRouter(prefix="/legal", tags=["Legal Admin"])


@router.post("/identity/entities")
def upsert_legal_entity(request: LegalEntityUpsertRequest) -> dict:
    return legal_ecosystem_service.upsert_legal_entity(request)


@router.post("/identity/users")
def upsert_legal_user(request: LegalUserUpsertRequest) -> dict:
    return legal_ecosystem_service.upsert_legal_user(request)


@router.post("/rbac/grant")
def grant_legal_role(request: LegalRoleGrantRequest) -> dict:
    return legal_ecosystem_service.grant_role(request)


@router.get("/rbac/{user_id}")
def list_legal_roles(user_id: str) -> dict:
    return legal_ecosystem_service.list_roles(user_id)


@router.post("/templates")
def create_contract_template(request: ContractTemplateCreateRequest) -> dict:
    return legal_ecosystem_service.create_template(request)


@router.get("/templates")
def list_contract_templates() -> dict:
    return legal_ecosystem_service.list_templates()


@router.post("/contracts/v2")
def create_contract_v2(request: ContractCreateV2Request) -> dict:
    return legal_ecosystem_service.create_contract(request)


@router.post("/contracts/v2/{contract_id}/version")
def version_contract_v2(contract_id: str, request: ContractVersionCreateRequest) -> dict:
    if request.contract_id != contract_id:
        request = ContractVersionCreateRequest(
            contract_id=contract_id,
            content=request.content,
            author_id=request.author_id,
            reason=request.reason,
        )
    return legal_ecosystem_service.create_contract_version(request)


@router.post("/contracts/v2/{contract_id}/status")
def change_contract_status(contract_id: str, request: ContractStatusActionRequest) -> dict:
    return legal_ecosystem_service.change_contract_status(contract_id, request)


@router.post("/contracts/v2/{contract_id}/sign")
def sign_contract_v2(contract_id: str, request: ContractSignV2Request) -> dict:
    return legal_ecosystem_service.sign_contract(contract_id, request)


@router.post("/contracts/v2/{contract_id}/digital-sign")
def digital_sign_contract_v2(contract_id: str, request: ContractDigitalSignRequest) -> dict:
    return legal_ecosystem_service.digital_sign_contract(contract_id, request)


@router.post("/contracts/v2/{contract_id}/verify-signature")
def verify_contract_signature_v2(contract_id: str, request: ContractSignatureVerifyRequest) -> dict:
    return legal_ecosystem_service.verify_contract_signature(contract_id, request)


@router.get("/contracts/v2/{contract_id}/custody")
def export_contract_custody_v2(contract_id: str) -> dict:
    return legal_ecosystem_service.export_contract_custody(contract_id)


@router.post("/contracts/v2/{contract_id}/verify-custody")
def verify_contract_custody_v2(contract_id: str, request: ContractCustodyVerifyRequest) -> dict:
    return legal_ecosystem_service.verify_contract_custody(contract_id, request)


@router.get("/contracts")
def list_contracts_admin() -> dict:
    return legal_ecosystem_service.list_admin_contracts()


@router.post("/bypass/protect")
def protect_commission(request: BypassProtectRequest) -> dict:
    return legal_ecosystem_service.protect_commission(request)


@router.post("/bypass/check")
def check_bypass_risk(request: BypassCheckRequest) -> dict:
    return legal_ecosystem_service.check_bypass_risk(request)


@router.post("/risk/analyze")
def analyze_risk(request: RiskAnalysisRequest) -> dict:
    return legal_ecosystem_service.analyze_risk(request)


@router.get("/risk")
def list_risk() -> dict:
    return legal_ecosystem_service.list_admin_risk()


@router.post("/risk/ingest")
def ingest_external_risk(request: ExternalRiskIngestRequest) -> dict:
    return legal_ecosystem_service.ingest_external_risk(request)


@router.get("/risk/center")
def risk_center_snapshot() -> dict:
    return legal_ecosystem_service.risk_center_snapshot()


@router.post("/audit/immutable")
def append_immutable_audit(request: AuditAppendRequest) -> dict:
    return legal_ecosystem_service.append_audit(request)


@router.get("/audit/immutable")
def list_immutable_audit() -> dict:
    return legal_ecosystem_service.list_admin_audit()


@router.post("/sla")
def upsert_sla(request: SLAUpsertRequest) -> dict:
    return legal_ecosystem_service.upsert_sla(request)


@router.post("/tasks")
def create_task(request: LegalTaskCreateRequest) -> dict:
    return legal_ecosystem_service.create_task(request)


@router.get("/tasks")
def list_tasks() -> dict:
    return legal_ecosystem_service.list_tasks()


@router.get("/kanban")
def kanban_snapshot() -> dict:
    return legal_ecosystem_service.kanban_snapshot()


@router.post("/tasks/auto-decision")
def auto_decide_task(request: LegalTaskAutoDecisionRequest) -> dict:
    return legal_ecosystem_service.auto_decide_task(request)


@router.post("/tasks/{task_id}/stage")
def update_task_stage(task_id: str, request: KanbanStageUpdateRequest) -> dict:
    return legal_ecosystem_service.update_task_stage(task_id, request)


@router.post("/override")
def create_override(request: OverrideRequest) -> dict:
    return legal_ecosystem_service.create_override(request)


@router.post("/core-dna/analyze")
def core_dna_legal_analyze(request: RiskAnalysisRequest) -> dict:
    return legal_ecosystem_service.process_core_dna_decision(request)


@router.post("/john/decision")
def john_decision_engine(request: JohnDecisionRequest) -> dict:
    return legal_ecosystem_service.john_decision_engine(request)


@router.post("/learning")
def create_learning(request: LegalLearningCreateRequest) -> dict:
    return legal_ecosystem_service.create_learning(request)


@router.get("/learning")
def list_learning() -> dict:
    return legal_ecosystem_service.list_learning()


@router.get("/notifications")
def list_notifications() -> dict:
    return legal_ecosystem_service.list_notifications()
