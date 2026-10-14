from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.db.models import Resume, UserProfile
from app.schemas.profile import ProfileResponse, ProfileUpdate, ResumeCreate, ResumeResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(user: CurrentUser) -> UserProfile:
    return user.profile


@router.patch("", response_model=ProfileResponse)
def update_profile(payload: ProfileUpdate, user: CurrentUser, db: DbSession) -> UserProfile:
    profile = user.profile
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/resumes", response_model=list[ResumeResponse])
def list_resumes(user: CurrentUser, db: DbSession) -> list[Resume]:
    return list(
        db.scalars(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))
    )


@router.post("/resumes", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def create_resume(payload: ResumeCreate, user: CurrentUser, db: DbSession) -> Resume:
    resume = Resume(
        user_id=user.id,
        file_name=payload.file_name,
        file_url=str(payload.file_url) if payload.file_url else None,
        metadata_json=payload.metadata,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume
