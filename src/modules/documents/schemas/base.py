from typing import Optional, Annotated

from pydantic import BaseModel, PlainSerializer

from src.modules.documents.enums import DocumentPartyTypeEnum, DocumentTypeEnum

import uuid


class DocumentAddressCreateModel(BaseModel):
    user_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None
    external_user_id: Optional[uuid.UUID] = None
    is_responsible: bool = False
    comment: Optional[str] = None
    party_type: DocumentPartyTypeEnum

DocTypeLabel = Annotated[
    DocumentTypeEnum,
    PlainSerializer(lambda v: v.get_russian_name(), return_type=str),
]
