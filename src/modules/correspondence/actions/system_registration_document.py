from datetime import datetime
from typing import Optional

from src.modules.correspondence.domain.enums.document_type import DocumentTypeEnum
import secrets


class SystemRegistrationDocumentAction:
    """Генерирует системный номер документа"""

    MAX_RETRIES = 5

    def _generate_system_number(
        self, document_type: DocumentTypeEnum, version: Optional[int] = 1
    ) -> str:
        prefix = document_type.name[:3]
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        ver = f"-V{version}" if version > 1 else ""

        random_part = secrets.token_hex(4).upper()

        return f"{prefix}-{year}/{month:02d}/{day:02d}-{random_part}{ver}"

    def execute(
        self, document_type: DocumentTypeEnum, version: Optional[int] = 1
    ) -> str:
        return self._generate_system_number(document_type, version)
