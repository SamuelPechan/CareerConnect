from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DiscoveryLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    search_id: UUID
    platform: str
    search_url: str
    query: str
    relationship_reason: str
    reviewed: bool
    created_at: datetime
    updated_at: datetime


class DiscoverySearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    opportunity_id: UUID
    company_id: UUID | None
    criteria: dict[str, object]
    relationship_categories: list[str]
    instructions: str
    links: list[DiscoveryLinkResponse]
    created_at: datetime
    updated_at: datetime


class DiscoveryLinkReviewUpdate(BaseModel):
    reviewed: bool
