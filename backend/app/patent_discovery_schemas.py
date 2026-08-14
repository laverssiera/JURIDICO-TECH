from __future__ import annotations

from pydantic import BaseModel, Field


class PatentRecord(BaseModel):
    id: str
    title: str
    category: str
    status: str
    novelty_score: float
    created_at: str
    prior_art_checked: bool | None = None


class RegisterPatentRequest(BaseModel):
    title: str | None = None
    category: str = Field(default="general", min_length=2)
    novelty_score: float = 0.0


class RegisterPatentResponse(BaseModel):
    status: str
    data: PatentRecord


class AnalyzeNoveltyRequest(BaseModel):
    novelty_score: float = 75.0
    prior_art_candidates: list[str] = Field(default_factory=list)


class AnalyzeNoveltyResponse(BaseModel):
    status: str
    is_novel: bool
    novelty_score: float
    prior_art_candidates: list[str]


class ValidatePriorArtRequest(BaseModel):
    patent_id: str | None = None


class ValidatePriorArtResponse(BaseModel):
    status: str
    data: PatentRecord


class CreateLicenseRequest(BaseModel):
    patent_id: str | None = None
    licensee: str | None = None
    royalty_rate: float = 0.0


class PatentLicenseData(BaseModel):
    patent_id: str
    licensee: str | None = None
    royalty_rate: float
    licensed_at: str


class CreateLicenseResponse(BaseModel):
    status: str
    data: PatentLicenseData