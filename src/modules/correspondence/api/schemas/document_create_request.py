from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, TypeAdapter

from src.modules.correspondence.api.schemas.document_recipient import (
    NormalizedRecipients,
)
from src.modules.correspondence.api.schemas.document_sender import NormalizedSender
from src.modules.correspondence.domain.enums.confidential_type import (
    DocumentConfidentialTypeEnum,
)


class ExternalRegistrationSchema(BaseModel):
    """Модель для внешней регистрации документа"""

    external_number: str
    external_registration_at: datetime


class DocumentCreateRequest(BaseModel):
    """Схема для создания документов"""

    content: str

    paper_count: Optional[int] = Field(default=1)
    attachment_description: Optional[str] = Field(
        alias="attachment_count", default=None
    )

    deadline: Optional[datetime] = Field(default=None)

    confidentiality_level: List[DocumentConfidentialTypeEnum] = Field(default=[])

    external_registration: ExternalRegistrationSchema | None = None

    sender: Optional[NormalizedSender] = None
    recipients: NormalizedRecipients

    @field_validator("external_registration", mode="before")
    @classmethod
    def validate_external_registration(cls, v):
        adapter = TypeAdapter(ExternalRegistrationSchema)
        return adapter.validate_json(v)
