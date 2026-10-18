from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

MessageType = Literal["linkedin", "email", "informational_interview", "thank_you"]
MessageStatus = Literal["draft", "approved", "copied", "sent", "archived"]


class MessageDraftGenerate(BaseModel):
    contact_id: UUID
    opportunity_id: UUID | None = None
    message_type: MessageType = "linkedin"


class MessageDraftUpdate(BaseModel):
    subject: str | None = Field(default=None, max_length=250)
    body: str | None = Field(default=None, min_length=1, max_length=20000)
    status: MessageStatus | None = None


class MessageDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    contact_id: UUID
    opportunity_id: UUID | None
    message_type: str
    subject: str | None
    body: str
    status: str
    generated_context: dict[str, object]
    created_at: datetime
    updated_at: datetime
