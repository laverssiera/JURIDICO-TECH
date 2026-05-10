from datetime import datetime

from pydantic import BaseModel


class ContractCreate(BaseModel):
    title: str
    contract_type: str
    content: str


class ContractResponse(BaseModel):
    contract_id: str
    title: str
    contract_type: str
    status: str
    risk_score: float
    created_at: datetime


class ContractCreateResult(BaseModel):
    status: str
    risk_score: float
    contract_id: str
    title: str
    event_status: str


class ContractListResponse(BaseModel):
    items: list[ContractResponse]
    total: int


class ClauseCreate(BaseModel):
    clause_type: str
    clause_text: str


class ClauseUpdate(BaseModel):
    clause_text: str


class ClauseResponse(BaseModel):
    clause_id: str
    contract_id: str
    clause_type: str
    clause_text: str
    litigation_score: float
    recommended: bool
    recommendation: str


class ClauseListResponse(BaseModel):
    items: list[ClauseResponse]
    total: int


class ContractSignRequest(BaseModel):
    signatory: str


class ContractBreachRequest(BaseModel):
    reason: str


class ContractTerminateRequest(BaseModel):
    reason: str


class ContractLifecycleResponse(BaseModel):
    contract_id: str
    status: str
    event_status: str
