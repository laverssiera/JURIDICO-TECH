from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.replay.engine import ReplayEngine
from app.replay.schemas import ReplayRequest, ReplayResult, ReplayStatusResponse

router = APIRouter()


@router.get("/status", response_model=ReplayStatusResponse)
async def replay_status(session: AsyncSession = Depends(get_session)) -> ReplayStatusResponse:
    engine = ReplayEngine(session)
    return await engine.status()


@router.post("/run", response_model=ReplayResult, status_code=201)
async def run_replay(
    data: ReplayRequest,
    session: AsyncSession = Depends(get_session),
) -> ReplayResult:
    engine = ReplayEngine(session)
    return await engine.replay(
        subject_filter=data.subject_filter,
        from_dt=data.from_dt,
        to_dt=data.to_dt,
        limit=min(data.limit, 500),
    )
