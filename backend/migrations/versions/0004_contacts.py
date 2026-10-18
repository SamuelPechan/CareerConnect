"""Add confirmed networking contacts.

Revision ID: 0004_contacts
Revises: 0003_companies_discovery
Create Date: 2026-10-18
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_contacts"
down_revision: str | None = "0003_companies_discovery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)
    op.create_table(
        "contacts",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("company_id", uuid_type, nullable=True),
        sa.Column("opportunity_id", uuid_type, nullable=True),
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.Column("job_title", sa.String(length=250), nullable=True),
        sa.Column("company_name", sa.String(length=250), nullable=False),
        sa.Column("school", sa.String(length=200), nullable=True),
        sa.Column("relationship_reason", sa.Text(), nullable=False),
        sa.Column("source_platform", sa.String(length=100), nullable=False),
        sa.Column("profile_url", sa.Text(), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("relationship_status", sa.String(length=32), server_default="new", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["job_opportunities.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contacts_user_company", "contacts", ["user_id", "company_id"])
    op.create_index("ix_contacts_user_status", "contacts", ["user_id", "relationship_status"])


def downgrade() -> None:
    op.drop_index("ix_contacts_user_status", table_name="contacts")
    op.drop_index("ix_contacts_user_company", table_name="contacts")
    op.drop_table("contacts")
