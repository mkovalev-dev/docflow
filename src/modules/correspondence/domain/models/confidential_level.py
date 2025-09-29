from sqlalchemy import Enum, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from src.common.db.mixins import BasicFieldsMixin
from src.core.db import Base
from src.modules.correspondence.domain.enums.confidential_type import (
    DocumentConfidentialTypeEnum,
)
from src.modules.correspondence.domain.models._mixins import RefDocumentMixin


class DocumentConfidential(Base, BasicFieldsMixin, RefDocumentMixin):
    """Уровни секретности документа"""

    __tablename__ = "correspondence_document_confidential"
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
    __table_args__ = (
        UniqueConstraint("document_id", "confidential", name="uq_doc_confidential"),
    )
