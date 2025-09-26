from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Enum,
    Integer,
    String,
    Text,
    Index,
    DateTime,
    ForeignKey,
    UUID,
    Boolean,
    literal_column,
)
from sqlalchemy.orm import mapped_column, Mapped, relationship, column_property

from src.common.db.mixins import BasicFieldsMixin
from src.core.db import Base
from src.modules.documents._mixins import RefDocumentMixin
from src.modules.documents.enums import (
    DocumentTypeEnum,
    DocumentPartyTypeEnum,
    DocumentConfidentialTypeEnum,
    DocumentAccessTypeEnum,
)
from src.modules.registration.models import RegistrationNumber

import uuid


class Document(Base, BasicFieldsMixin):
    """Документ"""

    __tablename__ = "documents_document"
    __table_args__ = (Index("ix_documents_document_type", "document_type"),)

    document_type: Mapped[str] = mapped_column(
        "document_type",
        Enum(
            DocumentTypeEnum,
            name="document_type_enum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    system_number: Mapped[str] = mapped_column(String(25), nullable=True)
    content: Mapped[str] = mapped_column("content", Text())
    paper_count: Mapped[int] = mapped_column("paper_count", Integer(), default=1)
    attachment_description: Mapped[str] = mapped_column(
        "attachment_description", String(100), nullable=True
    )

    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    # Additional fields
    deadline: Mapped[datetime] = mapped_column("deadline", DateTime(), nullable=True)

    document_status = column_property(literal_column("'UNKNOWN'"))


class DocumentRegistration(Base, BasicFieldsMixin, RefDocumentMixin):
    """Регистрационные данные документа"""

    __tablename__ = "document_document_registration"
    __document_backref__ = "registration"
    __document_backref_kwargs__ = {
        "cascade": "all, delete-orphan",
        "passive_deletes": True,
        "uselist": False,
        "lazy": "selectin",
    }

    registration_number_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("registration_registration_number.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        unique=True,
    )
    registration_number = relationship(
        RegistrationNumber, back_populates="document_registration", lazy="selectin"
    )
    external_registration_number: Mapped[str] = mapped_column(String(30), nullable=True)
    external_registration_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class DocumentAddress(Base, BasicFieldsMixin, RefDocumentMixin):
    """Отправители и получатели документа"""

    __tablename__ = "document_document_address"
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


class DocumentConfidential(Base, BasicFieldsMixin, RefDocumentMixin):
    """Уровни секретности документа"""

    __tablename__ = "document_document_confidential"
    __document_backref__ = "confidentials"

    confidential: Mapped[str] = mapped_column(
        Enum(
            DocumentConfidentialTypeEnum,
            name="document_confidential_enum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )


class DocumentAccess(Base, BasicFieldsMixin, RefDocumentMixin):
    """Наблюдатели за документом"""

    __tablename__ = "document_document_access"
    __document_backref__ = "accesses"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    access_type: Mapped[str] = mapped_column(
        Enum(
            DocumentAccessTypeEnum,
            name="document_access_type_enum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )


class DocumentFiles(Base, BasicFieldsMixin, RefDocumentMixin):
    """Файлы документов"""

    __tablename__ = "document_document_files"
    __document_backref__ = "files"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    extension: Mapped[Optional[str]] = mapped_column(String(20), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
