from __future__ import annotations

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    source: str
    doc_type: str
    title: str
    content: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    citations: list[dict]
    model: str
    retrieval_count: int


class IngestRequest(BaseModel):
    source: str
    doc_type: str
    title: str
    content: str


class IngestResponse(BaseModel):
    id: str
    source: str
    status: str
