from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
    school: str | None = Field(default=None, max_length=200)
    major: str | None = Field(default=None, max_length=200)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    skills: list[str] = Field(default_factory=list, max_length=50)
    previous_employers: list[str] = Field(default_factory=list, max_length=50)
    locations: list[str] = Field(default_factory=list, max_length=25)
    career_interests: list[str] = Field(default_factory=list, max_length=25)
    preferred_job_types: list[str] = Field(default_factory=list, max_length=15)
    preferred_industries: list[str] = Field(default_factory=list, max_length=25)


class ProfileUpdate(ProfileBase):
    onboarding_completed: bool | None = None


class ProfileResponse(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime


class ResumeCreate(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    file_url: AnyHttpUrl | None = None
    metadata: dict[str, str] = Field(default_factory=dict, max_length=20)


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    file_name: str
    file_url: str | None
    metadata_json: dict[str, str]
    created_at: datetime
    updated_at: datetime
