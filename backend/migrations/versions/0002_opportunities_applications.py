"""Create job opportunities and applications.

Revision ID: 0002_opportunities_applications
Revises: 0001_auth_profiles
Create Date: 2026-10-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_opportunities_applications"
down_revision: str | None = "0001_auth_profiles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)
    op.create_table(
        "job_opportunities",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("company_name", sa.String(length=250), nullable=False),
        sa.Column("location", sa.String(length=250), nullable=True),
        sa.Column("job_url", sa.Text(), nullable=True),
        sa.Column("source_platform", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date_saved", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="saved"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_opportunities_user_status", "job_opportunities", ["user_id", "status"])
    op.create_index("ix_job_opportunities_user_company", "job_opportunities", ["user_id", "company_name"])
    op.create_index("ix_job_opportunities_user_date_saved", "job_opportunities", ["user_id", "date_saved"])

    op.create_table(
        "applications",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("opportunity_id", uuid_type, nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="applied"),
        sa.Column("application_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resume_id", uuid_type, nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["job_opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("opportunity_id"),
    )
    op.create_index("ix_applications_user_status", "applications", ["user_id", "status"])
    op.create_index("ix_applications_user_application_date", "applications", ["user_id", "application_date"])


def downgrade() -> None:
    op.drop_index("ix_applications_user_application_date", table_name="applications")
    op.drop_index("ix_applications_user_status", table_name="applications")
    op.drop_table("applications")
    op.drop_index("ix_job_opportunities_user_date_saved", table_name="job_opportunities")
    op.drop_index("ix_job_opportunities_user_company", table_name="job_opportunities")
    op.drop_index("ix_job_opportunities_user_status", table_name="job_opportunities")
    op.drop_table("job_opportunities")
