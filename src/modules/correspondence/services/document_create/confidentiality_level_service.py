import uuid
from typing import List

from fastapi import HTTPException

from src.adapters.http.user_client import User
from src.modules.correspondence.domain.enums.confidential_type import (
    DocumentConfidentialTypeEnum,
)
from src.modules.correspondence.domain.models import DocumentConfidential


class DocumentConfidentialityLevelService:

    def __init__(self, user: User):
        self.user = user

    def validate_user_role(self, confidentiality_level: DocumentConfidentialTypeEnum):
        if confidentiality_level.value.replace("ROLE_", "") in self.user.roles:
            return True
        raise HTTPException(
            status_code=403,
            detail="Вы не можете создавать документы с таким уровнем конфиденциальности!",
        )

    def execute(
        self,
        confidentiality_level: List[DocumentConfidentialTypeEnum],
        document_id: uuid.UUID,
    ) -> List[DocumentConfidential]:
        levels: List[DocumentConfidential] = []

        for level in confidentiality_level:
            if self.validate_user_role(level):
                levels.append(
                    DocumentConfidential(
                        document_id=document_id,
                        confidential=level,
                    )
                )
        return levels
