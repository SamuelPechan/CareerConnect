"""Add reviewed message drafts.

Revision ID: 0006_message_drafts
Revises: 0005_networking
Create Date: 2026-10-18
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0006_message_drafts"
down_revision: str | None = "0005_networking"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)
    op.create_table(
        "message_drafts",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("contact_id", uuid_type, nullable=False),
        sa.Column("opportunity_id", uuid_type, nullable=True),
        sa.Column("message_type", sa.String(length=32), nullable=False),
        sa.Column("subject", sa.String(length=250), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="draft", nullable=False),
        sa.Column("generated_context", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["job_opportunities.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_message_drafts_user_status", "message_drafts", ["user_id", "status"])
    op.create_index("ix_message_drafts_user_contact", "message_drafts", ["user_id", "contact_id"])


def downgrade() -> None:
    op.drop_index("ix_message_drafts_user_contact", table_name="message_drafts")
    op.drop_index("ix_message_drafts_user_status", table_name="message_drafts")
    op.drop_table("message_drafts")
