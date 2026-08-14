"""0003 — users, refresh_tokens, arbitration_cases, arbitration_events, compliance_checks, compliance_alerts

Revision ID: 20260507_0003
Revises: 20260507_0002
Create Date: 2026-05-07
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260507_0003"
down_revision = "20260507_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), server_default="cliente"),
        sa.Column("tenant_id", sa.String(36), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # arbitration_cases
    op.create_table(
        "arbitration_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_number", sa.String(80), nullable=False, unique=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), server_default="open"),
        sa.Column("parties_json", sa.Text(), server_default="[]"),
        sa.Column("arbitrator_id", sa.String(36), nullable=True),
        sa.Column("tenant_id", sa.String(36), nullable=True),
        sa.Column("award_amount", sa.Float(), nullable=True),
        sa.Column("award_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # arbitration_events
    op.create_table(
        "arbitration_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("arbitration_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # compliance_checks
    op.create_table(
        "compliance_checks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("scope", sa.String(100), server_default="global"),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("score", sa.Float(), server_default="0"),
        sa.Column("findings_json", sa.Text(), server_default="[]"),
        sa.Column("tenant_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_compliance_checks_entity_id", "compliance_checks", ["entity_id"])

    # compliance_alerts
    op.create_table(
        "compliance_alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("check_id", sa.String(36), sa.ForeignKey("compliance_checks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alert_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(20), server_default="medium"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("resolved", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("compliance_alerts")
    op.drop_table("compliance_checks")
    op.drop_table("arbitration_events")
    op.drop_table("arbitration_cases")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
