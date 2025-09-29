import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.adapters.http.user_client import User
from src.common.utils import initials_fi_no_dots
from src.modules.documents.enums import DocumentTypeEnum
from src.modules.documents.models import Document


class DocumentCreateData(BaseModel):
    content: str
    paper_count: int
    attachment_description: Optional[str] = None
    deadline: Optional[datetime] = None


class DocumentCreateService:
    """Сервис по созданию нового документа"""

    def _generate_system_number(
        self, document_type: DocumentTypeEnum, user: User, version: Optional[int] = 1
    ):
        prefix = document_type.name[:3]
        year = datetime.now().year
        ver = f"-V{version}"
        postfix = initials_fi_no_dots(user.full_name)
        seq = str(uuid.uuid4().hex[:8]).upper()

        return f"{prefix}-{year}-{postfix}-{seq}{ver if version > 1 else ''}"

    def execute(
        self,
        id: uuid.UUID,
        document_type: DocumentTypeEnum,
        user: User,
        data: DocumentCreateData,
    ) -> Document:
        return Document(
            id=id,
            system_number=self._generate_system_number(document_type, user),
            content=data.content,
            paper_count=data.paper_count,
            attachment_description=data.attachment_description,
            creator_id=user.id,
            deadline=data.deadline,
        )
