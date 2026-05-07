from datetime import UTC, datetime


def now_utc() -> datetime:
    return datetime.now(UTC)

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LegalContract(Base):
    __tablename__ = "legal_contracts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    contract_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    title: Mapped[str] = mapped_column(Text)
    contract_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    clauses: Mapped[list["LegalClause"]] = relationship(back_populates="contract", cascade="all, delete-orphan")


class LegalClause(Base):
    __tablename__ = "legal_clauses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    contract_id: Mapped[str] = mapped_column(String(36), ForeignKey("legal_contracts.id", ondelete="CASCADE"))
    clause_type: Mapped[str] = mapped_column(String(120))
    clause_text: Mapped[str] = mapped_column(Text)
    litigation_score: Mapped[float] = mapped_column(Float, default=0)
    recommended: Mapped[bool] = mapped_column(Boolean, default=False)

    contract: Mapped[LegalContract] = relationship(back_populates="clauses")


class LegalEventOutbox(Base):
    __tablename__ = "legal_event_outbox"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    subject: Mapped[str] = mapped_column(String(255))
    payload_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
