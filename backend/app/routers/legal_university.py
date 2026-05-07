from fastapi import APIRouter, HTTPException

from app.legal_core.legal_university import LegalUniversityDomain

router = APIRouter()
_uni = LegalUniversityDomain()


@router.get("/tracks")
def tracks() -> dict:
    return _uni.list_tracks()


@router.post("/enroll")
def enroll(payload: dict) -> dict:
    try:
        return _uni.enroll(
            person_id=payload["person_id"],
            profile=payload["profile"],
            track=payload.get("track"),
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.get("/enrollments")
def list_enrollments(profile: str | None = None) -> dict:
    return {"enrollments": _uni.list_enrollments(profile)}
