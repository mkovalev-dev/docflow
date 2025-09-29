import uuid
from datetime import datetime
from typing import Optional

from src.modules.documents.models import DocumentRegistration


class RegistrationService:
    """Сервис по регистрации"""

    @staticmethod
    def initialize_registration_row(
        document_id: uuid.UUID,
        external_number: Optional[str] = None,
        external_registration_at: Optional[datetime] = None,
    ) -> DocumentRegistration:
        # TODO:Добавить проверку на существование уже регистрации
        return DocumentRegistration(
            document_id=document_id,
            external_registration_number=external_number,
            external_registration_at=external_registration_at,
        )
