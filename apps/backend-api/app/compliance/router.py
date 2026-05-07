from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ComplianceCheckRequest(BaseModel):
    entity_id: str
    scope: str = "global"


@router.post("/check")
async def check_compliance(data: ComplianceCheckRequest) -> dict[str, str]:
    return {
        "status": "ok",
        "check_id": str(uuid4()),
        "entity_id": data.entity_id,
    }
