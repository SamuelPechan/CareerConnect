from typing import Literal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field


class RecommendationRequest(BaseModel):
    opportunity_id: UUID
    consent: bool = Field(
        description="Confirms the user understands that limited professional context will be sent to the AI search provider"
    )


class Recommendation(BaseModel):
    name: str
    job_title: str
    company_name: str
    profile_url: AnyHttpUrl
    source_url: AnyHttpUrl
    source_title: str
    connection_reason: str
    evidence: str
    confidence: Literal["high", "medium", "low"]


class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]
    provider_note: str
