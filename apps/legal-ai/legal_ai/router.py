from __future__ import annotations

from fastapi import APIRouter

from legal_ai.config import settings
from legal_ai.rag import LegalRAG
from legal_ai.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)

router = APIRouter()
_rag = LegalRAG(settings)


@router.post("/search", response_model=SearchResponse)
async def search(data: SearchRequest):
    chunks = await _rag.search(data.query, top_k=data.top_k)
    return SearchResponse(
        query=data.query,
        results=[
            SearchResult(
                source=c.source,
                doc_type=c.doc_type,
                title=c.title,
                content=c.content,
                score=round(c.score, 4),
            )
            for c in chunks
        ],
    )


@router.post("/ask", response_model=AskResponse)
async def ask(data: AskRequest):
    result = await _rag.answer(data.question)
    return AskResponse(
        question=data.question,
        answer=result.answer,
        citations=result.citations,
        model=result.model,
        retrieval_count=result.retrieval_count,
    )


@router.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest(data: IngestRequest):
    """
    Ingest a document into the vector store.
    In production this embeds content and upserts into pgvector.
    """
    from uuid import uuid4
    doc_id = str(uuid4())

    if _rag._embeddings:
        try:
            from langchain.schema import Document
            from langchain_community.vectorstores.pgvector import PGVector
            doc = Document(
                page_content=data.content,
                metadata={"source": data.source, "doc_type": data.doc_type, "title": data.title, "id": doc_id},
            )
            store = PGVector(
                connection_string=settings.database_url,
                embedding_function=_rag._embeddings,
                collection_name=settings.vector_collection,
            )
            store.add_documents([doc])
            return IngestResponse(id=doc_id, source=data.source, status="indexed")
        except Exception:
            pass

    return IngestResponse(id=doc_id, source=data.source, status="queued_no_embeddings")
