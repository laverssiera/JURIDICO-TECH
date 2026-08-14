"""RAG pipeline — embed query → vector search → LLM answer with citations."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("legal-ai.rag")

# Known Brazilian & international legal sources
LEGAL_SOURCES = [
    {"source": "CLT", "doc_type": "statute", "title": "Consolidação das Leis do Trabalho"},
    {"source": "CC", "doc_type": "statute", "title": "Código Civil Brasileiro"},
    {"source": "CDC", "doc_type": "statute", "title": "Código de Defesa do Consumidor"},
    {"source": "LGPD", "doc_type": "statute", "title": "Lei Geral de Proteção de Dados"},
    {"source": "Lei12846", "doc_type": "statute", "title": "Lei Anticorrupção"},
    {"source": "CF88", "doc_type": "statute", "title": "Constituição Federal de 1988"},
    {"source": "CPC", "doc_type": "statute", "title": "Código de Processo Civil"},
    {"source": "STJ", "doc_type": "jurisprudence", "title": "Superior Tribunal de Justiça — jurisprudência"},
    {"source": "STF", "doc_type": "jurisprudence", "title": "Supremo Tribunal Federal — jurisprudência"},
    {"source": "GDPR", "doc_type": "statute", "title": "General Data Protection Regulation (EU)"},
    {"source": "ISO37001", "doc_type": "doctrine", "title": "ISO 37001 — Anti-bribery management systems"},
    {"source": "GRI", "doc_type": "doctrine", "title": "GRI Standards — sustainability reporting"},
]


@dataclass
class RetrievedChunk:
    source: str
    doc_type: str
    title: str
    content: str
    score: float


@dataclass
class RAGResponse:
    answer: str
    citations: list[dict]
    model: str
    retrieval_count: int


class LegalRAG:
    """
    Legal RAG pipeline.

    In production:
    - Embeddings via OpenAI text-embedding-3-small (1536 dim)
    - Vector store: pgvector on PostgreSQL
    - Retrieval: cosine similarity top-k
    - Generation: GPT-4o-mini with system prompt + retrieved context

    In dev/test (no API key):
    - Returns simulated answer with source citations
    """

    def __init__(self, settings) -> None:
        self.settings = settings
        self._llm: Any = None
        self._embeddings: Any = None

    def _init_llm(self) -> None:
        if self._llm or not self.settings.openai_api_key:
            return
        try:
            from langchain_openai import ChatOpenAI, OpenAIEmbeddings
            self._embeddings = OpenAIEmbeddings(
                model=self.settings.embedding_model,
                openai_api_key=self.settings.openai_api_key,
            )
            self._llm = ChatOpenAI(
                model=self.settings.chat_model,
                openai_api_key=self.settings.openai_api_key,
                temperature=0.1,
            )
        except ImportError:
            logger.warning("langchain-openai not installed — using simulated mode")

    async def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """Vector similarity search. Falls back to keyword simulation in dev."""
        k = top_k or self.settings.top_k
        self._init_llm()

        if self._embeddings:
            return await self._vector_search(query, k)
        return self._simulated_search(query, k)

    async def _vector_search(self, query: str, k: int) -> list[RetrievedChunk]:
        """Real pgvector search via LangChain PGVector."""
        try:
            from langchain_community.vectorstores.pgvector import PGVector
            store = PGVector(
                connection_string=self.settings.database_url,
                embedding_function=self._embeddings,
                collection_name=self.settings.vector_collection,
            )
            docs = store.similarity_search_with_score(query, k=k)
            return [
                RetrievedChunk(
                    source=d.metadata.get("source", "unknown"),
                    doc_type=d.metadata.get("doc_type", "statute"),
                    title=d.metadata.get("title", ""),
                    content=d.page_content,
                    score=float(score),
                )
                for d, score in docs
            ]
        except Exception as exc:
            logger.warning("pgvector search failed (%s), falling back to simulation", exc)
            return self._simulated_search(query, k)

    def _simulated_search(self, query: str, k: int) -> list[RetrievedChunk]:
        """Keyword-based simulation for dev/test without OpenAI key."""
        q_lower = query.lower()
        scored: list[tuple[float, dict]] = []

        keyword_map = {
            "trabalho": ["CLT", "NR"],
            "dados": ["LGPD", "GDPR"],
            "contrato": ["CC", "CPC"],
            "consumidor": ["CDC"],
            "corrupção": ["Lei12846", "ISO37001"],
            "constitucional": ["CF88"],
            "recurso": ["STJ", "STF", "CPC"],
            "esg": ["GRI", "ISO37001"],
        }

        for src in LEGAL_SOURCES:
            score = 0.3  # baseline
            for kw, srcs in keyword_map.items():
                if kw in q_lower and src["source"] in srcs:
                    score += 0.4
            scored.append((score, src))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            RetrievedChunk(
                source=s["source"],
                doc_type=s["doc_type"],
                title=s["title"],
                content=f"[Conteúdo simulado de {s['source']} para consulta: '{query}']",
                score=sc,
            )
            for sc, s in scored[:k]
        ]

    async def answer(self, query: str) -> RAGResponse:
        chunks = await self.search(query)

        if self._llm:
            answer_text = await self._llm_answer(query, chunks)
        else:
            answer_text = self._simulated_answer(query, chunks)

        return RAGResponse(
            answer=answer_text,
            citations=[
                {"source": c.source, "doc_type": c.doc_type, "title": c.title, "score": round(c.score, 4)}
                for c in chunks
            ],
            model=self.settings.chat_model if self._llm else "simulated",
            retrieval_count=len(chunks),
        )

    async def _llm_answer(self, query: str, chunks: list[RetrievedChunk]) -> str:
        from langchain.schema import HumanMessage, SystemMessage
        context = "\n\n".join(f"[{c.source}] {c.content}" for c in chunks)
        messages = [
            SystemMessage(content=(
                "Você é John Legal, assistente jurídico especializado em direito brasileiro e internacional. "
                "Responda com precisão, citando as fontes legais fornecidas. "
                "Não invente legislação. Se não souber, diga claramente."
            )),
            HumanMessage(content=f"Contexto legal:\n{context}\n\nPergunta: {query}"),
        ]
        result = await self._llm.ainvoke(messages)
        return result.content

    def _simulated_answer(self, query: str, chunks: list[RetrievedChunk]) -> str:
        citations = ", ".join(c.source for c in chunks[:3])
        return (
            f"[Modo simulado — configure LEGAL_AI_OPENAI_API_KEY para respostas reais]\n\n"
            f"Com base nas fontes: {citations}, a análise jurídica relacionada a '{query}' "
            f"envolve múltiplos aspectos normativos. "
            f"Recomendo consultar um advogado especializado para análise do caso concreto."
        )
