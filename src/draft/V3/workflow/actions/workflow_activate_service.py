import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workflow.enums import StatusEnum
from src.modules.workflow.models import Workflow, WorkflowStep


class WorkflowActivateService:
    """Активация маршрута"""

    def __init__(self, document_id: uuid.UUID, db: AsyncSession):
        self.document_id = document_id
        self.db = db

    async def execute(self) -> Workflow:
        query = select(Workflow).where(Workflow.document_id == self.document_id)
        result = await self.db.execute(query)
        workflow = result.scalars().first()
        if not workflow:
            raise ValueError("Не найден маршрут документа")

        # TODO:Нужно проверять еще что маршрут не запущен
        stmt = (
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == workflow.id)
            .order_by(WorkflowStep.order.asc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        step: WorkflowStep = result.scalars().first()
        if step:
            step.is_active = True
            step.status = StatusEnum.SENDED
            step.started_at = datetime.now()
            for participant in step.participants:
                participant.status = StatusEnum.SENDED
                participant.started_at = datetime.now()
            self.db.add(step)
        return workflow
