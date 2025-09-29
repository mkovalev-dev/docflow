from datetime import datetime

from sqlalchemy import UUID, ForeignKey, String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.db.mixins import BasicFieldsMixin
from src.core.db import Base
from src.modules.correspondence.domain.models._mixins import RefDocumentMixin

import uuid


class RegistrationNumber(Base, BasicFieldsMixin):
    """Регистрационные номера"""

    __tablename__ = "registration_registration_number"

    prefix: Mapped[str] = mapped_column(String(20), nullable=True)
    number: Mapped[str] = mapped_column(String(20))
    postfix: Mapped[str] = mapped_column(String(20), nullable=True)

    registrator: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)

    document_registration = relationship(
        "DocumentRegistration", back_populates="registration_number", uselist=False
    )

    @property
    def full_name(self) -> str:
        return f"{self.prefix}-{self.number}/{self.postfix}"

    __table_args__ = (
        Index("idx_reg_number_prefix_number", "prefix", "number"),
        Index("idx_reg_number_number_postfix", "number", "postfix"),
        Index("idx_reg_number_full", "prefix", "number", "postfix"),
    )


class DocumentRegistration(Base, BasicFieldsMixin, RefDocumentMixin):
    """Регистрационные данные документа"""

    __tablename__ = "correspondence_document_registration"
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
