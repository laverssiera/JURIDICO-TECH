from fastapi import APIRouter
from app.services.legal_engine import legal_engine

router = APIRouter()

@router.get("/alerts")
def get_norm_alerts() -> dict:
    return legal_engine.get_norm_alerts()


@router.get("/norms/alerts")
def get_norm_alerts_legacy() -> dict:
    return legal_engine.get_norm_alerts()

# Endpoints do Radar Legal
# GET /legal/radar/opportunities
