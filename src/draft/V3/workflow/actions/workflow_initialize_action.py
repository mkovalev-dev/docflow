from typing import List, Optional

from fastapi import Request
from pydantic import BaseModel

from src.adapters.http.user_client import UserClient
from src.common.enum.user_roles import UserRolesEnum
from src.modules.documents.enums import DocumentTypeEnum
from src.modules.documents.schemas.base import DocumentAddressCreateModel

from src.modules.workflow.enums import StepTypeEnum
from src.modules.workflow.models import Workflow, WorkflowStep, WorkflowParticipant
import uuid


class WorkflowSchema(BaseModel):
    step_type: StepTypeEnum
    users: List[uuid.UUID]


class WorkflowInitializeAction:
    """Экшен для инициализации нового маршрута у документа"""

    def __init__(
        self,
        document_id: uuid.UUID,
        document_type: DocumentTypeEnum,
        request: Request,
        recipients: List[DocumentAddressCreateModel],
        workflow_data: Optional[List[WorkflowSchema]],
    ):
        self.workflow_id = uuid.uuid4()
        self.document_id = document_id
        self.document_type = document_type
        self.request = request
        self.recipients = recipients
        self.workflow_data = workflow_data or []

    async def execute(self) -> Workflow:
        workflow = Workflow(id=self.workflow_id, document_id=self.document_id)
        steps = await self._build_steps()
        workflow.steps = steps
        return workflow

    async def _get_registration_users(self) -> List[uuid.UUID]:
        user_client = UserClient(
            session_id=self.request.cookies.get("SESSION"),
        )
        registrators = await user_client.get_user_ids_from_role(
            UserRolesEnum.ROLE_VSM_DOCFLOW_REGISTRATOR
        )
        return registrators

    async def _build_registration_step(self, order: int) -> WorkflowStep:
        registrators = await self._get_registration_users()
        registration_step = WorkflowStep(
            workflow_id=self.workflow_id,
            step_type=StepTypeEnum.REGISTRATION,
            order=order,
            participants=[WorkflowParticipant(user_id=r) for r in registrators],
        )
        return registration_step

    async def _build_incoming_steps(self):
        """Сборка шагов для Входящих документов"""
        steps = []
        if self.document_type == DocumentTypeEnum.INCOMING:
            registration_step = await self._build_registration_step(order=1)
            execution_step = WorkflowStep(
                workflow_id=self.workflow_id,
                step_type=StepTypeEnum.DECISION,
                order=2,
                participants=[
                    WorkflowParticipant(
                        user_id=recipient.user_id,
                    )
                    for recipient in self.recipients
                ],
            )
            steps.append(registration_step)
            steps.append(execution_step)

        return steps

    async def _build_steps(self) -> List[WorkflowStep]:
        method_name = f"_build_{self.document_type.value.lower()}_steps"
        builder = getattr(self, method_name, self._build_default)
        return await builder()

    async def _build_default(self) -> List[WorkflowStep]:
        """Используем шаги с фронта или ничего не делаем"""
        return await self._steps_from_workflow_data()

    async def _steps_from_workflow_data(self) -> List[WorkflowStep]:
        steps = []
        for idx, step_schema in enumerate(self.workflow_data, start=1):
            steps.append(
                WorkflowStep(
                    step_type=step_schema.step_type,
                    order=idx,
                    participants=[
                        WorkflowParticipant(
                            user_id=user_id,
                        )
                        for user_id in step_schema.users
                    ],
                )
            )
        return steps

    async def _build_assignment_steps(self):
        steps = []
        if self.document_type == DocumentTypeEnum.ASSIGNMENT:
            for idx, step_schema in enumerate(self.recipients, start=1):
                steps.append(
                    WorkflowStep(
                        step_type=StepTypeEnum.EXECUTION,
                        order=idx,
                        participants=[
                            WorkflowParticipant(
                                user_id=step_schema.user_id,
                                comment=step_schema.comment,
                                is_responsible=step_schema.is_responsible,
                            )
                        ],
                    )
                )
