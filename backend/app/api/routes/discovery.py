from urllib.parse import quote_plus
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DbSession
from app.db.models import Company, ContactDiscoveryLink, ContactDiscoverySearch, JobOpportunity
from app.schemas.discovery import (
    DiscoveryLinkResponse,
    DiscoveryLinkReviewUpdate,
    DiscoverySearchResponse,
)

router = APIRouter(prefix="/discovery", tags=["contact discovery"])


def get_owned_search(search_id: UUID, user_id: UUID, db: DbSession) -> ContactDiscoverySearch:
    search = db.scalar(
        select(ContactDiscoverySearch)
        .options(joinedload(ContactDiscoverySearch.links))
        .where(ContactDiscoverySearch.id == search_id, ContactDiscoverySearch.user_id == user_id)
    )
    if search is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery search not found")
    return search


def build_search_query(opportunity: JobOpportunity, profile: object) -> str:
    profile_school = getattr(profile, "school", None) or ""
    profile_major = getattr(profile, "major", None) or ""
    return " ".join(part for part in [opportunity.company_name, opportunity.title, profile_school, profile_major] if part)


@router.post(
    "/opportunities/{opportunity_id}/find-contacts",
    response_model=DiscoverySearchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discovery_search(
    opportunity_id: UUID, user: CurrentUser, db: DbSession
) -> ContactDiscoverySearch:
    opportunity = db.scalar(
        select(JobOpportunity).where(JobOpportunity.id == opportunity_id, JobOpportunity.user_id == user.id)
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    profile = user.profile
    skills = profile.skills if profile else []
    previous_employers = profile.previous_employers if profile else []
    career_interests = profile.career_interests if profile else []
    search_query = build_search_query(opportunity, profile)
    encoded_query = quote_plus(search_query)
    school = profile.school if profile else None
    company = opportunity.company_name
    categories = ["Current employee", "Recruiter or hiring-related role"]
    if school:
        categories.insert(0, "University alumni")
    if skills:
        categories.append("Shared skills")
    if previous_employers:
        categories.append("Shared previous employer")

    company_query = f"{company} employees {opportunity.title}"
    alumni_query = f"{school or 'university'} alumni {company}"
    organization_query = f"{opportunity.title} {company} professional organization"

    criteria = {
        "company_name": company,
        "job_title": opportunity.title,
        "location": opportunity.location,
        "school": school,
        "major": profile.major if profile else None,
        "skills": skills,
        "previous_employers": previous_employers,
        "career_interests": career_interests,
    }
    instructions = (
        "Review public professional information on the external platform. Look for people who work at the company, "
        "share a school, skill, or previous employer, or appear connected to recruiting for this role. "
        "Confirm the relationship reason before saving a contact. CareerConnect does not scrape profiles or send outreach automatically."
    )
    company_record = None
    if opportunity.company_id:
        company_record = db.scalar(
            select(Company).where(Company.id == opportunity.company_id, Company.user_id == user.id)
        )
    if company_record is None:
        company_record = db.scalar(
            select(Company).where(Company.user_id == user.id, Company.name.ilike(company))
        )
        if company_record is None:
            company_record = Company(user_id=user.id, name=company)
            db.add(company_record)
            db.flush()
        opportunity.company_id = company_record.id

    search = ContactDiscoverySearch(
        user_id=user.id,
        opportunity_id=opportunity.id,
        company_id=company_record.id,
        criteria=criteria,
        relationship_categories=categories,
        instructions=instructions,
    )
    links = [
        ("LinkedIn", f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}", "Search current employees, alumni, recruiters, and people with shared skills."),
        ("Handshake", f"https://app.joinhandshake.com/students/search?query={encoded_query}", "Search your permitted university and early-career network."),
        ("Company pages", f"https://www.google.com/search?q={quote_plus(company_query)}", "Look for public team pages and recruiting information."),
        ("Alumni directories", f"https://www.google.com/search?q={quote_plus(alumni_query)}", "Look for alumni pages or professional communities you are allowed to access."),
        ("Professional organizations", f"https://www.google.com/search?q={quote_plus(organization_query)}", "Look for relevant communities and professional groups."),
    ]
    search.links = [
        ContactDiscoveryLink(
            platform=platform,
            search_url=url,
            query=search_query,
            relationship_reason=reason,
        )
        for platform, url, reason in links
    ]
    db.add(search)
    db.add(opportunity)
    db.commit()
    db.refresh(search)
    return get_owned_search(search.id, user.id, db)


@router.get("/searches/{search_id}", response_model=DiscoverySearchResponse)
def get_discovery_search(search_id: UUID, user: CurrentUser, db: DbSession) -> ContactDiscoverySearch:
    return get_owned_search(search_id, user.id, db)


@router.patch("/links/{link_id}", response_model=DiscoveryLinkResponse)
def review_discovery_link(
    link_id: UUID, payload: DiscoveryLinkReviewUpdate, user: CurrentUser, db: DbSession
) -> ContactDiscoveryLink:
    link = db.scalar(
        select(ContactDiscoveryLink)
        .join(ContactDiscoveryLink.search)
        .where(ContactDiscoveryLink.id == link_id, ContactDiscoverySearch.user_id == user.id)
    )
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery link not found")
    link.reviewed = payload.reviewed
    db.add(link)
    db.commit()
    db.refresh(link)
    return link
