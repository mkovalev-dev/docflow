from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator
import uuid

from pydantic_core.core_schema import ValidationInfo

from src.modules.documents.models import Document
from src.modules.documents.schemas.base import DocTypeLabel


class DocumentSelectOut(BaseModel):
    """Элемент списка селекта"""

    id: uuid.UUID
    document_type: DocTypeLabel
    content: str
    registration_number: Optional[str]
    registration_at: Optional[datetime]

    @model_validator(mode="before")
    @classmethod
    def from_orm_model(cls, v: Document, info: ValidationInfo):
        registration_number = None
        registration_at = None

        if registration := v.registration.registration_number:
            registration_number = registration.full_number
            registration_at = registration.created_at

        return {
            "id": v.id,
            "document_type": v.document_type,
            "content": v.content,
            "registration_number": registration_number,
            "registration_at": registration_at,
        }
