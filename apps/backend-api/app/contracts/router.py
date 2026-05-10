from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.repository import ContractRepository
from app.contracts.schemas import (
    ClauseCreate,
    ClauseListResponse,
    ClauseResponse,
    ClauseUpdate,
    ContractBreachRequest,
    ContractCreate,
    ContractCreateResult,
    ContractLifecycleResponse,
    ContractListResponse,
    ContractResponse,
    ContractSignRequest,
    ContractTerminateRequest,
)
from app.contracts.service import ClauseService, ContractService
from app.db.session import get_session

router = APIRouter()


@router.post("/")
async def create_contract(
    data: ContractCreate,
    session: AsyncSession = Depends(get_session),
    x_tenant_id: str | None = Header(default=None),
) -> ContractCreateResult:
    repo = ContractRepository(session)
    contract = ContractService.build_contract(
        title=data.title,
        contract_type=data.contract_type,
        content=data.content,
        tenant_id=x_tenant_id,
    )
    event_payload = {
        "contract_id": contract.id,
        "title": contract.title,
        "tenant_id": contract.tenant_id,
        "risk_score": contract.risk_score,
    }
    persisted = await repo.add_with_outbox(
        contract=contract,
        subject="legal.contract.created",
        payload=event_payload,
    )

    return ContractCreateResult(
        status="created",
        risk_score=persisted.risk_score,
        contract_id=persisted.id,
        title=persisted.title,
        event_status="outbox_pending",
    )


@router.get("/", response_model=ContractListResponse)
async def list_contracts(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> ContractListResponse:
    repo = ContractRepository(session)
    contracts = await repo.list_all(limit=limit, offset=offset)

    items = [
        ContractResponse(
            contract_id=c.id,
            title=c.title,
            contract_type=c.contract_type,
            status=c.status,
            risk_score=c.risk_score,
            created_at=c.created_at,
        )
        for c in contracts
    ]
    return ContractListResponse(items=items, total=len(items))


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    session: AsyncSession = Depends(get_session),
) -> ContractResponse:
    repo = ContractRepository(session)
    contract = await repo.get(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="contract_not_found")

    return ContractResponse(
        contract_id=contract.id,
        title=contract.title,
        contract_type=contract.contract_type,
        status=contract.status,
        risk_score=contract.risk_score,
        created_at=contract.created_at,
    )


@router.post("/{contract_id}/clauses", response_model=ClauseResponse)
async def create_clause(
    contract_id: str,
    data: ClauseCreate,
    session: AsyncSession = Depends(get_session),
) -> ClauseResponse:
    repo = ContractRepository(session)
    contract = await repo.get(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="contract_not_found")

    clause_service = ClauseService()
    clause, recommendation = await clause_service.build_clause(
        contract_id=contract_id,
        clause_type=data.clause_type,
        clause_text=data.clause_text,
    )
    persisted = await repo.add_clause(clause)

    return ClauseResponse(
        clause_id=persisted.id,
        contract_id=persisted.contract_id,
        clause_type=persisted.clause_type,
        clause_text=persisted.clause_text,
        litigation_score=persisted.litigation_score,
        recommended=persisted.recommended,
        recommendation=recommendation,
    )


@router.get("/{contract_id}/clauses", response_model=ClauseListResponse)
async def list_clauses(
    contract_id: str,
    session: AsyncSession = Depends(get_session),
) -> ClauseListResponse:
    repo = ContractRepository(session)
    contract = await repo.get(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="contract_not_found")

    clauses = await repo.list_clauses(contract_id)
    items = [
        ClauseResponse(
            clause_id=c.id,
            contract_id=c.contract_id,
            clause_type=c.clause_type,
            clause_text=c.clause_text,
            litigation_score=c.litigation_score,
            recommended=c.recommended,
            recommendation="Revisar clausula com base no risco processual.",
        )
        for c in clauses
    ]
    return ClauseListResponse(items=items, total=len(items))


@router.patch("/{contract_id}/clauses/{clause_id}", response_model=ClauseResponse)
async def update_clause(
    contract_id: str,
    clause_id: str,
    data: ClauseUpdate,
    session: AsyncSession = Depends(get_session),
) -> ClauseResponse:
    repo = ContractRepository(session)
    clause = await repo.get_clause(contract_id=contract_id, clause_id=clause_id)
    if clause is None:
        raise HTTPException(status_code=404, detail="clause_not_found")

    clause_service = ClauseService()
    updated_entity, recommendation = await clause_service.build_clause(
        contract_id=contract_id,
        clause_type=clause.clause_type,
        clause_text=data.clause_text,
    )

    clause.clause_text = updated_entity.clause_text
    clause.litigation_score = updated_entity.litigation_score
    clause.recommended = updated_entity.recommended
    await repo.update_clause(clause)

    return ClauseResponse(
        clause_id=clause.id,
        contract_id=clause.contract_id,
        clause_type=clause.clause_type,
        clause_text=clause.clause_text,
        litigation_score=clause.litigation_score,
        recommended=clause.recommended,
        recommendation=recommendation,
    )


@router.delete("/{contract_id}/clauses/{clause_id}")
async def delete_clause(
    contract_id: str,
    clause_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    repo = ContractRepository(session)
    clause = await repo.get_clause(contract_id=contract_id, clause_id=clause_id)
    if clause is None:
        raise HTTPException(status_code=404, detail="clause_not_found")

    await repo.delete_clause(clause)
    return {"status": "deleted", "clause_id": clause_id}


# ── Lifecycle ─────────────────────────────────────────────────────────────────

VALID_TRANSITIONS: dict[str, list[str]] = {
    "created": ["review", "signed"],
    "review": ["signed", "created"],
    "signed": ["active"],
    "active": ["terminated", "breached"],
    "terminated": [],
    "breached": [],
}


def _assert_transition(current: str, target: str) -> None:
    if target not in VALID_TRANSITIONS.get(current, []):
        raise HTTPException(
            status_code=422,
            detail=f"Transição inválida: {current} → {target}",
        )


@router.patch("/{contract_id}/sign", response_model=ContractLifecycleResponse, status_code=200)
async def sign_contract(
    contract_id: str,
    data: ContractSignRequest,
    session: AsyncSession = Depends(get_session),
) -> ContractLifecycleResponse:
    repo = ContractRepository(session)
    contract = await repo.get(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="contract_not_found")
    _assert_transition(contract.status, "signed")
    updated = await repo.transition(
        contract=contract,
        new_status="signed",
        subject="legal.contract.signed",
        payload={"contract_id": contract.id, "signatory": data.signatory, "title": contract.title},
    )
    return ContractLifecycleResponse(contract_id=updated.id, status=updated.status, event_status="outbox_pending")


@router.patch("/{contract_id}/activate", response_model=ContractLifecycleResponse, status_code=200)
async def activate_contract(
    contract_id: str,
    session: AsyncSession = Depends(get_session),
) -> ContractLifecycleResponse:
    repo = ContractRepository(session)
    contract = await repo.get(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="contract_not_found")
    _assert_transition(contract.status, "active")
    updated = await repo.transition(
        contract=contract,
        new_status="active",
        subject="legal.contract.created",
        payload={"contract_id": contract.id, "status": "active", "title": contract.title},
    )
    return ContractLifecycleResponse(contract_id=updated.id, status=updated.status, event_status="outbox_pending")


@router.patch("/{contract_id}/breach", response_model=ContractLifecycleResponse, status_code=200)
async def breach_contract(
    contract_id: str,
    data: ContractBreachRequest,
    session: AsyncSession = Depends(get_session),
) -> ContractLifecycleResponse:
    repo = ContractRepository(session)
    contract = await repo.get(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="contract_not_found")
    _assert_transition(contract.status, "breached")
    updated = await repo.transition(
        contract=contract,
        new_status="breached",
        subject="legal.contract.breach",
        payload={"contract_id": contract.id, "reason": data.reason, "title": contract.title},
    )
    return ContractLifecycleResponse(contract_id=updated.id, status=updated.status, event_status="outbox_pending")


@router.patch("/{contract_id}/terminate", response_model=ContractLifecycleResponse, status_code=200)
async def terminate_contract(
    contract_id: str,
    data: ContractTerminateRequest,
    session: AsyncSession = Depends(get_session),
) -> ContractLifecycleResponse:
    repo = ContractRepository(session)
    contract = await repo.get(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="contract_not_found")
    _assert_transition(contract.status, "terminated")
    updated = await repo.transition(
        contract=contract,
        new_status="terminated",
        subject="legal.contract.terminated",
        payload={"contract_id": contract.id, "reason": data.reason, "status": "terminated"},
    )
    return ContractLifecycleResponse(contract_id=updated.id, status=updated.status, event_status="outbox_pending")
