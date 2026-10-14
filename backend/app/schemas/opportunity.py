from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

OpportunityStatus = Literal["saved", "planning_to_apply"]
ApplicationStatus = Literal["applied", "interviewing", "rejected", "offer", "withdrawn"]
SortField = Literal["title", "company_name", "date_saved", "updated_at"]
SortOrder = Literal["asc", "desc"]


class ApplicationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    application_date: datetime | None
    resume_id: UUID | None
    notes: str | None


class OpportunityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    company_name: str = Field(min_length=1, max_length=250)
    company_id: UUID | None = None
    location: str | None = Field(default=None, max_length=250)
    job_url: AnyHttpUrl | None = None
    source_platform: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=20000)
    date_saved: datetime | None = None
    notes: str | None = Field(default=None, max_length=10000)
    status: OpportunityStatus = "saved"


class OpportunityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    company_name: str | None = Field(default=None, min_length=1, max_length=250)
    company_id: UUID | None = None
    location: str | None = Field(default=None, max_length=250)
    job_url: AnyHttpUrl | None = None
    source_platform: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=20000)
    date_saved: datetime | None = None
    notes: str | None = Field(default=None, max_length=10000)
    status: OpportunityStatus | None = None


class OpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    company_id: UUID | None
    title: str
    company_name: str
    location: str | None
    job_url: str | None
    source_platform: str | None
    description: str | None
    date_saved: datetime
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    application: ApplicationSummary | None = None


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    application_date: datetime | None = None
    resume_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=10000)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    opportunity_id: UUID
    status: str
    application_date: datetime | None
    resume_id: UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    opportunity: OpportunityResponse
