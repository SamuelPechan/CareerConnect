from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DbSession
from app.db.models import Application, JobOpportunity, Resume
from app.schemas.opportunity import (
    ApplicationResponse,
    ApplicationStatus,
    ApplicationUpdate,
    OpportunityCreate,
    OpportunityResponse,
    OpportunityStatus,
    OpportunityUpdate,
    SortField,
    SortOrder,
)

router = APIRouter(tags=["opportunities and applications"])


def get_owned_opportunity(opportunity_id: UUID, user_id: UUID, db: DbSession) -> JobOpportunity:
    opportunity = db.scalar(
        select(JobOpportunity)
        .options(joinedload(JobOpportunity.application))
        .where(JobOpportunity.id == opportunity_id, JobOpportunity.user_id == user_id)
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return opportunity


def get_owned_application(application_id: UUID, user_id: UUID, db: DbSession) -> Application:
    application = db.scalar(
        select(Application)
        .options(joinedload(Application.opportunity))
        .where(Application.id == application_id, Application.user_id == user_id)
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.get("/opportunities", response_model=list[OpportunityResponse])
def list_opportunities(
    user: CurrentUser,
    db: DbSession,
    status_filter: OpportunityStatus | None = Query(default=None, alias="status"),
    source_platform: str | None = Query(default=None, max_length=100),
    company: str | None = Query(default=None, max_length=250),
    sort_by: SortField = "date_saved",
    sort_order: SortOrder = "desc",
) -> list[JobOpportunity]:
    sort_column = getattr(JobOpportunity, sort_by)
    ordering = desc(sort_column) if sort_order == "desc" else asc(sort_column)
    query = select(JobOpportunity).options(joinedload(JobOpportunity.application)).where(
        JobOpportunity.user_id == user.id
    )
    if status_filter:
        query = query.where(JobOpportunity.status == status_filter)
    if source_platform:
        query = query.where(JobOpportunity.source_platform.ilike(f"%{source_platform}%"))
    if company:
        query = query.where(JobOpportunity.company_name.ilike(f"%{company}%"))
    return list(db.scalars(query.order_by(ordering)))


@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(payload: OpportunityCreate, user: CurrentUser, db: DbSession) -> JobOpportunity:
    opportunity = JobOpportunity(
        user_id=user.id,
        title=payload.title,
        company_name=payload.company_name,
        location=payload.location,
        job_url=str(payload.job_url) if payload.job_url else None,
        source_platform=payload.source_platform,
        description=payload.description,
        date_saved=payload.date_saved or datetime.now(UTC),
        notes=payload.notes,
        status=payload.status,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(opportunity_id: UUID, user: CurrentUser, db: DbSession) -> JobOpportunity:
    return get_owned_opportunity(opportunity_id, user.id, db)


@router.patch("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: UUID, payload: OpportunityUpdate, user: CurrentUser, db: DbSession
) -> JobOpportunity:
    opportunity = get_owned_opportunity(opportunity_id, user.id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "job_url" and value:
            value = str(value)
        setattr(opportunity, field, value)
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(opportunity_id: UUID, user: CurrentUser, db: DbSession) -> None:
    opportunity = get_owned_opportunity(opportunity_id, user.id, db)
    db.delete(opportunity)
    db.commit()


@router.post("/opportunities/{opportunity_id}/apply", response_model=ApplicationResponse)
def convert_to_application(opportunity_id: UUID, user: CurrentUser, db: DbSession) -> Application:
    opportunity = get_owned_opportunity(opportunity_id, user.id, db)
    if opportunity.application is not None:
        return opportunity.application
    application = Application(
        user_id=user.id,
        opportunity_id=opportunity.id,
        status="applied",
        application_date=datetime.now(UTC),
    )
    opportunity.status = "applied"
    db.add(application)
    db.add(opportunity)
    db.commit()
    db.refresh(application)
    return get_owned_application(application.id, user.id, db)


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    user: CurrentUser,
    db: DbSession,
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    source_platform: str | None = Query(default=None, max_length=100),
    company: str | None = Query(default=None, max_length=250),
    sort_by: Literal["application_date", "updated_at", "company_name"] = "application_date",
    sort_order: SortOrder = "desc",
) -> list[Application]:
    sort_column = {
        "application_date": Application.application_date,
        "updated_at": Application.updated_at,
        "company_name": JobOpportunity.company_name,
    }[sort_by]
    ordering = desc(sort_column) if sort_order == "desc" else asc(sort_column)
    query = (
        select(Application)
        .join(Application.opportunity)
        .options(joinedload(Application.opportunity))
        .where(Application.user_id == user.id)
    )
    if status_filter:
        query = query.where(Application.status == status_filter)
    if source_platform:
        query = query.where(JobOpportunity.source_platform.ilike(f"%{source_platform}%"))
    if company:
        query = query.where(JobOpportunity.company_name.ilike(f"%{company}%"))
    return list(db.scalars(query.order_by(ordering)))


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: UUID, user: CurrentUser, db: DbSession) -> Application:
    return get_owned_application(application_id, user.id, db)


@router.patch("/applications/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID, payload: ApplicationUpdate, user: CurrentUser, db: DbSession
) -> Application:
    application = get_owned_application(application_id, user.id, db)
    if payload.resume_id is not None:
        resume = db.scalar(select(Resume).where(Resume.id == payload.resume_id, Resume.user_id == user.id))
        if resume is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    application.opportunity.status = "applied"
    db.add(application)
    db.commit()
    db.refresh(application)
    return get_owned_application(application.id, user.id, db)


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: UUID, user: CurrentUser, db: DbSession) -> None:
    application = get_owned_application(application_id, user.id, db)
    application.opportunity.status = "planning_to_apply"
    db.delete(application)
    db.commit()
