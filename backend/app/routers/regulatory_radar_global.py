from fastapi import APIRouter, HTTPException

from app.legal_core.regulatory_radar_global import RegulatoryRadarGlobalDomain
from app.integration.event_bus import event_bus

router = APIRouter()
_radar = RegulatoryRadarGlobalDomain()


@router.post("/signals")
def ingest_signal(payload: dict) -> dict:
    try:
        signal = _radar.ingest_signal(
            source=payload["source"],
            title=payload["title"],
            summary=payload["summary"],
            tags=payload.get("tags", []),
            severity=payload.get("severity", "medium"),
        )
        event_bus.publish("radar.signal.ingested", signal)
        return signal
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/signals")
def list_signals(source: str | None = None, severity: str | None = None) -> dict:
    return {"signals": _radar.list_signals(source, severity)}


@router.post("/signals/{signal_id}/disseminate")
def disseminate(signal_id: str) -> dict:
    try:
        result = _radar.disseminate(signal_id)
        event_bus.publish("radar.signal.disseminated", result)
        return result
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
