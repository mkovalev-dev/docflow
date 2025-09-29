from typing import List, Optional

from fastapi import HTTPException

from src.adapters.http.user_client import User
import uuid

from src.modules.documents.enums import (
    DocumentAccessTypeEnum,
    DocumentConfidentialTypeEnum,
)
from src.modules.documents.models import DocumentAccess


class DocumentAccessService:

    def __init__(
        self,
        user: User,
        document_id: uuid.UUID,
        users_data: dict[str, User],
        confidentiality_levels: list[DocumentConfidentialTypeEnum],
    ):
        self.user = user
        self.document_id = document_id
        self.users_data = users_data
        self.confidentiality_levels = confidentiality_levels

    async def validate_user_role(
        self,
        user: User,
        levels: List[DocumentConfidentialTypeEnum],
    ) -> None:
        """
        Проверка, что пользователь обладает хотя бы одним уровнем из confidentiality_levels.
        """
        user_roles = user.roles
        required_levels = [level.value for level in levels]

        if not any(role in user_roles for role in required_levels):
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Пользователь {user.get('id')} не имеет доступа "
                    f"ни к одному из уровней конфиденциальности: {required_levels}"
                ),
            )

    async def execute(
        self,
        user_ids: Optional[List[uuid.UUID]] = None,
    ) -> List[DocumentAccess]:
        accesses: List[DocumentAccess] = []
        if not user_ids:
            user_ids = []

        for user_id in set(user_ids):
            user = self.users_data.get(str(user_id), None)
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Пользователь с ID {user_id} не найден.",
                )

            await self.validate_user_role(user=user, levels=self.confidentiality_levels)

            accesses.append(
                DocumentAccess(
                    document_id=self.document_id,
                    user_id=user_id,
                    access_type=DocumentAccessTypeEnum.READONLY,
                )
            )

        return accesses
