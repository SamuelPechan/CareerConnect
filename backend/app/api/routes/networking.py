from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.db.models import (
    Application,
    ApplicationContact,
    Contact,
    ContactInteraction,
    FollowUpReminder,
    JobOpportunity,
)
from app.schemas.networking import (
    ApplicationContactResponse,
    InteractionCreate,
    InteractionResponse,
    InteractionUpdate,
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
)

router = APIRouter(tags=["networking"])


def owned_contact(contact_id: UUID, user_id: UUID, db: DbSession) -> Contact:
    contact = db.scalar(select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id))
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


def owned_application(application_id: UUID, user_id: UUID, db: DbSession) -> Application:
    application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user_id))
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.post(
    "/contacts/{contact_id}/applications/{application_id}",
    response_model=ApplicationContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def connect_contact_to_application(
    contact_id: UUID, application_id: UUID, user: CurrentUser, db: DbSession
) -> ApplicationContact:
    owned_contact(contact_id, user.id, db)
    owned_application(application_id, user.id, db)
    existing = db.scalar(
        select(ApplicationContact).where(
            ApplicationContact.contact_id == contact_id,
            ApplicationContact.application_id == application_id,
            ApplicationContact.user_id == user.id,
        )
    )
    if existing is not None:
        return existing
    link = ApplicationContact(
        user_id=user.id, contact_id=contact_id, application_id=application_id
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/contacts/{contact_id}/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_contact_from_application(
    contact_id: UUID, application_id: UUID, user: CurrentUser, db: DbSession
) -> None:
    link = db.scalar(
        select(ApplicationContact).where(
            ApplicationContact.contact_id == contact_id,
            ApplicationContact.application_id == application_id,
            ApplicationContact.user_id == user.id,
        )
    )
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact connection not found")
    db.delete(link)
    db.commit()


@router.get("/contacts/{contact_id}/interactions", response_model=list[InteractionResponse])
def list_interactions(contact_id: UUID, user: CurrentUser, db: DbSession) -> list[ContactInteraction]:
    owned_contact(contact_id, user.id, db)
    return list(
        db.scalars(
            select(ContactInteraction)
            .where(ContactInteraction.contact_id == contact_id, ContactInteraction.user_id == user.id)
            .order_by(ContactInteraction.occurred_at.desc())
        )
    )


@router.post("/contacts/{contact_id}/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_interaction(
    contact_id: UUID, payload: InteractionCreate, user: CurrentUser, db: DbSession
) -> ContactInteraction:
    owned_contact(contact_id, user.id, db)
    interaction = ContactInteraction(
        user_id=user.id,
        contact_id=contact_id,
        interaction_type=payload.interaction_type,
        occurred_at=payload.occurred_at or datetime.now(UTC),
        notes=payload.notes,
        outcome=payload.outcome,
        next_steps=payload.next_steps,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.patch("/interactions/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: UUID, payload: InteractionUpdate, user: CurrentUser, db: DbSession
) -> ContactInteraction:
    interaction = db.scalar(
        select(ContactInteraction).where(ContactInteraction.id == interaction_id, ContactInteraction.user_id == user.id)
    )
    if interaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interaction, field, value)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.delete("/interactions/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(interaction_id: UUID, user: CurrentUser, db: DbSession) -> None:
    interaction = db.scalar(
        select(ContactInteraction).where(ContactInteraction.id == interaction_id, ContactInteraction.user_id == user.id)
    )
    if interaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    db.delete(interaction)
    db.commit()


@router.get("/reminders", response_model=list[ReminderResponse])
def list_reminders(
    user: CurrentUser,
    db: DbSession,
    completed: bool | None = None,
    overdue: bool = False,
    contact_id: UUID | None = None,
) -> list[FollowUpReminder]:
    query = select(FollowUpReminder).where(FollowUpReminder.user_id == user.id)
    if completed is not None:
        query = query.where(FollowUpReminder.completed == completed)
    if overdue:
        query = query.where(FollowUpReminder.completed.is_(False), FollowUpReminder.due_at < datetime.now(UTC))
    if contact_id:
        query = query.where(FollowUpReminder.contact_id == contact_id)
    return list(db.scalars(query.order_by(FollowUpReminder.due_at.asc())))


@router.post("/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(payload: ReminderCreate, user: CurrentUser, db: DbSession) -> FollowUpReminder:
    if payload.contact_id:
        owned_contact(payload.contact_id, user.id, db)
    if payload.opportunity_id:
        opportunity = db.scalar(
            select(JobOpportunity).where(JobOpportunity.id == payload.opportunity_id, JobOpportunity.user_id == user.id)
        )
        if opportunity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    if payload.interaction_id:
        interaction = db.scalar(
            select(ContactInteraction).where(
                ContactInteraction.id == payload.interaction_id, ContactInteraction.user_id == user.id
            )
        )
        if interaction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    if not any((payload.contact_id, payload.opportunity_id, payload.interaction_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reminder must be connected to a contact, opportunity, or interaction")
    reminder = FollowUpReminder(user_id=user.id, **payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.patch("/reminders/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: UUID, payload: ReminderUpdate, user: CurrentUser, db: DbSession
) -> FollowUpReminder:
    reminder = db.scalar(
        select(FollowUpReminder).where(FollowUpReminder.id == reminder_id, FollowUpReminder.user_id == user.id)
    )
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: UUID, user: CurrentUser, db: DbSession) -> None:
    reminder = db.scalar(
        select(FollowUpReminder).where(FollowUpReminder.id == reminder_id, FollowUpReminder.user_id == user.id)
    )
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
