from pathlib import Path
from typing import List

from fastapi import HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.http.user_client import User
from src.modules.documents.enums import (
    DocumentTypesRequestEnum,
    DocumentPartyTypeEnum,
    DocumentConfidentialTypeEnum,
    DocumentAccessTypeEnum,
    DocumentTypeEnum,
)
from src.modules.documents.models import (
    Document,
    DocumentRegistration,
    DocumentAddress,
    DocumentConfidential,
    DocumentAccess,
    DocumentFiles,
)
from src.modules.documents.schemas.base import DocumentAddressCreateModel
from src.modules.documents.schemas.document_create import (
    DocumentCreateSchema,
    ExternalRegistrationSchema,
)
import uuid


from src.modules.workflow.actions.workflow_initialize_action import (
    WorkflowInitializeAction,
)


class DocumentCreateService:

    def __init__(
        self,
        db: AsyncSession,
        document_type: DocumentTypesRequestEnum,
        user: User | None,
        request: Request,
    ):
        self.db = db
        self.document_id = uuid.uuid4()
        self.request = request
        self.document_type = document_type.name
        if user:
            self.auth_user = user
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")

    async def _initial_registration(
        self, external_registration: ExternalRegistrationSchema | None
    ):
        registration = DocumentRegistration(
            document_id=self.document_id,
        )
        if external_registration:
            registration.external_registration_number = (
                external_registration.external_number
            )
            registration.external_registration_at = (
                external_registration.external_registration_at
            )
        self.db.add(registration)

    async def _create_recipients(self, recipients: List[DocumentAddressCreateModel]):
        data = []
        for recipient in recipients:
            data.append(
                DocumentAddress(
                    document_id=self.document_id,
                    party_type=recipient.party_type,
                    user_id=recipient.user_id,
                    external_user_id=recipient.external_user_id,
                    organization_id=recipient.organization_id,
                    is_responsible=recipient.is_responsible,
                    comment=recipient.comment,
                )
            )
        self.db.add_all(data)

    async def _create_sender(self, sender: DocumentAddressCreateModel):
        if sender is None:
            sender = DocumentAddressCreateModel.model_validate(
                {
                    "user_id": self.auth_user.id,
                    "party_type": DocumentPartyTypeEnum.SENDER,
                }
            )

        self.db.add(
            DocumentAddress(
                document_id=self.document_id,
                party_type=sender.party_type,
                user_id=sender.user_id,
                external_user_id=sender.external_user_id,
                organization_id=sender.organization_id,
                is_responsible=sender.is_responsible,
                comment=sender.comment,
            )
        )

    async def _add_confidentiality_level(
        self, confidentiality_level: List[DocumentConfidentialTypeEnum] = []
    ):
        data = []
        for level in confidentiality_level:
            data.append(
                DocumentConfidential(
                    document_id=self.document_id,
                    confidential=level,
                )
            )

        self.db.add_all(data)

    async def _add_access_to_document(self, access: List[uuid.UUID]):
        data = []
        for access in access:
            data.append(
                DocumentAccess(
                    document_id=self.document_id,
                    user_id=access,
                    access_type=DocumentAccessTypeEnum.READONLY,
                )
            )
        self.db.add_all(data)

    async def _add_files_to_document(
        self, files: List[UploadFile], is_main: bool = False
    ):
        items = []
        for file in files:
            items.append(
                DocumentFiles(
                    document_id=self.document_id,
                    file_id=uuid.uuid4(),
                    name=file.filename,
                    size=file.size,
                    extension=Path(file.filename).suffix.lstrip(".").lower(),
                    is_main=is_main,
                )
            )
        self.db.add_all(items)

    async def create_document(self, data: DocumentCreateSchema) -> Document:
        try:
            document = Document(
                id=self.document_id,
                document_type=self.document_type,
                content=data.content,
                paper_count=data.paper_count,
                attachment_description=data.attachment_description,
                deadline=data.deadline,
                creator_id=self.auth_user.id,
            )
            self.db.add(document)

            await self._initial_registration(
                external_registration=data.external_registration
            )
            await self._create_recipients(recipients=data.recipients)
            await self._create_sender(sender=data.sender)
            await self._add_confidentiality_level(
                confidentiality_level=data.confidentiality_level
            )
            await self._add_access_to_document(access=data.access)

            await self._add_files_to_document(files=[data.main_file], is_main=True)
            await self._add_files_to_document(files=data.file_list, is_main=False)

            workflow = WorkflowInitializeAction(
                document_id=self.document_id,
                document_type=DocumentTypeEnum.__members__[self.document_type],
                request=self.request,
                recipients=data.recipients,
                workflow_data=data.workflow,
            )
            self.db.add(await workflow.execute())

            await self.db.commit()
            return document
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Document creation failed: {str(e)}"
            )
