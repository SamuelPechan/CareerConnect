"""Add companies and contact discovery search plans.

Revision ID: 0003_companies_discovery
Revises: 0002_opportunities_applications
Create Date: 2026-10-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003_companies_discovery"
down_revision: str | None = "0002_opportunities_applications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)
    json_type = postgresql.JSONB()

    op.create_table(
        "companies",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.Column("domain", sa.String(length=250), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_companies_user_name", "companies", ["user_id", "name"])

    op.add_column("job_opportunities", sa.Column("company_id", uuid_type, nullable=True))
    op.create_foreign_key(
        "fk_job_opportunities_company_id_companies",
        "job_opportunities",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "contact_discovery_searches",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("opportunity_id", uuid_type, nullable=False),
        sa.Column("company_id", uuid_type, nullable=True),
        sa.Column("criteria", json_type, nullable=False),
        sa.Column("relationship_categories", json_type, server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["job_opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_discovery_searches_user_created", "contact_discovery_searches", ["user_id", "created_at"])

    op.create_table(
        "contact_discovery_links",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("search_id", uuid_type, nullable=False),
        sa.Column("platform", sa.String(length=100), nullable=False),
        sa.Column("search_url", sa.Text(), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("relationship_reason", sa.Text(), nullable=False),
        sa.Column("reviewed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["search_id"], ["contact_discovery_searches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_discovery_links_search_platform", "contact_discovery_links", ["search_id", "platform"])


def downgrade() -> None:
    op.drop_index("ix_discovery_links_search_platform", table_name="contact_discovery_links")
    op.drop_table("contact_discovery_links")
    op.drop_index("ix_discovery_searches_user_created", table_name="contact_discovery_searches")
    op.drop_table("contact_discovery_searches")
    op.drop_constraint("fk_job_opportunities_company_id_companies", "job_opportunities", type_="foreignkey")
    op.drop_column("job_opportunities", "company_id")
    op.drop_index("ix_companies_user_name", table_name="companies")
    op.drop_table("companies")
