"""Add application contact links, interactions, and reminders.

Revision ID: 0005_networking
Revises: 0004_contacts
Create Date: 2026-10-18
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_networking"
down_revision: str | None = "0004_contacts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)

    op.create_table(
        "application_contacts",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("application_id", uuid_type, nullable=False),
        sa.Column("contact_id", uuid_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", "contact_id"),
    )
    op.create_index("ix_application_contacts_user", "application_contacts", ["user_id"])
    op.create_index("ix_application_contacts_contact", "application_contacts", ["contact_id"])

    op.create_table(
        "contact_interactions",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("contact_id", uuid_type, nullable=False),
        sa.Column("interaction_type", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("next_steps", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_interactions_user_contact_date",
        "contact_interactions",
        ["user_id", "contact_id", "occurred_at"],
    )

    op.create_table(
        "follow_up_reminders",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("contact_id", uuid_type, nullable=True),
        sa.Column("opportunity_id", uuid_type, nullable=True),
        sa.Column("interaction_id", uuid_type, nullable=True),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["job_opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interaction_id"], ["contact_interactions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminders_user_due", "follow_up_reminders", ["user_id", "due_at", "completed"])


def downgrade() -> None:
    op.drop_index("ix_reminders_user_due", table_name="follow_up_reminders")
    op.drop_table("follow_up_reminders")
    op.drop_index("ix_interactions_user_contact_date", table_name="contact_interactions")
    op.drop_table("contact_interactions")
    op.drop_index("ix_application_contacts_contact", table_name="application_contacts")
    op.drop_index("ix_application_contacts_user", table_name="application_contacts")
    op.drop_table("application_contacts")
