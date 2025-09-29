from typing import Optional

from pydantic import BaseModel, model_validator
import uuid

from src.modules.correspondence.domain.enums.document_party_type import (
    DocumentPartyTypeEnum,
)


class DocumentAddressCreateModel(BaseModel):
    user_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None
    external_user_id: Optional[uuid.UUID] = None
    is_responsible: bool = False
    comment: Optional[str] = None
    party_type: DocumentPartyTypeEnum

    @model_validator(mode="after")
    def check_exactly_one_identity(self):
        ids = [self.user_id, self.external_user_id, self.organization_id]
        if not any(ids):
            raise ValueError("Нужно указать хотя бы один идентификатор адресата.")
        return self
