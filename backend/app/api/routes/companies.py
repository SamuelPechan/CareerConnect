from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.db.models import Company, JobOpportunity
from app.schemas.company import CompanyCreate, CompanyResponse
from app.schemas.opportunity import OpportunityResponse

router = APIRouter(prefix="/companies", tags=["companies"])


def get_owned_company(company_id: UUID, user_id: UUID, db: DbSession) -> Company:
    company = db.scalar(select(Company).where(Company.id == company_id, Company.user_id == user_id))
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.get("", response_model=list[CompanyResponse])
def list_companies(user: CurrentUser, db: DbSession) -> list[Company]:
    return list(
        db.scalars(select(Company).where(Company.user_id == user.id).order_by(func.lower(Company.name)))
    )


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_or_reuse_company(payload: CompanyCreate, user: CurrentUser, db: DbSession) -> Company:
    company = db.scalar(
        select(Company).where(Company.user_id == user.id, func.lower(Company.name) == payload.name.lower())
    )
    if company is not None:
        return company
    company = Company(user_id=user.id, name=payload.name, domain=payload.domain, notes=payload.notes)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: UUID, user: CurrentUser, db: DbSession) -> Company:
    return get_owned_company(company_id, user.id, db)


@router.get("/{company_id}/opportunities", response_model=list[OpportunityResponse])
def list_company_opportunities(company_id: UUID, user: CurrentUser, db: DbSession) -> list[JobOpportunity]:
    get_owned_company(company_id, user.id, db)
    return list(
        db.scalars(
            select(JobOpportunity)
            .where(JobOpportunity.company_id == company_id, JobOpportunity.user_id == user.id)
            .order_by(JobOpportunity.date_saved.desc())
        )
    )
