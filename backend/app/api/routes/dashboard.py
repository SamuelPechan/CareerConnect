from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.db.models import (
    Application,
    ApplicationContact,
    Contact,
    ContactDiscoveryLink,
    ContactDiscoverySearch,
    ContactInteraction,
    FollowUpReminder,
    JobOpportunity,
)
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
    total_contacts = db.scalar(select(func.count(Contact.id)).where(Contact.user_id == user.id)) or 0
    upcoming_follow_ups = db.scalar(
        select(func.count(FollowUpReminder.id)).where(
            FollowUpReminder.user_id == user.id,
            FollowUpReminder.completed.is_(False),
            FollowUpReminder.due_at >= datetime.now(UTC),
        )
    ) or 0
    overdue_follow_ups = db.scalar(
        select(func.count(FollowUpReminder.id)).where(
            FollowUpReminder.user_id == user.id,
            FollowUpReminder.completed.is_(False),
            FollowUpReminder.due_at < datetime.now(UTC),
        )
    ) or 0
    total_interactions = db.scalar(
        select(func.count(ContactInteraction.id)).where(ContactInteraction.user_id == user.id)
    ) or 0
    total_discovery_links = db.scalar(
        select(func.count(ContactDiscoveryLink.id))
        .join(ContactDiscoverySearch, ContactDiscoveryLink.search_id == ContactDiscoverySearch.id)
        .where(ContactDiscoverySearch.user_id == user.id)
    ) or 0
    reviewed_discovery_links = db.scalar(
        select(func.count(ContactDiscoveryLink.id))
        .join(ContactDiscoverySearch, ContactDiscoveryLink.search_id == ContactDiscoverySearch.id)
        .where(ContactDiscoverySearch.user_id == user.id, ContactDiscoveryLink.reviewed.is_(True))
    ) or 0
    applications_with_contacts = db.scalar(
        select(func.count(func.distinct(ApplicationContact.application_id))).where(
            ApplicationContact.user_id == user.id
        )
    ) or 0
    applications_without_contacts = max(total_applications - applications_with_contacts, 0)
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
        total_contacts=total_contacts,
        upcoming_follow_ups=upcoming_follow_ups,
        overdue_follow_ups=overdue_follow_ups,
        total_interactions=total_interactions,
        total_discovery_links=total_discovery_links,
        reviewed_discovery_links=reviewed_discovery_links,
        applications_with_contacts=applications_with_contacts,
        applications_without_contacts=applications_without_contacts,
        interview_rate=round(by_status.get("interviewing", 0) / total_applications * 100, 1)
        if total_applications
        else None,
        offer_rate=round(by_status.get("offer", 0) / total_applications * 100, 1)
        if total_applications
        else None,
    )
