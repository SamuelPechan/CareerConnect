from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=250)
    job_title: str | None = Field(default=None, max_length=250)
    company_name: str = Field(min_length=1, max_length=250)
    school: str | None = Field(default=None, max_length=200)
    relationship_reason: str = Field(min_length=1, max_length=5000)
    source_platform: str = Field(min_length=1, max_length=100)
    profile_url: AnyHttpUrl | None = None
    email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=10000)
    relationship_status: str = Field(default="new", min_length=1, max_length=32)
    company_id: UUID | None = None
    opportunity_id: UUID | None = None


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=250)
    job_title: str | None = Field(default=None, max_length=250)
    company_name: str | None = Field(default=None, min_length=1, max_length=250)
    school: str | None = Field(default=None, max_length=200)
    relationship_reason: str | None = Field(default=None, min_length=1, max_length=5000)
    source_platform: str | None = Field(default=None, min_length=1, max_length=100)
    profile_url: AnyHttpUrl | None = None
    email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=10000)
    relationship_status: str | None = Field(default=None, min_length=1, max_length=32)
    company_id: UUID | None = None
    opportunity_id: UUID | None = None


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    company_id: UUID | None
    opportunity_id: UUID | None
    name: str
    job_title: str | None
    company_name: str
    school: str | None
    relationship_reason: str
    source_platform: str
    profile_url: str | None
    email: str | None
    notes: str | None
    relationship_status: str
    created_at: datetime
    updated_at: datetime
