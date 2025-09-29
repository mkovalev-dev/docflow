from sqlalchemy.orm import aliased
from sqlalchemy import select, case
import uuid

from src.modules.documents.models import Document
from src.modules.workflow.models import WorkflowStep, WorkflowParticipant, Workflow


def document_status_expression(user_id: uuid.UUID):
    Step = aliased(WorkflowStep)
    Participant = aliased(WorkflowParticipant)

    # Статус, если пользователь — участник
    participant_status_subquery = (
        select(Step.status)
        .join(Participant, Participant.workflow_step_id == Step.id)
        .where(Participant.user_id == user_id)
        .where((Step.is_active == True) | (Step.finished_at.isnot(None)))
        .order_by(Step.started_at.desc().nullslast())
        .limit(1)
        .scalar_subquery()
    )

    # Статус, если пользователь — создатель
    creator_status_subquery = (
        select(Step.status)
        .where(Step.workflow_id == Workflow.id)
        .order_by(Step.is_active.desc(), Step.finished_at.desc().nullslast())
        .limit(1)
        .scalar_subquery()
    )

    return case(
        (
            Document.creator_id == user_id,
            creator_status_subquery,
        ),
        else_=participant_status_subquery,
    )
