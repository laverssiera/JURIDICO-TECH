from typing import Any, Literal, List

from pydantic import BaseModel, Field


class SPERequest(BaseModel):
    name: str = Field(..., min_length=3)
    partners: List[str] = Field(default_factory=list)
    purpose: str = Field(..., min_length=5)


class ContractAuditRequest(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=20)


class ContractSignedEvent(BaseModel):
    contract_id: str = Field(..., min_length=3)
    monolito_id: str = Field(..., min_length=3)
    spe_name: str = Field(..., min_length=3)
    partners: List[str] = Field(default_factory=list)
    purpose: str = Field(..., min_length=5)


class Finding(BaseModel):
    category: str
    severity: str
    description: str
    recommendation: str


class NormAlert(BaseModel):
    id: str
    title: str
    impact: str
    source: str
    action: str


class ChecklistItem(BaseModel):
    area: str
    status: str
    note: str


ContractState = Literal[
    "draft",
    "generated",
    "sent",
    "signed",
    "locked",
    "executed",
    "rejected",
    "breached",
]


class ContractCreateRequest(BaseModel):
    title: str = Field(..., min_length=3)
    contract_type: str = Field(..., min_length=3)
    lead_id: str = Field(..., min_length=2)
    deal_id: str = Field(..., min_length=2)
    property_id: str = Field(..., min_length=2)
    involved_users: list[str] = Field(default_factory=list)
    created_by: str = Field(..., min_length=2)
    template_context: dict[str, Any] = Field(default_factory=dict)
    broker_id: str | None = None
    owner_id: str | None = None
    commission_amount: float | None = None


class ContractLifecycleActionRequest(BaseModel):
    actor_id: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    ip: str | None = None


class ContractVersionRequest(BaseModel):
    author_id: str = Field(..., min_length=2)
    reason: str = Field(default="update", min_length=3)
    changes: dict[str, Any] = Field(default_factory=dict)


class ContractSignRequest(BaseModel):
    actor_id: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    ip: str = Field(..., min_length=7)
    signature_provider: str = Field(default="internal", min_length=2)


class LegalValidateRequest(BaseModel):
    action: str = Field(..., min_length=3)
    lead_id: str | None = None
    deal_id: str | None = None
    property_id: str | None = None
    user_id: str = Field(..., min_length=2)
    user_role: str = Field(..., min_length=2)


class LegalGateRequest(BaseModel):
    user_id: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    action: str = Field(..., min_length=3)
    module: str = Field(..., min_length=2)
    entity_id: str = Field(..., min_length=2)
    lead_id: str | None = None
    deal_id: str | None = None
    property_id: str | None = None


class LegalLockRequest(BaseModel):
    entity_type: str = Field(..., min_length=2)
    entity_id: str = Field(..., min_length=2)
    lock_type: str = Field(..., min_length=2)
    reason: str = Field(..., min_length=3)
    active: bool = True
    created_by: str = Field(..., min_length=2)


class ComplianceCheckRequest(BaseModel):
    user_id: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    action: str = Field(..., min_length=3)
    module: str = Field(..., min_length=2)
    entity_id: str = Field(..., min_length=2)
    lead_id: str | None = None
    deal_id: str | None = None
    property_id: str | None = None
    property_documents_ok: bool = False


class LegalDecisionRequest(BaseModel):
    conflict_type: str = Field(..., min_length=3)
    lead_id: str | None = None
    deal_id: str | None = None
    property_id: str | None = None
    entity_id: str = Field(..., min_length=2)
    requested_by: str = Field(..., min_length=2)
    brokers: list[str] = Field(default_factory=list)


class PaymentAuthorizationRequest(BaseModel):
    user_id: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    entity_id: str = Field(..., min_length=2)
    deal_id: str = Field(..., min_length=2)
    contract_id: str | None = None


class LegalEventRequest(BaseModel):
    type: Literal["lead_created", "deal_created", "match_generated", "deal_won"]
    payload: dict[str, Any] = Field(default_factory=dict)


class BypassDetectionRequest(BaseModel):
    lead_id: str = Field(..., min_length=2)
    deal_id: str = Field(..., min_length=2)
    property_id: str = Field(..., min_length=2)
    broker_id: str = Field(..., min_length=2)
    owner_id: str | None = None
    entity_id: str = Field(..., min_length=2)
    source: str = Field(default="hub", min_length=2)


class MatchProposalRequest(BaseModel):
    event_name: Literal["match_generated", "simulation_done", "deal_created", "deal_won"]
    lead_id: str = Field(..., min_length=2)
    deal_id: str = Field(..., min_length=2)
    property_id: str = Field(..., min_length=2)
    broker_id: str = Field(..., min_length=2)
    owner_id: str | None = None
    involved_users: list[str] = Field(default_factory=list)
    requested_by: str = Field(..., min_length=2)


class DisputeRequest(BaseModel):
    lead_id: str = Field(..., min_length=2)
    deal_id: str = Field(..., min_length=2)
    property_id: str = Field(..., min_length=2)
    brokers: list[str] = Field(..., min_length=2)


class JohnRiskRequest(BaseModel):
    lead_id: str = Field(..., min_length=2)
    deal_id: str = Field(..., min_length=2)
    property_id: str = Field(..., min_length=2)
    broker_id: str | None = None
    owner_id: str | None = None
    has_nda: bool = False
    has_non_circ: bool = False
    has_intermediation: bool = False
    document_inconsistencies: list[str] = Field(default_factory=list)
    hours_to_expected_signature: int | None = None


class AuditEventRequest(BaseModel):
    user_id: str = Field(..., min_length=2)
    action: str = Field(..., min_length=3)
    ip: str = Field(..., min_length=7)
    identity_key: str = Field(..., min_length=3)
    module: str | None = None
    entity_id: str | None = None
    legal_status: str | None = None


LegalEntityType = Literal["pf", "pj", "monolith"]
LegalRiskLevel = Literal["low", "medium", "high"]
LegalTaskPriority = Literal["low", "medium", "high", "critical"]
LegalRoleName = Literal[
    "JURIDICO_MASTER",
    "JURIDICO_ANALYST",
    "AUDITOR",
    "SYSTEM_AUTOMATION",
]
ContractLifecycleV2 = Literal["draft", "pending", "signed", "active", "completed", "canceled"]


class LegalEntityUpsertRequest(BaseModel):
    entity_ref: str = Field(..., min_length=2)
    entity_type: LegalEntityType
    document: str = Field(..., min_length=3)
    jurisdiction: str = Field(default="BR", min_length=2)
    risk_profile: LegalRiskLevel = "medium"
    metadata: dict[str, Any] = Field(default_factory=dict)


class LegalUserUpsertRequest(BaseModel):
    user_id: str = Field(..., min_length=2)
    legal_entity_id: str = Field(..., min_length=8)
    rbac_subject_id: str | None = None
    email: str | None = None


class LegalRoleGrantRequest(BaseModel):
    user_id: str = Field(..., min_length=2)
    role: LegalRoleName
    granted_by: str = Field(..., min_length=2)


class ContractParty(BaseModel):
    role: Literal["buyer", "seller", "broker", "system"]
    legal_entity_id: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=2)


class ContractTemplateCreateRequest(BaseModel):
    template_key: str = Field(..., min_length=3)
    contract_type: str = Field(..., min_length=3)
    jurisdiction: str = Field(default="BR", min_length=2)
    body: str = Field(..., min_length=20)
    variables: list[str] = Field(default_factory=list)
    created_by: str = Field(..., min_length=2)


class ContractCreateV2Request(BaseModel):
    title: str = Field(..., min_length=3)
    contract_type: str = Field(..., min_length=3)
    template_key: str | None = None
    jurisdiction: str = Field(default="BR", min_length=2)
    parties: list[ContractParty] = Field(..., min_length=2)
    created_by: str = Field(..., min_length=2)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContractVersionCreateRequest(BaseModel):
    contract_id: str = Field(..., min_length=8)
    content: dict[str, Any] = Field(default_factory=dict)
    author_id: str = Field(..., min_length=2)
    reason: str = Field(default="update", min_length=3)


class ContractStatusActionRequest(BaseModel):
    actor_id: str = Field(..., min_length=2)
    role: LegalRoleName
    target_status: ContractLifecycleV2
    reason: str | None = None


class ContractSignV2Request(BaseModel):
    actor_id: str = Field(..., min_length=2)
    role: LegalRoleName
    signature_provider: str = Field(default="internal", min_length=2)


class ContractDigitalSignRequest(BaseModel):
    actor_id: str = Field(..., min_length=2)
    role: LegalRoleName
    signature_provider: str = Field(default="advanced", min_length=2)
    certificate_ref: str = Field(default="ICP-BR-A1", min_length=3)
    validity_days: int = Field(default=365, ge=1, le=3650)


class ContractSignatureVerifyRequest(BaseModel):
    actor_id: str = Field(..., min_length=2)
    at_time: str | None = None


class ContractCustodyVerifyRequest(BaseModel):
    actor_id: str = Field(..., min_length=2)


class BypassProtectRequest(BaseModel):
    lead_id: str = Field(..., min_length=2)
    broker_id: str = Field(..., min_length=2)
    asset_id: str = Field(..., min_length=2)
    commission_owner_id: str = Field(..., min_length=2)
    protected_until: str | None = None


class BypassCheckRequest(BaseModel):
    lead_id: str = Field(..., min_length=2)
    broker_id: str = Field(..., min_length=2)
    asset_id: str = Field(..., min_length=2)
    candidate_broker_id: str = Field(..., min_length=2)
    source_event: str = Field(default="deal.created", min_length=4)


class RiskAnalysisRequest(BaseModel):
    operation_type: str = Field(..., min_length=3)
    deal_id: str | None = None
    actors: list[str] = Field(default_factory=list)
    contract: str | None = None
    amount: float | None = None
    has_documents: bool = True
    user_age_days: int = 365


class ExternalRiskIngestRequest(BaseModel):
    monolith: str = Field(..., min_length=2)
    deal_id: str = Field(..., min_length=2)
    risk_level: LegalRiskLevel
    score: float = Field(..., ge=0, le=1)
    flags: list[str] = Field(default_factory=list)


class AuditAppendRequest(BaseModel):
    event_type: str = Field(..., min_length=3)
    actor_id: str = Field(..., min_length=2)
    target_id: str = Field(..., min_length=2)
    payload: dict[str, Any] = Field(default_factory=dict)


class SLAUpsertRequest(BaseModel):
    event_type: str = Field(..., min_length=3)
    sla_hours: int = Field(..., ge=1, le=240)


class LegalTaskCreateRequest(BaseModel):
    event_type: str = Field(..., min_length=3)
    target_id: str = Field(..., min_length=2)
    created_by: str = Field(..., min_length=2)
    priority: LegalTaskPriority | None = None
    risk_level: LegalRiskLevel | None = None


class LegalTaskAutoDecisionRequest(BaseModel):
    event_type: str = Field(..., min_length=3)
    target_id: str = Field(..., min_length=2)
    created_by: str = Field(..., min_length=2)
    operation_type: str = Field(default="legal.validation", min_length=3)
    actors: list[str] = Field(default_factory=list)
    contract: str | None = None
    amount: float | None = None
    has_documents: bool = True
    user_age_days: int = 365


class OverrideRequest(BaseModel):
    rule_code: str = Field(..., min_length=3)
    target_id: str = Field(..., min_length=2)
    reason: str = Field(..., min_length=8)
    requested_by: str = Field(..., min_length=2)
    approver_one: str = Field(..., min_length=2)
    approver_two: str = Field(..., min_length=2)


class JohnDecisionRequest(BaseModel):
    deal_id: str = Field(..., min_length=2)
    actors: list[str] = Field(default_factory=list)
    contract: str | None = None
    amount: float | None = None
    has_documents: bool = True
    user_age_days: int = 365


class LegalLearningCreateRequest(BaseModel):
    pattern_type: Literal["fraud", "loss", "contract_failure"]
    description: str = Field(..., min_length=10)
    source_id: str = Field(..., min_length=2)
    outcome: str = Field(..., min_length=3)


class KanbanStageUpdateRequest(BaseModel):
    actor_id: str = Field(..., min_length=2)
    stage: Literal["pending_legal", "under_review", "approved", "blocked"]
    reason: str | None = None
