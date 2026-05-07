from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ArbitrationStart(BaseModel):
    case_title: str
    parties: list[str]


@router.post("/start")
async def start_arbitration(data: ArbitrationStart) -> dict[str, str]:
    return {
        "status": "started",
        "arbitration_id": str(uuid4()),
        "case_title": data.case_title,
    }
