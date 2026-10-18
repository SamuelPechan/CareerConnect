from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApplicationContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    contact_id: UUID
    created_at: datetime
    updated_at: datetime


class InteractionCreate(BaseModel):
    interaction_type: str = Field(min_length=1, max_length=64)
    occurred_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=10000)
    outcome: str | None = Field(default=None, max_length=5000)
    next_steps: str | None = Field(default=None, max_length=5000)


class InteractionUpdate(InteractionCreate):
    interaction_type: str | None = Field(default=None, min_length=1, max_length=64)


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    contact_id: UUID
    interaction_type: str
    occurred_at: datetime
    notes: str | None
    outcome: str | None
    next_steps: str | None
    created_at: datetime
    updated_at: datetime


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    due_at: datetime
    notes: str | None = Field(default=None, max_length=10000)
    contact_id: UUID | None = None
    opportunity_id: UUID | None = None
    interaction_id: UUID | None = None


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    due_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=10000)
    completed: bool | None = None


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    contact_id: UUID | None
    opportunity_id: UUID | None
    interaction_id: UUID | None
    title: str
    due_at: datetime
    notes: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
