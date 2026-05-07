"""Legal AI — JURIDICOTECH LICEU 6.0
RAG jurídico com pgvector + LangChain + fontes brasileiras e internacionais.
"""
from __future__ import annotations

from fastapi import FastAPI

from legal_ai.router import router

app = FastAPI(
    title="JURIDICOTECH Legal AI",
    version="6.0.0",
    description="RAG jurídico — busca semântica em legislação, jurisprudência e doutrina",
)

app.include_router(router, prefix="/legal-ai", tags=["rag"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "legal-ai"}
