from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.db.models import Application, JobOpportunity
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(user: CurrentUser, db: DbSession) -> DashboardSummary:
    total_opportunities = db.scalar(
        select(func.count(JobOpportunity.id)).where(JobOpportunity.user_id == user.id)
    ) or 0
    total_applications = db.scalar(
        select(func.count(Application.id)).where(Application.user_id == user.id)
    ) or 0
    grouped_statuses = db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == user.id)
        .group_by(Application.status)
    ).all()
    by_status = {status: count for status, count in grouped_statuses}
    return DashboardSummary(
        total_saved_opportunities=total_opportunities,
        total_applications=total_applications,
        applications_by_status=by_status,
        total_interviews=by_status.get("interviewing", 0),
        total_offers=by_status.get("offer", 0),
    )
