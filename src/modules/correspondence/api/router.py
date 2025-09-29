from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.http.user_client import User
from src.core.auth import get_current_user
from src.core.db import get_session
from src.modules.correspondence.actions.system_registration_document import (
    SystemRegistrationDocumentAction,
)
from src.modules.correspondence.api.schemas.document_create_request import (
    DocumentCreateRequest,
)
from src.modules.correspondence.domain.enums.document_type import (
    DocumentTypesRequestEnum,
    DocumentTypeEnum,
)
from src.modules.correspondence.domain.models import Document
from src.modules.correspondence.services.document_create.address_service import (
    DocumentCreateAddress,
)
from src.modules.correspondence.services.document_create.confidentiality_level_service import (
    DocumentConfidentialityLevelService,
)

import uuid

from src.modules.correspondence.services.document_create.registration_service import (
    RegistrationService,
)

router = APIRouter(prefix="/correspondence", tags=["documents"])


@router.post(
    "/{document_request_type}",
)
async def create_new_document(
    data: Annotated[DocumentCreateRequest, Form()],
    document_request_type: DocumentTypesRequestEnum,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Контракт на создание нового документа"""

    document_type: DocumentTypeEnum = DocumentTypeEnum.__members__[
        document_request_type.name
    ]
    doc_id = uuid.uuid4()
    async with db.begin():
        document = Document(
            id=doc_id,
            document_type=document_type,
            creator_id=user.id,
            **data.model_dump(
                include={"content", "paper_count", "attachment_description", "deadline"}
            ),
        )
        document.system_number = SystemRegistrationDocumentAction().execute(
            document_type=document_type
        )
        confidential = DocumentConfidentialityLevelService(user=user).execute(
            confidentiality_level=data.confidentiality_level,
            document_id=doc_id,
        )
        document.registration = RegistrationService.execute(
            document_id=doc_id,
            external_number=getattr(
                data.external_registration, "external_number", None
            ),
            external_registration_at=getattr(
                data.external_registration, "external_registration_at", None
            ),
        )

        addresses = DocumentCreateAddress(document_id=doc_id, auth_user=user).execute(
            recipients=data.recipients, sender=data.sender
        )

        db.add_all(addresses)
        db.add_all(confidential)
        db.add(document)

    return {"system_number": document.system_number}
