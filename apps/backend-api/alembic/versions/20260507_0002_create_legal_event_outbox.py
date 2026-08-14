"""create legal event outbox

Revision ID: 20260507_0002
Revises: 20260507_0001
Create Date: 2026-05-07 00:30:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260507_0002"
down_revision = "20260507_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "legal_event_outbox",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("legal_event_outbox")
