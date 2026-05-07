from datetime import UTC, datetime


def now_utc() -> datetime:
    return datetime.now(UTC)

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ── Contracts ─────────────────────────────────────────────────────────────────

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


# ── Outbox ─────────────────────────────────────────────────────────────────────

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


# ── Auth ──────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="cliente")
    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    user: Mapped[User] = relationship(back_populates="refresh_tokens")


# ── Arbitration ───────────────────────────────────────────────────────────────

class ArbitrationCase(Base):
    __tablename__ = "arbitration_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open")  # open|hearing|award|closed
    parties_json: Mapped[str] = mapped_column(Text, default="[]")    # JSON list of party names
    arbitrator_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    award_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    award_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    events: Mapped[list["ArbitrationEvent"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", order_by="ArbitrationEvent.created_at"
    )


class ArbitrationEvent(Base):
    __tablename__ = "arbitration_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("arbitration_cases.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(80))   # filed|hearing_scheduled|evidence_submitted|award_issued
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    case: Mapped[ArbitrationCase] = relationship(back_populates="events")


# ── Compliance ────────────────────────────────────────────────────────────────

class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(100), default="global")
    status: Mapped[str] = mapped_column(String(50), default="pending")   # pending|passed|failed|review
    score: Mapped[float] = mapped_column(Float, default=0.0)
    findings_json: Mapped[str] = mapped_column(Text, default="[]")
    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    alerts: Mapped[list["ComplianceAlert"]] = relationship(
        back_populates="check", cascade="all, delete-orphan"
    )


class ComplianceAlert(Base):
    __tablename__ = "compliance_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    check_id: Mapped[str] = mapped_column(String(36), ForeignKey("compliance_checks.id", ondelete="CASCADE"))
    alert_type: Mapped[str] = mapped_column(String(80))   # regulatory|esg|labor|tax|data_privacy
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # low|medium|high|critical
    message: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    check: Mapped[ComplianceCheck] = relationship(back_populates="alerts")
