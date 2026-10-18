from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.db.models import Contact, ContactInteraction, JobOpportunity, MessageDraft
from app.schemas.message_draft import MessageDraftGenerate, MessageDraftResponse, MessageDraftUpdate

router = APIRouter(prefix="/message-drafts", tags=["message drafts"])


def owned_contact(contact_id: UUID, user_id: UUID, db: DbSession) -> Contact:
    contact = db.scalar(select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id))
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


def owned_opportunity(opportunity_id: UUID, user_id: UUID, db: DbSession) -> JobOpportunity:
    opportunity = db.scalar(
        select(JobOpportunity).where(JobOpportunity.id == opportunity_id, JobOpportunity.user_id == user_id)
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return opportunity


def generate_content(message_type: str, user: object, contact: Contact, opportunity: JobOpportunity | None) -> tuple[str | None, str]:
    profile = getattr(user, "profile", None)
    school = getattr(profile, "school", None) or "my university"
    major = getattr(profile, "major", None) or "my field"
    role = opportunity.title if opportunity else "the work you do"
    company = opportunity.company_name if opportunity else contact.company_name
    reason = contact.relationship_reason
    opening = f"I’m a {major} student at {school} exploring {role} at {company}."
    context = f"I noticed we may have a connection through {reason.lower()}."
    if message_type == "email":
        return (
            f"Learning about {company} and {role}",
            f"Hi {contact.name},\n\n{opening} {context}\n\nWould you be open to a brief conversation about your experience and any advice you would share with someone exploring this path? I’m happy to work around your schedule.\n\nThank you,\n{getattr(user, 'email', 'Your name')}\n",
        )
    if message_type == "informational_interview":
        return (
            None,
            f"Hi {contact.name},\n\n{opening} {context}\n\nI’d appreciate the chance to ask a few questions about your experience. Would you be open to a brief informational conversation?\n\nBest,\n{getattr(user, 'email', 'Your name')}\n",
        )
    if message_type == "thank_you":
        return (
            None,
            f"Hi {contact.name},\n\nThank you for taking the time to speak with me about {company} and {role}. Your perspective on {reason.lower()} was especially helpful. I appreciate your advice and will keep you posted as I continue exploring this opportunity.\n\nBest,\n{getattr(user, 'email', 'Your name')}\n",
        )
    return (
        None,
        f"Hi {contact.name},\n\n{opening} {context}\n\nI’d love to learn more about your experience at {company}. Would you be open to connecting?\n\nBest,\n{getattr(user, 'email', 'Your name')}\n",
    )


@router.post("/generate", response_model=MessageDraftResponse, status_code=status.HTTP_201_CREATED)
def generate_message_draft(
    payload: MessageDraftGenerate, user: CurrentUser, db: DbSession
) -> MessageDraft:
    contact = owned_contact(payload.contact_id, user.id, db)
    opportunity = None
    opportunity_id = payload.opportunity_id or contact.opportunity_id
    if opportunity_id:
        opportunity = owned_opportunity(opportunity_id, user.id, db)
    subject, body = generate_content(payload.message_type, user, contact, opportunity)
    interactions = list(
        db.scalars(
            select(ContactInteraction)
            .where(ContactInteraction.contact_id == contact.id, ContactInteraction.user_id == user.id)
            .order_by(ContactInteraction.occurred_at.desc())
            .limit(5)
        )
    )
    context = {
        "contact_name": contact.name,
        "relationship_reason": contact.relationship_reason,
        "company_name": opportunity.company_name if opportunity else contact.company_name,
        "job_title": opportunity.title if opportunity else None,
        "interaction_count": len(interactions),
        "review_required": True,
    }
    draft = MessageDraft(
        user_id=user.id,
        contact_id=contact.id,
        opportunity_id=opportunity.id if opportunity else None,
        message_type=payload.message_type,
        subject=subject,
        body=body,
        generated_context=context,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("", response_model=list[MessageDraftResponse])
def list_message_drafts(
    user: CurrentUser,
    db: DbSession,
    contact_id: UUID | None = None,
    draft_status: str | None = Query(default=None, alias="status", max_length=32),
) -> list[MessageDraft]:
    query = select(MessageDraft).where(MessageDraft.user_id == user.id)
    if contact_id:
        query = query.where(MessageDraft.contact_id == contact_id)
    if draft_status:
        query = query.where(MessageDraft.status == draft_status)
    return list(db.scalars(query.order_by(MessageDraft.updated_at.desc())))


@router.get("/{draft_id}", response_model=MessageDraftResponse)
def get_message_draft(draft_id: UUID, user: CurrentUser, db: DbSession) -> MessageDraft:
    draft = db.scalar(select(MessageDraft).where(MessageDraft.id == draft_id, MessageDraft.user_id == user.id))
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message draft not found")
    return draft


@router.patch("/{draft_id}", response_model=MessageDraftResponse)
def update_message_draft(
    draft_id: UUID, payload: MessageDraftUpdate, user: CurrentUser, db: DbSession
) -> MessageDraft:
    draft = db.scalar(select(MessageDraft).where(MessageDraft.id == draft_id, MessageDraft.user_id == user.id))
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message draft not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(draft, field, value)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message_draft(draft_id: UUID, user: CurrentUser, db: DbSession) -> None:
    draft = db.scalar(select(MessageDraft).where(MessageDraft.id == draft_id, MessageDraft.user_id == user.id))
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message draft not found")
    db.delete(draft)
    db.commit()
