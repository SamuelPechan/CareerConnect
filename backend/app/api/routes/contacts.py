from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.db.models import Company, Contact, JobOpportunity
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


def get_owned_contact(contact_id: UUID, user_id: UUID, db: DbSession) -> Contact:
    contact = db.scalar(select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id))
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


def get_owned_company(company_id: UUID, user_id: UUID, db: DbSession) -> Company:
    company = db.scalar(select(Company).where(Company.id == company_id, Company.user_id == user_id))
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


def get_owned_opportunity(opportunity_id: UUID, user_id: UUID, db: DbSession) -> JobOpportunity:
    opportunity = db.scalar(
        select(JobOpportunity).where(JobOpportunity.id == opportunity_id, JobOpportunity.user_id == user_id)
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return opportunity


@router.get("", response_model=list[ContactResponse])
def list_contacts(
    user: CurrentUser,
    db: DbSession,
    company_id: UUID | None = None,
    opportunity_id: UUID | None = None,
    school: str | None = Query(default=None, max_length=200),
    relationship_status: str | None = Query(default=None, max_length=32),
    source_platform: str | None = Query(default=None, max_length=100),
) -> list[Contact]:
    query = select(Contact).where(Contact.user_id == user.id)
    if company_id:
        query = query.where(Contact.company_id == company_id)
    if opportunity_id:
        query = query.where(Contact.opportunity_id == opportunity_id)
    if school:
        query = query.where(Contact.school.ilike(f"%{school}%"))
    if relationship_status:
        query = query.where(Contact.relationship_status == relationship_status)
    if source_platform:
        query = query.where(Contact.source_platform.ilike(f"%{source_platform}%"))
    return list(db.scalars(query.order_by(Contact.created_at.desc())))


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, user: CurrentUser, db: DbSession) -> Contact:
    company = None
    if payload.company_id:
        company = get_owned_company(payload.company_id, user.id, db)
    else:
        company = db.scalar(
            select(Company).where(Company.user_id == user.id, Company.name.ilike(payload.company_name))
        )
        if company is None:
            company = Company(user_id=user.id, name=payload.company_name)
            db.add(company)
            db.flush()

    opportunity = None
    if payload.opportunity_id:
        opportunity = get_owned_opportunity(payload.opportunity_id, user.id, db)
        if opportunity.company_id and opportunity.company_id != company.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contact company does not match opportunity")

    contact = Contact(
        user_id=user.id,
        company_id=company.id,
        opportunity_id=opportunity.id if opportunity else None,
        name=payload.name,
        job_title=payload.job_title,
        company_name=payload.company_name,
        school=payload.school,
        relationship_reason=payload.relationship_reason,
        source_platform=payload.source_platform,
        profile_url=str(payload.profile_url) if payload.profile_url else None,
        email=str(payload.email) if payload.email else None,
        notes=payload.notes,
        relationship_status=payload.relationship_status,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: UUID, user: CurrentUser, db: DbSession) -> Contact:
    return get_owned_contact(contact_id, user.id, db)


@router.patch("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: UUID, payload: ContactUpdate, user: CurrentUser, db: DbSession) -> Contact:
    contact = get_owned_contact(contact_id, user.id, db)
    changes = payload.model_dump(exclude_unset=True)
    if "company_id" in changes and changes["company_id"] is not None:
        get_owned_company(changes["company_id"], user.id, db)
    if "opportunity_id" in changes and changes["opportunity_id"] is not None:
        get_owned_opportunity(changes["opportunity_id"], user.id, db)
    for field, value in changes.items():
        if field in {"profile_url", "email"} and value is not None:
            value = str(value)
        setattr(contact, field, value)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: UUID, user: CurrentUser, db: DbSession) -> None:
    contact = get_owned_contact(contact_id, user.id, db)
    db.delete(contact)
    db.commit()
