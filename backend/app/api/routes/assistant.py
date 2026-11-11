from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import AnyHttpUrl, TypeAdapter, ValidationError
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.db.models import JobOpportunity
from app.schemas.recommendations import (
    Recommendation,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendations import find_recommendations

router = APIRouter(prefix="/assistant", tags=["career assistant"])
http_url = TypeAdapter(AnyHttpUrl)


def owned_opportunity(opportunity_id: UUID, user_id: UUID, db: DbSession) -> JobOpportunity:
    opportunity = db.scalar(
        select(JobOpportunity).where(JobOpportunity.id == opportunity_id, JobOpportunity.user_id == user_id)
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return opportunity


@router.post("/recommendations", response_model=RecommendationResponse)
def recommend_connections(
    payload: RecommendationRequest, user: CurrentUser, db: DbSession
) -> RecommendationResponse:
    if not payload.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirm the public-web research consent before requesting recommendations",
        )
    opportunity = owned_opportunity(payload.opportunity_id, user.id, db)
    try:
        raw_recommendations = find_recommendations(opportunity, user.profile, get_settings())
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    recommendations: list[Recommendation] = []
    for item in raw_recommendations:
        try:
            item["profile_url"] = str(http_url.validate_python(item.get("profile_url", "")))
            item["source_url"] = str(http_url.validate_python(item.get("source_url", "")))
            recommendations.append(Recommendation.model_validate(item))
        except (ValidationError, TypeError, ValueError):
            continue
    return RecommendationResponse(
        recommendations=recommendations,
        provider_note="These are public-web suggestions, not verified endorsements. Review the evidence before saving anyone.",
    )
