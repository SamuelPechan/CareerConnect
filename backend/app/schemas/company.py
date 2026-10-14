from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=250)
    domain: str | None = Field(default=None, max_length=250)
    notes: str | None = Field(default=None, max_length=10000)


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    domain: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
