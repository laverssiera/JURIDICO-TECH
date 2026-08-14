"""create legal contracts and clauses

Revision ID: 20260507_0001
Revises: None
Create Date: 2026-05-07 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260507_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "legal_contracts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_number", sa.String(length=120), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("contract_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "legal_clauses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=36), sa.ForeignKey("legal_contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clause_type", sa.String(length=120), nullable=False),
        sa.Column("clause_text", sa.Text(), nullable=False),
        sa.Column("litigation_score", sa.Float(), nullable=False),
        sa.Column("recommended", sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("legal_clauses")
    op.drop_table("legal_contracts")
