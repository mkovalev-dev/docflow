from sqlalchemy import String, UUID, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from src.common.db.mixins import BasicFieldsMixin
from src.core.db import Base


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
        # Составные индексы для частых запросов
        Index("idx_reg_number_prefix_number", "prefix", "number"),
        Index("idx_reg_number_number_postfix", "number", "postfix"),
        Index("idx_reg_number_full", "prefix", "number", "postfix"),
    )
