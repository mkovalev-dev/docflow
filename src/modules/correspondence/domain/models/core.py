from datetime import datetime

from sqlalchemy import String, Enum, Text, UUID, Integer, DateTime, ClauseList
from sqlalchemy.orm import Mapped, mapped_column

from src.common.db.mixins import BasicFieldsMixin
from src.core.db import Base
from src.modules.correspondence.domain.enums.document_type import DocumentTypeEnum
import uuid


class Document(Base, BasicFieldsMixin):
    """Документ"""

    __tablename__ = "correspondence_document"

    document_type: Mapped[str] = mapped_column(
        "document_type",
        Enum(
            DocumentTypeEnum,
            name="correspondence_document_document_type_enum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )

    system_number: Mapped[str] = mapped_column(String(25), nullable=True)
    content: Mapped[str] = mapped_column("content", Text(), default="", nullable=True)

    paper_count: Mapped[int] = mapped_column(
        "paper_count", Integer(), default=1, nullable=True
    )
    attachment_description: Mapped[str] = mapped_column(
        "attachment_description", String(100), nullable=True
    )
    deadline: Mapped[datetime] = mapped_column("deadline", DateTime(), nullable=True)

    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
