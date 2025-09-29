import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import ConfigDict, BaseModel, model_validator, Field
from pydantic_core.core_schema import ValidationInfo

from src.adapters.http.user_client import User
from src.modules.documents.enums import (
    DocumentPartyTypeEnum,
    DocumentConfidentialTypeEnum,
)
from src.modules.documents.schemas.base import DocTypeLabel
from src.modules.documents.schemas.document_address import AddressGroups
from src.modules.registration.schemas.registration_response import RegistrationModel
from src.modules.workflow.enums import StatusEnum


class DocumentFileItem(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    size: int
    extension: str
    type: str
    is_main: bool

    @model_validator(mode="before")
    def set_type_from_extension(self):
        self.type = self.extension
        return self


class DocumentListItem(BaseModel):
    id: uuid.UUID
    document_type: DocTypeLabel
    registration: RegistrationModel
    sender: AddressGroups
    recipient: AddressGroups
    content: str
    created_at: datetime
    creator: Optional[User]
    paper_count: int
    attachment_count: Optional[str] = None
    deadline: Optional[datetime] = None
    actions: dict[str, bool] | None = None
    confidentiality_level: List[DocumentConfidentialTypeEnum]
    main_file: Optional[DocumentFileItem] = None
    file_list: List[DocumentFileItem] = Field(default_factory=list)
    status: Optional[StatusEnum] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def _split_parties(cls, parties) -> tuple[list, list]:
        """Разделяет адресатов на отправителей и получателей."""
        senders = []
        recipients = []

        for p in parties or []:
            pt = getattr(p, "party_type", None)
            val = getattr(pt, "value", getattr(pt, "name", pt))
            (
                senders if val == DocumentPartyTypeEnum.SENDER.value else recipients
            ).append(p)

        return senders, recipients

    @classmethod
    def _prepare_files(
        cls, files: list
    ) -> tuple[Optional[DocumentFileItem], List[DocumentFileItem]]:
        """Определяет главный файл и список остальных файлов."""
        files = files or []
        main = next((f for f in files if f.is_main), None)
        others = [f for f in files if not f.is_main]

        return (
            (
                DocumentFileItem.model_validate(main, from_attributes=True)
                if main
                else None
            ),
            [DocumentFileItem.model_validate(f, from_attributes=True) for f in others],
        )

    @classmethod
    def _get_creator(cls, creator_id, context: dict) -> Optional[User]:
        return context.get("users", {}).get(str(creator_id))

    @model_validator(mode="before")
    @classmethod
    def from_orm_model(cls, v, info: ValidationInfo):
        if isinstance(v, dict):
            return v

        # Адресаты
        senders, recipients = cls._split_parties(getattr(v, "address_parties", []))

        # Пользователь
        creator = cls._get_creator(getattr(v, "creator_id", None), info.context or {})

        # Файлы
        main_file, file_list = cls._prepare_files(getattr(v, "files", []))

        # Конфиденциальность
        confidentials = [c.confidential for c in getattr(v, "confidentials", [])]

        # Статичные действия (в будущем можно передавать через context)
        actions = {
            "approve": True,
            "originality": True,
            "registration": True,
            "reject": True,
            "revision": True,
            "revoke": True,
            "sign": True,
            "registration_edit": True,
            "assignment": True,
        }

        return {
            "id": v.id,
            "document_type": getattr(v, "document_type"),
            "registration": getattr(v, "registration"),
            "sender": senders,
            "recipient": recipients,
            "content": v.content,
            "created_at": v.created_at,
            "creator": creator,
            "paper_count": v.paper_count,
            "attachment_count": getattr(v, "attachment_description", None),
            "deadline": getattr(v, "deadline", None),
            "confidentiality_level": confidentials,
            "main_file": main_file,
            "file_list": file_list,
            "status": getattr(v, "document_status", None),
            "actions": actions,
        }
