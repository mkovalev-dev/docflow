from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from src.adapters.http.user_client import User
from src.modules.documents.enums import DocumentTypeEnum
from src.modules.documents.schemas.document_create import DocumentCreateSchema
from src.modules.documents.services.document_access_service import DocumentAccessService
from src.modules.documents.services.document_confidentiality_level_service import (
    DocumentConfidentialityLevelService,
)
from src.modules.documents.services.document_create_address import DocumentCreateAddress
from src.modules.documents.services.document_create_service import (
    DocumentCreateService,
    DocumentCreateData,
)
import uuid

from src.modules.registration.services.registration_service import RegistrationService


class DocumentOrchestrationService:
    """Оркестрация создания нового документа"""

    def __init__(
        self,
        document_type: DocumentTypeEnum,
        db: AsyncSession,
        request: Request,
        user: User,
    ):
        self.document_type = document_type
        self.db = db
        self.request = request
        self.user = user

    async def execute(self, data: DocumentCreateSchema):
        document_id = uuid.uuid4()
        document = DocumentCreateService().execute(
            id=document_id,
            document_type=self.document_type,
            user=self.user,
            data=DocumentCreateData.model(data),
        )
        registration = RegistrationService.initialize_registration_row(
            document_id=document_id,
            external_number=getattr(data.external_registration, "external_number"),
            external_registration_at=getattr(
                data.external_registration, "external_registration_at"
            ),
        )
        #
        address_service = DocumentCreateAddress(
            document_id=document_id, auth_user=self.user
        )
        addresses = await address_service.execute(
            recipients=data.recipients, sender=data.sender
        )
        #
        confidential = DocumentConfidentialityLevelService(
            user=self.user, document_id=document_id
        ).execute(confidentiality_level=data.confidentiality_level)

        #
        document_access_client = DocumentAccessService(
            user=self.user, document_id=document_id, request=self.request
        )
        document_access = await document_access_client.execute(
            user_ids=data.access, confidentiality_levels=data.confidentiality_level
        )
