import uuid
from typing import Optional, List

from src.modules.correspondence.api.schemas.parts.address_create import (
    DocumentAddressCreateModel,
)
from src.modules.correspondence.domain.enums.document_party_type import (
    DocumentPartyTypeEnum,
)
from src.modules.correspondence.domain.models import DocumentAddress


class DocumentCreateAddress:

    def __init__(self, document_id: uuid.UUID, auth_user):
        self.document_id = document_id
        self.auth_user = auth_user

    def execute(
        self,
        recipients: Optional[List[DocumentAddressCreateModel]] = None,
        sender: Optional[DocumentAddressCreateModel] = None,
    ) -> List[DocumentAddress]:
        addresses: List[DocumentAddress] = []

        if recipients:
            addresses += self._build_recipients(recipients)

        addresses.append(self._build_sender(sender))

        return addresses

    def _build_recipients(
        self, recipients: List[DocumentAddressCreateModel]
    ) -> List[DocumentAddress]:
        return [self._build_address(recipient) for recipient in recipients]

    def _build_sender(
        self, sender: Optional[DocumentAddressCreateModel]
    ) -> DocumentAddress:
        if sender is None:
            sender = DocumentAddressCreateModel.model_validate(
                {
                    "user_id": self.auth_user.id,
                    "party_type": DocumentPartyTypeEnum.SENDER,
                }
            )
        return self._build_address(sender)

    def _build_address(self, data: DocumentAddressCreateModel) -> DocumentAddress:
        return DocumentAddress(
            document_id=self.document_id,
            party_type=data.party_type,
            user_id=data.user_id,
            external_user_id=data.external_user_id,
            organization_id=data.organization_id,
            is_responsible=data.is_responsible,
            comment=data.comment,
        )
