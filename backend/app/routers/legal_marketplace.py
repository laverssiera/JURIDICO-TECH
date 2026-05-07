from fastapi import APIRouter, HTTPException

from app.legal_core.legal_marketplace import LegalMarketplaceDomain

router = APIRouter()
_market = LegalMarketplaceDomain()


@router.post("/requests")
def create_request(payload: dict) -> dict:
    try:
        return _market.create_request(
            client_name=payload["client_name"],
            service_type=payload["service_type"],
            description=payload["description"],
            budget=payload.get("budget"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.patch("/requests/{request_id}")
def update_status(request_id: str, payload: dict) -> dict:
    try:
        return _market.update_status(request_id, payload["status"])
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requests")
def list_requests(service_type: str | None = None) -> dict:
    return {"requests": _market.list_requests(service_type)}
