from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.arbitration.repository import ArbitrationRepository
from app.arbitration.schemas import (
    ArbitrationCreate,
    ArbitrationEventCreate,
    ArbitrationEventResponse,
    ArbitrationListResponse,
    ArbitrationResponse,
    ArbitrationUpdate,
)
from app.db.session import get_session

router = APIRouter()


def _repo(session=Depends(get_session)) -> ArbitrationRepository:
    return ArbitrationRepository(session)


@router.post("/", response_model=ArbitrationResponse, status_code=201)
async def create_case(data: ArbitrationCreate, repo: ArbitrationRepository = Depends(_repo)):
    case = await repo.create(
        title=data.title,
        parties=data.parties,
        arbitrator_id=data.arbitrator_id,
        tenant_id=data.tenant_id,
    )
    return case


@router.get("/", response_model=ArbitrationListResponse)
async def list_cases(repo: ArbitrationRepository = Depends(_repo)):
    items = await repo.list_all()
    return ArbitrationListResponse(total=len(items), items=items)


@router.get("/{case_id}", response_model=ArbitrationResponse)
async def get_case(case_id: str, repo: ArbitrationRepository = Depends(_repo)):
    case = await repo.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Arbitration case not found")
    return case


@router.patch("/{case_id}", response_model=ArbitrationResponse)
async def update_case(case_id: str, data: ArbitrationUpdate, repo: ArbitrationRepository = Depends(_repo)):
    case = await repo.update(case_id, **data.model_dump(exclude_none=True))
    if not case:
        raise HTTPException(status_code=404, detail="Arbitration case not found")
    return case


@router.post("/{case_id}/events", response_model=ArbitrationEventResponse, status_code=201)
async def add_event(case_id: str, data: ArbitrationEventCreate, repo: ArbitrationRepository = Depends(_repo)):
    case = await repo.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Arbitration case not found")
    ev = await repo.add_event(case_id, data.event_type, data.description)
    return ev


@router.get("/{case_id}/events", response_model=list[ArbitrationEventResponse])
async def list_events(case_id: str, repo: ArbitrationRepository = Depends(_repo)):
    case = await repo.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Arbitration case not found")
    return case.events
