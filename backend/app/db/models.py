from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_email", "email"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    opportunities: Mapped[list["JobOpportunity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    companies: Mapped[list["Company"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    interactions: Mapped[list["ContactInteraction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["FollowUpReminder"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    message_drafts: Mapped[list["MessageDraft"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    discovery_searches: Mapped[list["ContactDiscoverySearch"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class PasswordResetToken(TimestampMixin, Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (Index("ix_password_reset_tokens_user_expires", "user_id", "expires_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="password_reset_tokens")


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    school: Mapped[str | None] = mapped_column(String(200))
    major: Mapped[str | None] = mapped_column(String(200))
    graduation_year: Mapped[int | None] = mapped_column()
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    previous_employers: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    locations: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    career_interests: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    preferred_job_types: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    preferred_industries: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="profile")


class Resume(TimestampMixin, Base):
    __tablename__ = "resumes"
    __table_args__ = (Index("ix_resumes_user_created", "user_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    user: Mapped[User] = relationship(back_populates="resumes")


class Company(TimestampMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (Index("ix_companies_user_name", "user_id", "name"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(250))
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="companies")
    opportunities: Mapped[list["JobOpportunity"]] = relationship(back_populates="company")
    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")
    discovery_searches: Mapped[list["ContactDiscoverySearch"]] = relationship(
        back_populates="company"
    )


class JobOpportunity(TimestampMixin, Base):
    __tablename__ = "job_opportunities"
    __table_args__ = (
        Index("ix_job_opportunities_user_status", "user_id", "status"),
        Index("ix_job_opportunities_user_company", "user_id", "company_name"),
        Index("ix_job_opportunities_user_date_saved", "user_id", "date_saved"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    company_name: Mapped[str] = mapped_column(String(250), nullable=False)
    location: Mapped[str | None] = mapped_column(String(250))
    job_url: Mapped[str | None] = mapped_column(Text)
    source_platform: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    date_saved: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="saved", nullable=False)

    user: Mapped[User] = relationship(back_populates="opportunities")
    company: Mapped[Company | None] = relationship(back_populates="opportunities")
    application: Mapped["Application | None"] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan", uselist=False
    )
    contacts: Mapped[list["Contact"]] = relationship(back_populates="opportunity")
    reminders: Mapped[list["FollowUpReminder"]] = relationship(back_populates="opportunity")
    message_drafts: Mapped[list["MessageDraft"]] = relationship(back_populates="opportunity")


class Contact(TimestampMixin, Base):
    __tablename__ = "contacts"
    __table_args__ = (
        Index("ix_contacts_user_company", "user_id", "company_id"),
        Index("ix_contacts_user_status", "user_id", "relationship_status"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL")
    )
    opportunity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("job_opportunities.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(250))
    company_name: Mapped[str] = mapped_column(String(250), nullable=False)
    school: Mapped[str | None] = mapped_column(String(200))
    relationship_reason: Mapped[str] = mapped_column(Text, nullable=False)
    source_platform: Mapped[str] = mapped_column(String(100), nullable=False)
    profile_url: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(String(320))
    notes: Mapped[str | None] = mapped_column(Text)
    relationship_status: Mapped[str] = mapped_column(String(32), default="new", nullable=False)

    user: Mapped[User] = relationship(back_populates="contacts")
    company: Mapped[Company | None] = relationship(back_populates="contacts")
    opportunity: Mapped[JobOpportunity | None] = relationship(back_populates="contacts")
    application_contacts: Mapped[list["ApplicationContact"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    interactions: Mapped[list["ContactInteraction"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["FollowUpReminder"]] = relationship(back_populates="contact")
    message_drafts: Mapped[list["MessageDraft"]] = relationship(back_populates="contact")


class Application(TimestampMixin, Base):
    __tablename__ = "applications"
    __table_args__ = (
        Index("ix_applications_user_status", "user_id", "status"),
        Index("ix_applications_user_application_date", "user_id", "application_date"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("job_opportunities.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), default="applied", nullable=False)
    application_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resume_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("resumes.id", ondelete="SET NULL")
    )
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="applications")
    opportunity: Mapped[JobOpportunity] = relationship(back_populates="application")
    resume: Mapped[Resume | None] = relationship()
    application_contacts: Mapped[list["ApplicationContact"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class ApplicationContact(TimestampMixin, Base):
    __tablename__ = "application_contacts"
    __table_args__ = (
        Index("ix_application_contacts_user", "user_id"),
        Index("ix_application_contacts_contact", "contact_id"),
        UniqueConstraint("application_id", "contact_id"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    application_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )

    application: Mapped[Application] = relationship(back_populates="application_contacts")
    contact: Mapped[Contact] = relationship(back_populates="application_contacts")


class ContactInteraction(TimestampMixin, Base):
    __tablename__ = "contact_interactions"
    __table_args__ = (Index("ix_interactions_user_contact_date", "user_id", "contact_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )
    interaction_type: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text)
    next_steps: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="interactions")
    contact: Mapped[Contact] = relationship(back_populates="interactions")
    reminders: Mapped[list["FollowUpReminder"]] = relationship(back_populates="interaction")


class FollowUpReminder(TimestampMixin, Base):
    __tablename__ = "follow_up_reminders"
    __table_args__ = (Index("ix_reminders_user_due", "user_id", "due_at", "completed"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE")
    )
    opportunity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("job_opportunities.id", ondelete="CASCADE")
    )
    interaction_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("contact_interactions.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="reminders")
    contact: Mapped[Contact | None] = relationship(back_populates="reminders")
    opportunity: Mapped[JobOpportunity | None] = relationship(back_populates="reminders")
    interaction: Mapped[ContactInteraction | None] = relationship(back_populates="reminders")


class MessageDraft(TimestampMixin, Base):
    __tablename__ = "message_drafts"
    __table_args__ = (
        Index("ix_message_drafts_user_status", "user_id", "status"),
        Index("ix_message_drafts_user_contact", "user_id", "contact_id"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("job_opportunities.id", ondelete="SET NULL")
    )
    message_type: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(250))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    generated_context: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    user: Mapped[User] = relationship(back_populates="message_drafts")
    contact: Mapped[Contact] = relationship(back_populates="message_drafts")
    opportunity: Mapped[JobOpportunity | None] = relationship(back_populates="message_drafts")


class ContactDiscoverySearch(TimestampMixin, Base):
    __tablename__ = "contact_discovery_searches"
    __table_args__ = (Index("ix_discovery_searches_user_created", "user_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("job_opportunities.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL")
    )
    criteria: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    relationship_categories: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped[User] = relationship(back_populates="discovery_searches")
    opportunity: Mapped[JobOpportunity] = relationship()
    company: Mapped[Company | None] = relationship(back_populates="discovery_searches")
    links: Mapped[list["ContactDiscoveryLink"]] = relationship(
        back_populates="search", cascade="all, delete-orphan"
    )


class ContactDiscoveryLink(TimestampMixin, Base):
    __tablename__ = "contact_discovery_links"
    __table_args__ = (Index("ix_discovery_links_search_platform", "search_id", "platform"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    search_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("contact_discovery_searches.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    search_url: Mapped[str] = mapped_column(Text, nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    relationship_reason: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    search: Mapped[ContactDiscoverySearch] = relationship(back_populates="links")
