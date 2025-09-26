from datetime import datetime
from typing import List

from sqlalchemy import DateTime, func, Text, Boolean, Enum, UUID, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.db.mixins import BasicFieldsMixin
from src.core.db import Base

from src.modules.documents.models import RefDocumentMixin
from src.modules.workflow.enums import StatusEnum, StepTypeEnum
import uuid


class Workflow(Base, BasicFieldsMixin, RefDocumentMixin):
    """Ядро для маршрута"""

    __tablename__ = "workflow_workflow"
    __document_backref__ = "workflow"
    __document_backref_kwargs__ = {
        "cascade": "all, delete-orphan",
        "passive_deletes": True,
        "uselist": False,
        "lazy": "selectin",
    }

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    steps: Mapped[List["WorkflowStep"]] = relationship(
        "WorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",  # orphan удаляется при удалении из коллекции
        passive_deletes=True,
        lazy="selectin",
        order_by="WorkflowStep.order",
    )


class WorkflowStep(Base, BasicFieldsMixin):
    """Шаг для маршрута"""

    __tablename__ = "workflow_workflow_step"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_workflow.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow: Mapped["Workflow"] = relationship(
        "Workflow",
        back_populates="steps",
        lazy="selectin",
    )

    step_type: Mapped[str] = mapped_column(
        Enum(
            StepTypeEnum,
            name="step_type_enum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            StatusEnum,
            name="status_map_enum",
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=StatusEnum.WAITING,
    )
    order: Mapped[int] = mapped_column(Integer(), default=1)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)

    participants: Mapped[List["WorkflowParticipant"]] = relationship(
        "WorkflowParticipant",
        back_populates="step",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class WorkflowParticipant(Base, BasicFieldsMixin):
    """Участники шага маршрута"""

    __tablename__ = "workflow_workflow_participant_step"

    workflow_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_workflow_step.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step: Mapped["WorkflowStep"] = relationship(
        "WorkflowStep",
        back_populates="participants",
        lazy="selectin",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    status: Mapped[str] = mapped_column(
        Enum(
            StatusEnum,
            name="participant_status_enum",
            native_enum=True,
            validate_strings=True,
        ),
        default=StatusEnum.WAITING,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_responsible: Mapped[bool] = mapped_column(Boolean(), default=False)
