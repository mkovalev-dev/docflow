from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.http.user_client import User
import uuid
from fastapi import Request, HTTPException

from src.modules.documents.models import Document


class BaseDocumentAction(ABC):
    def __init__(
        self,
        user: User,
        document_id: uuid.UUID,
        db: AsyncSession,
        request: Optional[Request] = None,
    ):
        self.user = user
        self.document_id = document_id
        self.db = db
        self.request = request

        self.document: Optional[Document] = None

    async def execute(self):
        """
        Шаблонный метод:
        1. Загружает документ
        2. Проверяет права
        3. Выполняет действие (run)
        """
        await self.load_document()
        await self.check_permissions()
        return await self.run()

    async def load_document(self):
        from src.modules.documents.models import Document

        result = await self.db.get(Document, self.document_id)
        if not result:
            raise HTTPException(status_code=404, detail="Документ не найден")
        self.document = result

    @abstractmethod
    async def check_permissions(self):
        """
        Должен быть переопределён в подклассе.
        Проверяет, имеет ли пользователь право выполнять действие.
        """
        raise NotImplementedError

    @abstractmethod
    async def run(self):
        """
        Должен быть переопределён в подклассе.
        Реализует само действие (регистрация, удаление и т.д.).
        """
        raise NotImplementedError
