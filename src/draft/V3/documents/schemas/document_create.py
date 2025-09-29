import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator, TypeAdapter

from src.modules.documents.enums import DocumentConfidentialTypeEnum
from src.modules.documents.schemas.document_recipient import NormalizedRecipients
from src.modules.documents.schemas.document_sender import NormalizedSender
from src.modules.workflow.actions.workflow_initialize_action import WorkflowSchema


class ExternalRegistrationSchema(BaseModel):
    """Модель для внешней регистрации документа"""

    external_number: str
    external_registration_at: datetime


class DocumentCreateSchema(BaseModel):
    """Модель для создания нового документа"""

    content: str
    paper_count: int = 0
    attachment_description: str | None = Field(alias="attachment_count", default=None)
    access: List[uuid.UUID] | None = Field(alias="white_list", default=[])
    deadline: Optional[datetime] = None

    confidentiality_level: List[DocumentConfidentialTypeEnum] = []
    external_registration: ExternalRegistrationSchema | None = None

    sender: Optional[NormalizedSender] = None
    recipients: NormalizedRecipients

    workflow: Optional[List[WorkflowSchema]] = []

    main_file: Optional[UploadFile] = Field(alias="main_file", default=None)
    file_list: Optional[List[UploadFile]] = Field(alias="file_list", default=[])

    answer_to: Optional[List[uuid.UUID]] = Field(alias="answer_to", default=[])
    related_document: Optional[List[uuid.UUID]] = Field(
        alias="related_document", default=[]
    )

    @field_validator("external_registration", mode="before")
    @classmethod
    def validate_external_registration(cls, v):
        adapter = TypeAdapter(ExternalRegistrationSchema)
        return adapter.validate_json(v)

    @field_validator("workflow", mode="before")
    @classmethod
    def validate_workflow(cls, v):
        adapter = TypeAdapter(List[WorkflowSchema])
        if len(v) > 0:
            return adapter.validate_json(v[0])
        return []
