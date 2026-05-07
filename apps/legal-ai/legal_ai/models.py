"""pgvector + SQLAlchemy model for legal document embeddings."""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)   # e.g. "CLT", "LGPD", "CC"
    doc_type: Mapped[str] = mapped_column(String(80), nullable=False)  # statute|jurisprudence|doctrine
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # embedding stored as text (JSON array) when pgvector unavailable; in prod use Vector(1536)
    embedding_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
