from typing import List

from fastapi import HTTPException, Request

from src.adapters.http.user_client import User, UserClient
import uuid

from src.modules.documents.enums import (
    DocumentAccessTypeEnum,
    DocumentConfidentialTypeEnum,
)
from src.modules.documents.models import DocumentAccess


class DocumentAccessService:

    def __init__(self, user: User, document_id: uuid.UUID, request: Request):
        self.user = user
        self.document_id = document_id
        self.request = request

    async def get_users_data(self, user_ids: List[uuid.UUID]):
        user_client = UserClient(
            session_id=self.request.cookies.get("SESSION"),
        )
        return await user_client.get_users(ids=user_ids)

    async def validate_user_role(
        self,
        user: User,
        levels: List[DocumentConfidentialTypeEnum],
    ) -> None:
        """
        Проверка, что пользователь обладает хотя бы одним уровнем из confidentiality_levels.
        """
        user_roles = user.get("roles", [])
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
        user_ids: List[uuid.UUID],
        confidentiality_levels: list[DocumentConfidentialTypeEnum],
    ) -> List[DocumentAccess]:
        accesses: List[DocumentAccess] = []
        users_data = await self.get_users_data(user_ids)

        for user_id in user_ids:
            user = users_data.get(str(user_id), None)
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Пользователь с ID {user_id} не найден.",
                )

            await self.validate_user_role(user=user, levels=confidentiality_levels)

            accesses.append(
                DocumentAccess(
                    document_id=self.document_id,
                    user_id=user_id,
                    access_type=DocumentAccessTypeEnum.READONLY,
                )
            )

        return accesses
