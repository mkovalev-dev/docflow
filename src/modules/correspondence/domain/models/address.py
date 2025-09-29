from sqlalchemy import Enum, UUID, Boolean, String
from sqlalchemy.orm import mapped_column, Mapped

from src.common.db.mixins import BasicFieldsMixin
from src.core.db import Base
from src.modules.correspondence.domain.enums.document_party_type import (
    DocumentPartyTypeEnum,
)
from src.modules.correspondence.domain.models._mixins import RefDocumentMixin
import uuid


class DocumentAddress(Base, BasicFieldsMixin, RefDocumentMixin):
    """Отправители и получатели документа"""

    __tablename__ = "correspondence_document_address"
    __document_backref__ = "address_parties"

    party_type: Mapped[str] = mapped_column(
        Enum(
            DocumentPartyTypeEnum,
            name="document_party_type_enum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    external_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    is_responsible: Mapped[bool] = mapped_column(Boolean, nullable=True)
    comment: Mapped[str] = mapped_column(String(255), nullable=True)
