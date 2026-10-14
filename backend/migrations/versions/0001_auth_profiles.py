"""Create users, profiles, and resume references.

Revision ID: 0001_auth_profiles
Revises:
Create Date: 2026-10-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_auth_profiles"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)
    json_type = postgresql.JSONB()

    op.create_table(
        "users",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "user_profiles",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("school", sa.String(length=200), nullable=True),
        sa.Column("major", sa.String(length=200), nullable=True),
        sa.Column("graduation_year", sa.Integer(), nullable=True),
        sa.Column("skills", json_type, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("previous_employers", json_type, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("locations", json_type, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("career_interests", json_type, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("preferred_job_types", json_type, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("preferred_industries", json_type, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "resumes",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=True),
        sa.Column("metadata_json", json_type, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resumes_user_created", "resumes", ["user_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_resumes_user_created", table_name="resumes")
    op.drop_table("resumes")
    op.drop_table("user_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
