from fastapi import HTTPException
from sqlalchemy import select, Integer, func, cast

from src.common.actions.base import BaseDocumentAction
from src.common.enum.user_roles import UserRolesEnum
from src.modules.documents.enums import DocumentTypeEnum, DocumentConfidentialTypeEnum
from src.modules.documents.models import DocumentRegistration
from src.modules.registration.models import RegistrationNumber


class DocumentRegistrationAction(BaseDocumentAction):
    """Действие по регистрации документа"""

    async def check_permissions(self):
        if UserRolesEnum.ROLE_VSM_DOCFLOW_REGISTRATOR not in self.user.roles:
            raise HTTPException(
                status_code=403, detail="Недостаточно прав для регистрации документа"
            )

    def get_prefix(self):
        """
        Возвращает префикс для регистрационного номера на основе типа документа.
        """
        if self.document.document_type == DocumentTypeEnum.INCOMING.value:
            return "ВХ"
        elif self.document.document_type == DocumentTypeEnum.OUTGOING.value:
            return "ИСХ-ВСМ"
        elif self.document.document_type == DocumentTypeEnum.ASSIGNMENT.value:
            return "ПОР"
        else:
            return ""

    def get_postfix(self):
        postfix_map = {
            DocumentConfidentialTypeEnum.DOCUMENT_PRIVACY_LEVEL_CONFIDENTIAL: "-К",
            DocumentConfidentialTypeEnum.DOCUMENT_PRIVACY_LEVEL_COMMERCIAL_SECRET: "-КТ",
            DocumentConfidentialTypeEnum.DOCUMENT_PRIVACY_LEVEL_PERSONAL_DATA: "-ПД",
            DocumentConfidentialTypeEnum.DOCUMENT_PRIVACY_LEVEL_OFFICIAL_USE_ONLY: "-ДСП",
        }

        for level in self.document.confidentials:
            postfix = postfix_map.get(level.confidential)
            if postfix:
                return postfix

        return ""

    async def get_next_number_by_prefix(self) -> str:
        # Запрос на максимальный номер, преобразованный в int
        stmt = select(func.max(cast(RegistrationNumber.number, Integer))).where(
            RegistrationNumber.prefix == self.get_prefix()
        )
        result = await self.db.execute(stmt)
        max_number = result.scalar() or 0
        next_number = max_number + 1
        # Формируем строку с ведущими нулями
        next_number_str = str(next_number).zfill(6)
        return next_number_str

    async def generate_registration_number(self) -> RegistrationNumber:
        """
        - prefix (str): Префикс номера
        - number (int): Порядковый номер
        - postfix (str): Постфикс номера
        """
        return RegistrationNumber(
            prefix=self.get_prefix(),
            number=await self.get_next_number_by_prefix(),
            postfix=self.get_postfix(),
            registrator=self.user.id,
        )

    async def run(self):
        stmt = select(DocumentRegistration).where(
            DocumentRegistration.document_id == self.document_id
        )
        result = await self.db.execute(stmt)
        registration_instance: DocumentRegistration = result.scalar_one_or_none()
        if registration_instance is None:
            registration_instance = DocumentRegistration(
                document_id=self.document_id,
            )

        registration_instance.registration_number = (
            await self.generate_registration_number()
        )
        self.db.add(registration_instance)
        await self.db.commit()
