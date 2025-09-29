import uuid
from typing import List

from fastapi import HTTPException

from src.adapters.http.user_client import User
from src.modules.documents.enums import DocumentConfidentialTypeEnum
from src.modules.documents.models import DocumentConfidential


class DocumentConfidentialityLevelService:

    def __init__(self, user: User, document_id: uuid.UUID):
        self.user = user
        self.document_id = document_id

    def validate_user_role(self, confidentiality_level: DocumentConfidentialTypeEnum):
        if confidentiality_level.value in self.user.roles:
            return True
        raise HTTPException(
            status_code=403,
            detail="Вы не можете создавать документы с таким уровнем конфиденциальности!",
        )

    def execute(
        self, confidentiality_level: List[DocumentConfidentialTypeEnum]
    ) -> List[DocumentConfidential]:
        levels: List[DocumentConfidential] = []
        for level in confidentiality_level:
            if self.validate_user_role(level):
                levels.append(
                    DocumentConfidential(
                        document_id=self.document_id,
                        confidential=level,
                    )
                )
        return levels
