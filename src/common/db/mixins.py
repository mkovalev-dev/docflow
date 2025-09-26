from datetime import datetime

from sqlalchemy import UUID, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
import uuid


class IdMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        "id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.now,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        "deleted_at", DateTime(timezone=True), nullable=True
    )


class BasicFieldsMixin(IdMixin, CreatedAtMixin):
    pass
